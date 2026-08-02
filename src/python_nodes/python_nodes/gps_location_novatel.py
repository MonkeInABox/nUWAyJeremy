#! /usr/bin/env python3

import rclpy

from geometry_msgs.msg import TransformStamped
from rclpy.node import Node
from tf2_ros.transform_broadcaster import TransformBroadcaster
# from nav_msgs.msg import Odometry
from sbg_driver.msg import SbgEkfEuler, SbgGpsPos, SbgGpsHdt
from tf_transformations import quaternion_from_euler
from nav_msgs.msg import Odometry

class DynamicBroadcaster(Node):

    def __init__(self):
        super().__init__('dynamic_broadcaster')
        self.tfb_ = TransformBroadcaster(self)
        self.sub_pos = self.create_subscription(Odometry, "/odometry/global", self.update_position, 1)
        self.sub_orient = self.create_subscription(SbgGpsHdt, "/sbg/gps_hdt", self.update_orientation, 1)
        self.currentOX = 0.0
        self.currentOY = 0.0
        self.currentOZ = 0.0
        self.currentOW = 0.0
        self.currentX = 0.0
        self.currentY = 0.0
        

    def update_position(self, msg):
        
        tfs = TransformStamped()
        tfs.header.stamp = self.get_clock().now().to_msg()
        tfs.header.frame_id = "map"
        tfs._child_frame_id = "base_link"
        tfs.transform.translation.x = msg.pose.pose.position.x
        tfs.transform.translation.y = msg.pose.pose.position.y
        tfs.transform.translation.z = 0.0 

        tfs.transform.rotation.x = self.currentOX
        tfs.transform.rotation.y = self.currentOY
        tfs.transform.rotation.z = self.currentOZ
        tfs.transform.rotation.w = self.currentOW

        self.currentX = msg.pose.pose.position.x
        self.currentY = msg.pose.pose.position.y

        self.tfb_.sendTransform(tfs)

    def update_orientation(self, msg):

        tfs = TransformStamped()
        tfs.header.stamp = self.get_clock().now().to_msg()
        tfs.header.frame_id = "map"
        tfs._child_frame_id = "base_link"

        tfs.transform.translation.x = self.currentX
        tfs.transform.translation.y = self.currentY
        tfs.transform.translation.z = 0.0

        roll = 0.0
        pitch = 0.0
        yaw = (msg.true_heading * 3.14) / 180

        quat = quaternion_from_euler(roll, pitch, yaw)

        tfs.transform.rotation.x = quat[0]
        tfs.transform.rotation.y = quat[1]
        tfs.transform.rotation.z = quat[2]
        tfs.transform.rotation.w = quat[3]
        
        self.currentOX = quat[0]
        self.currentOY = quat[1]
        self.currentOZ = quat[2]
        self.currentOW = quat[3]

        self.tfb_.sendTransform(tfs)

    currentX = 0.0
    currentY = 0.0
    currentOX = 0.0
    currentOY = 0.0
    currentOZ = 0.0
    currentOW = 0.0

def main():
    rclpy.init()
    node = DynamicBroadcaster()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()