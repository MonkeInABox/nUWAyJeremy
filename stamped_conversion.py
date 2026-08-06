#!/usr/bin/env python

from std_msgs.msg import Int32, Float32MultiArray, String
from geometry_msgs.msg import Twist, TwistStamped
import rclpy
from python_nodes_interfaces.msg import Int32Stamped, Float32MultiArrayStamped, StringStamped
from rclpy.node import Node

class stampedConverter(Node):

    def __init__(self):
        super().__init__("stamped_conversion")

        self.create_subscription(Twist, "/joy_cmd_vel", self.convert_cmd_vel_cb, 10)
        self.create_subscription(Twist, "/gps_cmd_vel", self.convert_gps_vel_cb, 10)
        self.create_subscription(Float32MultiArray, "/drive_cmds", self.convert_drive_cmd_cb, 10)
        self.create_subscription(Int32, "/driving_mode", self.convert_driving_mode_cb, 10)
        self.create_subscription(String, "/stop_slow_signal", self.convert_stop_slow_signal_cb, 10)
        self.create_subscription(String, "/errorCodesDisp", self.convert_errorCodesDisp_cb, 10)

        self.joy_cmd_convert_pub = self.create_publisher(TwistStamped, "/joy_cmd_vel_stamped", 10)
        self.gps_cmd_convert_pub = self.create_publisher(TwistStamped, "/gps_cmd_vel_stamped", 10)
        self.drive_cmds_pub = self.create_publisher(Float32MultiArrayStamped, "/drive_cmds_stamped", 10)
        self.driving_mode_convert_pub = self.create_publisher(Int32Stamped, "/driving_mode_stamped", 10)
        self.slow_stop_signal_pub = self.create_publisher(Float32MultiArrayStamped, "/stop_slow_signal_stamped", 10)
        self.errorCodesDisp_pub = self.create_publisher(Int32Stamped, "/errorCodesDisp_stamped", 10)

        self.get_logger().info("started conversion node")

    def convert_cmd_vel_cb(self, data):
        msg = TwistStamped()

        msg.twist = data
        msg.header.stamp = self.get_clock().now().to_msg()

        self.joy_cmd_convert_pub.publish(msg)

    def convert_gps_vel_cb(self, data):
        msg = TwistStamped()

        msg.twist = data
        msg.header.stamp = self.get_clock().now().to_msg()

        self.gps_cmd_convert_pub.publish(msg)

    def convert_driving_mode_cb(self, data):
        msg = Int32Stamped()

        msg.data = data.data
        msg.header.stamp = self.get_clock().now().to_msg()

        self.driving_mode_convert_pub.publish(msg)

    def convert_drive_cmd_cb(self, data):
        msg = Float32MultiArrayStamped()

        msg.data = data.data
        msg.header.stamp = self.get_clock().now().to_msg()

        self.drive_cmds_pub.publish(msg)

    def convert_slow_stop_signal_cb(self, data):
        msg = StringStamped()

        msg.data = data.data
        msg.header.stamp = self.get_clock().now().to_msg()

        self.slow_stop_signal_pub.publish(msg)

    def convert_errorCodesDisp_cb(self, data):
        msg = StringStamped()

        msg.data = data.data
        msg.header.stamp = self.get_clock().now().to_msg()

        self.errorCodesDisp_pub.publish(msg)


def main(args=None):
    rclpy.init()
    node = stampedConverter()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
