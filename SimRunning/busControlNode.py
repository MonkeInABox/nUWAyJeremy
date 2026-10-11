#!/usr/bin/env python3
"""
Jeremy Butson, adapting (https://github.com/szacho/pointcam) to the University of Western Australia REV Project nUWAy shuttle driving
Uses Autoware packages
"""
import numpy as np
import torch

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.executors import MultiThreadedExecutor

from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2
from numpy.lib.recfunctions import structured_to_unstructured

import message_filters

from autoware_control_msgs.msg import Control
from autoware_vehicle_msgs.msg import ControlModeReport

from driveModel import drivePointCAM, fps_downsample


# Transforms, same as in model training
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

# limits to attempt to remove errors
x_max = 20
x_min = -20
y_limit = 20
z_limit = 30

# padding same as model, same as the numher of points
PADDING = 4300
NPOINTS = 3072

MAX_ABS_SPEED = 5.5
MAX_ABS_STEER = 0.32

# mode numbers to match the Autoware numbers on nUWAy 4 whilst in autonomous mode (manual is driving with PS5 controller)
AUTONOMOUS_MODE = 1
MANUAL_MODE = 4


def preprocess_cloud(msg: PointCloud2, transformation_matrix: np.ndarray) -> np.ndarray:
    """Transforms and checks pointcloud

    Args:
        msg (PointCloud2): input cloud
        transformation_matrix (np.ndarray): transform matrix defined above

    Returns:
        np.ndarray: the converted pointcloud
    """
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


class BusControlNode(Node):
    def __init__(self):
        """initialises parameters
        """
        super().__init__("bus_control_node")

        self.declare_parameter("front_lidar_topic", "/lidar_localisation/front/cloud") #front point cloud topic name
        self.declare_parameter("rear_lidar_topic", "/lidar_localisation/rear/cloud") # rear point cloud topic name
        self.declare_parameter("checkpoint_path", "/checkpoints/pointcam_shuttle_lane_following.pth") # path hto checkpoint of model being tested
        self.declare_parameter("n_patches", 64) # match the model
        self.declare_parameter("points_per_patch", 32) # match the model
        self.declare_parameter("sync_slop_sec", 0.1) 
        self.declare_parameter("stall_threshold_sec", 0.3) 
        self.declare_parameter("bench_mode", True) # to run on bus make False

        front_topic = self.get_parameter("front_lidar_topic").value
        rear_topic = self.get_parameter("rear_lidar_topic").value
        checkpoint_path = self.get_parameter("checkpoint_path").value
        n_patches = self.get_parameter("n_patches").value
        points_per_patch = self.get_parameter("points_per_patch").value
        sync_slop = self.get_parameter("sync_slop_sec").value
        self.stall_threshold_sec = self.get_parameter("stall_threshold_sec").value
        self.bench_mode = self.get_parameter("bench_mode").value

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
        state = torch.load(checkpoint_path, map_location=self.device, weights_only=True)
        if isinstance(state, dict) and "model_state_dict" in state:
            state = state["model_state_dict"]

        # getting rid of pretrain values for running 
        state = {k: v for k, v in state.items() if "masknet" not in k}
        
        missing, unexpected = self.model.load_state_dict(state, strict=False)
        self.get_logger().info(f"Loaded checkpoint state_dict (ignored {len(missing)} pretraining keys).")
        
        self.model.to(self.device)
        self.model.eval()

        if self.bench_mode:
            control_cmd_topic = "/control/command/control_cmd_bench"
            self.get_logger().warn(
                f"BENCH MODE: publishing to '{control_cmd_topic}', NOT the real "
                f"control_cmd topic. This cannot drive the bus. Pass "
                f"-p bench_mode:=false only after completing the deployment "
                f"sheet's full pre-drive checklist."
            )
        else:
            control_cmd_topic = "/control/command/control_cmd"
            self.get_logger().warn(
                f"LIVE MODE: publishing to the REAL '{control_cmd_topic}' topic. "
                f"This WILL drive the bus while autonomous mode is engaged."
            )
        self.control_pub = self.create_publisher(Control, control_cmd_topic, 10)

        self.inference_callback_group = MutuallyExclusiveCallbackGroup()
        self.mode_callback_group = MutuallyExclusiveCallbackGroup()

        self._control_mode = MANUAL_MODE

        mode_qos = QoSProfile(depth=1, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.mode_sub = self.create_subscription(
            ControlModeReport, "/vehicle/status/control_mode", self.mode_callback,
            mode_qos, callback_group=self.mode_callback_group,
        )

        sensor_qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.front_sub = message_filters.Subscriber(
            self, PointCloud2, front_topic, qos_profile=sensor_qos,
        )
        self.rear_sub = message_filters.Subscriber(
            self, PointCloud2, rear_topic, qos_profile=sensor_qos,
        )
        self.time_sync = message_filters.ApproximateTimeSynchronizer(
            [self.front_sub, self.rear_sub], queue_size=10, slop=sync_slop
        )
        self.time_sync.registerCallback(self.lidar_callback)

        self._last_front_stamp = None
        self._last_lidar_time = self.get_clock().now()
        self.watchdog_timer = self.create_timer(
            0.1, self.watchdog_callback, callback_group=self.inference_callback_group
        )

        self.get_logger().info(
            f"Subscribed to front='{front_topic}', rear='{rear_topic}', "
            f"mode='/vehicle/status/control_mode', publishing to '{control_cmd_topic}'"
        )

    def mode_callback(self, msg: ControlModeReport):
        """callback for checking what mdoe the bus is in

        Args:
            msg (ControlModeReport): _description_
        """
        new_mode = msg.mode
        if self._control_mode == AUTONOMOUS_MODE and new_mode != AUTONOMOUS_MODE:
            self._publish_control(0.0, 0.0)
            self.get_logger().info(f"Left autonomous mode (now mode={new_mode}) -- sent one zero command.")
        self._control_mode = new_mode

    def watchdog_callback(self):
        """callback to check whether over the stall threshold time has occurred since last message
        """
        elapsed = (self.get_clock().now() - self._last_lidar_time).nanoseconds / 1e9
        if elapsed > self.stall_threshold_sec:
            if self.bench_mode or self._control_mode == AUTONOMOUS_MODE:
                self.get_logger().warn(
                    f"No LiDAR frame in {elapsed:.2f}s -- publishing zero.",
                    throttle_duration_sec=1.0,
                )
                # self._publish_control(0.0, 0.0)

    def lidar_callback(self, front_msg: PointCloud2, rear_msg: PointCloud2):
        """callback for getting LiDAR data

        Args:
            front_msg (PointCloud2): front point cloud
            rear_msg (PointCloud2): rear point cloud
        """
        self._last_lidar_time = self.get_clock().now()

        stamp_key = (front_msg.header.stamp.sec, front_msg.header.stamp.nanosec)
        if stamp_key == self._last_front_stamp:
            self.get_logger().warn("Front LiDAR frame repeated -- publishing stop.", throttle_duration_sec=2.0)
            self._publish_control_gated(0.0, 0.0)
            return
        self._last_front_stamp = stamp_key

        try:
            front_points = preprocess_cloud(front_msg, front_LiDAR_transformation_matrix)
            rear_points = preprocess_cloud(rear_msg, rear_LiDAR_transformation_matrix)
        except Exception as e:
            self.get_logger().error(f"LiDAR preprocessing failed: {e}")
            self._publish_control_gated(0.0, 0.0)
            return

        front_tensor = torch.from_numpy(front_points).unsqueeze(0).to(self.device)
        rear_tensor = torch.from_numpy(rear_points).unsqueeze(0).to(self.device)

        with torch.no_grad():
            front_tensor = fps_downsample(front_tensor, PADDING, NPOINTS)
            rear_tensor = fps_downsample(rear_tensor, PADDING, NPOINTS)
            speed, steering_angle = self.model(front_tensor, rear_tensor)

        speed = float(speed.item() / 8.0)

        steering_angle = float(steering_angle.item()) # add OFFSET if needed

        if abs(speed) > MAX_ABS_SPEED or abs(steering_angle) > MAX_ABS_STEER:
            self.get_logger().warn(
                f"Model output out of expected range (speed={speed:.3f}, steer={steering_angle:.3f}) -- publishing stop."
            )
            self._publish_control_gated(0.0, 0.0)
            return

        self._publish_control_gated(speed, steering_angle)

    def _publish_control_gated(self, speed: float, steering_angle: float):
        """publish only in auto mode

        Args:
            speed (float): speed to publish
            steering_angle (float): steering to publish
        """
        if not self.bench_mode and self._control_mode != AUTONOMOUS_MODE:
            return
        self._publish_control(speed, steering_angle)

    def _publish_control(self, speed: float, steering_angle: float):
        """publishes

        Args:
            speed (float): speed to publish
            steering_angle (float): steering to publish
        """
        ctl = Control()
        ctl.stamp = self.get_clock().now().to_msg()
        ctl.longitudinal.velocity = float(speed)
        ctl.lateral.steering_tire_angle = float(steering_angle)
        self.control_pub.publish(ctl)

    def publish_shutdown_zero(self):
        """sens zero once shutdown
        """
        ctl = Control()
        ctl.stamp = self.get_clock().now().to_msg()
        ctl.longitudinal.velocity = 0.0
        ctl.lateral.steering_tire_angle = 0.0
        self.control_pub.publish(ctl)
        self.get_logger().info("Published shutdown zero command.")


def main(args=None):
    rclpy.init(args=args)
    node = BusControlNode()
    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        node.get_logger().info("Stopped by user.")
    finally:
        node.publish_shutdown_zero()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
