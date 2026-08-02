#! /usr/bin/env python3

import rclpy

from geometry_msgs.msg import TransformStamped
from rclpy.node import Node
from tf2_ros.transform_broadcaster import TransformBroadcaster
from nav_msgs.msg import Odometry

class DynamicBroadcaster(Node):

    def __init__(self):
        super().__init__('dynamic_broadcaster')
        self.tfb_ = TransformBroadcaster(self)
        self.sub_pose = self.create_subscription(Odometry, "/odometry/global", self.update_position, 10)

    def update_position(self, msg):
        
        tfs = TransformStamped()
        tfs.header.stamp = self.get_clock().now().to_msg()
        tfs.header.frame_id = "map"
        tfs._child_frame_id = "base_link"
        tfs.transform.translation.x = msg.pose.pose.position.x
        tfs.transform.translation.y = msg.pose.pose.position.y
        tfs.transform.translation.z = 0.0  

        tfs.transform.rotation.x = msg.pose.pose.orientation.x
        tfs.transform.rotation.y = msg.pose.pose.orientation.y
        tfs.transform.rotation.z = msg.pose.pose.orientation.z
        tfs.transform.rotation.w = msg.pose.pose.orientation.w

        self.tfb_.sendTransform(tfs)    

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