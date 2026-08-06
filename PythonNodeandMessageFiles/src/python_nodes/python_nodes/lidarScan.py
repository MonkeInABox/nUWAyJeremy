#!/usr/bin/env python

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from python_nodes_interfaces.msg import StringMultiArrayStamped
from std_msgs.msg import Int32, Float64, Float32
from geometry_msgs.msg import Vector3Stamped
from sensor_msgs.msg import LaserScan


class lidarSpeedLimiterNode(Node):

    def __init__(self):
        super().__init__("Lidar_Speed_Limiter")

        self.speed_limit_pub = self.create_publisher(Vector3Stamped, "/lidar_speed_limit", 10)
        self.lidar_scan = self.create_subscription(
            LaserScan, "/lidar_safety/sick_lms_1xx/scan", self.SpeedLimiting, 10
        )
        self.speed_fb_sub = self.create_subscription(
            Float32, "speed_fb", self.updateSpeed, 1
        )
        self.speed_fb = 0.0
        self.max_vel = 5.8
        self.right_vel = 5.8
        self.left_vel = 5.8

    def updateSpeed(self, msg):
        self.speed_fb = msg.data
        return

    def SpeedLimiting(self, msg):
        new_vel = Float64()

        if (msg.header.frame_id == "lidar_safety_rear_right"):
            right_new_vel = self.max_vel
            for x in range(700,900,5):
                if median(msg.ranges[x-2:x+3]) < self.speed_fb * 1.5:
                    self.right_vel = self.max_vel / 2
        elif (msg.header.frame_id == "lidar_safety_rear_left"):
            right_new_vel = self.max_vel
            for x in range(200,400,5):
                if median(msg.ranges[x-2:x+3]) < self.speed_fb * 1.5:
                    self.left_vel = self.max_vel / 2

        if self.speed_fb < 1.0:
            new_vel = self.max_vel
        else:
            new_vel = min(self.right_vel, self.left_vel)
        
        new_msg = Vector3Stamped()
        new_msg.header.stamp = self.get_clock().now().to_msg()
        new_msg.vector.x = new_vel
        new_msg.vector.y = 0.0
        new_msg.vector.z = 0.0
        self.speed_limit_pub.publish(new_msg)

        return


def main(args=None):
    rclpy.init()
    node = lidarSpeedLimiterNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
