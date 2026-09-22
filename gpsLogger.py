#!/usr/bin/env python3
"""
Usage:
    python3 gpsLogger.py --ros-args -p gps_topic:=/gps -p output_csv:=gps_log.csv

If output_csv isn't given, a filename is generated with the current
date/time so repeated runs don't overwrite each other.
"""

import csv
import os
from datetime import datetime

import rclpy
from rclpy.node import Node

from gps_msgs.msg import GPSFix


class GpsLogger(Node):
    def __init__(self):
        super().__init__("gps_logger")

        self.declare_parameter("gps_topic", "/gps")
        self.declare_parameter("output_csv", "")  
        self.declare_parameter("log_every_n", 1)  

        gps_topic = self.get_parameter("gps_topic").value
        output_csv = self.get_parameter("output_csv").value
        self.log_every_n = self.get_parameter("log_every_n").value

        if not output_csv:
            output_csv = f"gps_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        self.output_csv = output_csv

        file_exists = os.path.exists(self.output_csv)
        self.csv_file = open(self.output_csv, "a", newline="")
        self.csv_writer = csv.writer(self.csv_file)
        if not file_exists:
            self.csv_writer.writerow([
                "ros_stamp_sec", "ros_stamp_nanosec", "wall_clock_iso",
                "latitude", "longitude", "altitude",
                "track", "speed", "climb",
            ])
            self.csv_file.flush()

        self._msg_count = 0

        self.sub = self.create_subscription(GPSFix, gps_topic, self.gps_callback, 10)

        self.get_logger().info(f"Logging '{gps_topic}' to {self.output_csv}")

    def gps_callback(self, msg: GPSFix):
        self._msg_count += 1
        if (self._msg_count - 1) % self.log_every_n != 0:
            return

        wall_clock_iso = datetime.now().isoformat(timespec="milliseconds")

        self.csv_writer.writerow([
            msg.header.stamp.sec,
            msg.header.stamp.nanosec,
            wall_clock_iso,
            msg.latitude,
            msg.longitude,
            msg.altitude,
            msg.track,
            msg.speed,
            msg.climb,
        ])
        
        self.csv_file.flush()

        self.get_logger().info(
            f"lat={msg.latitude:.6f} lon={msg.longitude:.6f} alt={msg.altitude:.1f} "
            f"speed={msg.speed:.2f} @ stamp={msg.header.stamp.sec}.{msg.header.stamp.nanosec}",
            throttle_duration_sec=2.0,  # don't spam the console if GPS publishes fast
        )

    def destroy_node(self):
        self.csv_file.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = GpsLogger()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Stopped by user.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
