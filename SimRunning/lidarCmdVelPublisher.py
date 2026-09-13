#!/usr/bin/env python3
"""
Node that subscribes to the front/rear LiDAR PointCloud2 topics, runs
them through the trained PointCAM shuttle-bus model, and publishes the
predicted speed/steering as a cmd_vel Twist


Inference model - LiDAR transform > crop > padding > FPS 
"""

import numpy as np
import torch

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy

from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2
from numpy.lib.recfunctions import structured_to_unstructured
from geometry_msgs.msg import Twist, TwistStamped

import message_filters

from driveModel import drivePointCAM, fps_downsample


# Same LiDAR extrinsics / crop bounds / padding used in shuttleBusTrainCAM
rear_LiDAR_transformation_matrix = np.array([
    [np.cos(np.deg2rad(8)), 0, np.sin(np.deg2rad(8)), 1.689],
    [0, 1, 0, 0],
    [-np.sin(np.deg2rad(8)), 0, np.cos(np.deg2rad(8)), 0.9],
    [0, 0, 0, 1]]
    )
front_LiDAR_transformation_matrix = np.array([
    [-np.cos(np.deg2rad(8)), 0, -np.sin(np.deg2rad(8)), -1.689],
    [0, -1, 0, 0],
    [-np.sin(np.deg2rad(8)), 0, np.cos(np.deg2rad(8)), 0.9],
    [0, 0, 0, 1]
])

x_max = 20
x_min = -20
y_limit = 20
z_limit = 30

PADDING = 4300       # fixed point count the model's inputs are padded/cropped to
NPOINTS = 3072       # FPS-downsampled point count fed to the model (matches training)


MAX_ABS_SPEED = 5.5
MAX_ABS_STEER = 0.32


def preprocess_cloud(msg: PointCloud2, transformation_matrix: np.ndarray) -> np.ndarray:
    points = structured_to_unstructured(
        point_cloud2.read_points(msg, field_names=("x", "y", "z", "intensity"), skip_nans=True)
    )
    points = np.delete(points, -1, axis=1)  

    ones = np.ones((points.shape[0], 1))
    points_h = np.hstack([points, ones]) 
    points_h = (transformation_matrix @ points_h.T).T 

    px, py, pz = points_h[:, 0], points_h[:, 1], points_h[:, 2]
    mask = (px > x_min) & (px < x_max) & (np.abs(py) < y_limit) & (pz < z_limit)
    cropped = points_h[mask, :3]  

    if len(cropped) > PADDING:
        indices = np.random.choice(len(cropped), PADDING, replace=False)
        cropped = cropped[indices]

    if len(cropped) < PADDING:
        filler = np.zeros((PADDING - len(cropped), 3), dtype=cropped.dtype)
        cropped = np.vstack([cropped, filler])

    return cropped.astype(np.float32)


class LidarCmdVelPublisher(Node):
    def __init__(self):
        super().__init__("lidar_cmd_vel_publisher")

        # ROS2 Topic dexcs
        self.declare_parameter("front_lidar_topic", "/lidar_localisation/front/cloud")
        self.declare_parameter("rear_lidar_topic", "/lidar_localisation/rear/cloud")
        self.declare_parameter("cmd_vel_topic", "/cmd_vel")
        self.declare_parameter("checkpoint_path", "/workspace/drive_ws/models/pointcam_shuttle_lane_following.pth")
        self.declare_parameter("n_patches", 64)
        self.declare_parameter("points_per_patch", 32)
        self.declare_parameter("sync_slop_sec", 0.1)  

        front_topic = self.get_parameter("front_lidar_topic").value
        rear_topic = self.get_parameter("rear_lidar_topic").value
        cmd_vel_topic = self.get_parameter("cmd_vel_topic").value
        checkpoint_path = self.get_parameter("checkpoint_path").value
        n_patches = self.get_parameter("n_patches").value
        points_per_patch = self.get_parameter("points_per_patch").value
        sync_slop = self.get_parameter("sync_slop_sec").value

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.get_logger().info(f"Loading model on {self.device} from {checkpoint_path}")


        self.model = drivePointCAM(
            checkpoint_path=None,
            n_patches=n_patches,
            points_per_patch=points_per_patch,
            freeze_encoder=False,
            drop_path_rate=0.0,
        )

        state = torch.load(checkpoint_path, map_location=self.device, weights_only=True)

        if isinstance(state, dict) and "model_state_dict" in state:
            state = state["model_state_dict"]
        self.model.load_state_dict(state)
        self.model.to(self.device)
        self.model.eval()

        # PUBLISHER AND SUBSCRIBER GEN 
        self.cmd_vel_pub = self.create_publisher(Twist, cmd_vel_topic, 10)
        self.cmd_vel_stamped_pub = self.create_publisher(TwistStamped, cmd_vel_topic + "_stamped", 10)

        sensor_qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.front_sub = message_filters.Subscriber(self, PointCloud2, front_topic, qos_profile=sensor_qos)
        self.rear_sub = message_filters.Subscriber(self, PointCloud2, rear_topic, qos_profile=sensor_qos)

        self.time_sync = message_filters.ApproximateTimeSynchronizer(
            [self.front_sub, self.rear_sub], queue_size=10, slop=sync_slop
        )
        self.time_sync.registerCallback(self.lidar_callback)

        self._last_front_stamp = None

        self.get_logger().info(
            f"Subscribed to front='{front_topic}', rear='{rear_topic}', publishing cmd_vel on '{cmd_vel_topic}'"
        )

    def lidar_callback(self, front_msg: PointCloud2, rear_msg: PointCloud2):
        stamp_key = (front_msg.header.stamp.sec, front_msg.header.stamp.nanosec)
        if stamp_key == self._last_front_stamp:
            self.get_logger().warn("Front LiDAR frame repeated -- publishing stop.", throttle_duration_sec=2.0)
            self._publish_cmd(0.0, 0.0)
            return
        self._last_front_stamp = stamp_key

        try:
            front_points = preprocess_cloud(front_msg, front_LiDAR_transformation_matrix)
            rear_points = preprocess_cloud(rear_msg, rear_LiDAR_transformation_matrix)
        except Exception as e:
            self.get_logger().error(f"LiDAR preprocessing failed: {e}")
            self._publish_cmd(0.0, 0.0)
            return

        front_tensor = torch.from_numpy(front_points).unsqueeze(0).to(self.device)  # (1, PADDING, 3)
        rear_tensor = torch.from_numpy(rear_points).unsqueeze(0).to(self.device)

        with torch.no_grad():
            front_tensor = fps_downsample(front_tensor, PADDING, NPOINTS)
            rear_tensor = fps_downsample(rear_tensor, PADDING, NPOINTS)
            speed, steering_angle = self.model(front_tensor, rear_tensor)

        speed = float(speed.item())
        steering_angle = float(steering_angle.item())

        if abs(speed) > MAX_ABS_SPEED or abs(steering_angle) > MAX_ABS_STEER:
            self.get_logger().warn(
                f"Model output out of expected range (speed={speed:.3f}, steer={steering_angle:.3f}) -- publishing stop."
            )
            self._publish_cmd(0.0, 0.0)
            return

        self._publish_cmd(speed, steering_angle)

    def _publish_cmd(self, linear_x: float, angular_z: float):
        twist = Twist()
        twist.linear.x = linear_x
        twist.angular.z = angular_z
        self.cmd_vel_pub.publish(twist)

        stamped = TwistStamped()
        stamped.header.stamp = self.get_clock().now().to_msg()
        stamped.twist = twist
        self.cmd_vel_stamped_pub.publish(stamped)


def main(args=None):
    rclpy.init(args=args)
    node = LidarCmdVelPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Node stopped by user.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
