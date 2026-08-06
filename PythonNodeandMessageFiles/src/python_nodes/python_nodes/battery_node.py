#!/usr/bin/env python

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32
from python_nodes_interfaces.msg import StringMultiArrayStamped

import os


class battery_node(Node):

    def __init__(self):
        super().__init__("battery_node")

        self.timer_cb = self.create_timer(5.0, self.update_controller_cb)
        self.controller_battery_pub = self.create_publisher(Float32, "/controller_battery_percent", 10)
        self.controller_status_pub = self.create_publisher(String, "/controller_status_percent", 10)
        
        self.get_logger().info("started controller battery node")
        self.folders = os.listdir("/sys/class/power_supply")

        self.dir = None

        for i in self.folders:
            if "sony_controller" in i:
                self.dir = i

        self.green = None
        self.red = None
        self.blue = None

        self.led_folder_path = "/sys/class/power_supply/" + self.dir + "/powers/leds"
        self.led_folder = os.listdir(self.led_folder_path)

        for i in self.led_folder:
            if "green" in i:
                self.green_file = i
            if "red" in i:
                self.red_file = i
            if "blue" in i:
                self.blue_file = i

        if self.dir == None:
            exit(1)

        self.path = "/sys/class/power_supply/" + self.dir


    def update_controller_cb(self):
        file = open(self.path + "/capacity", "r")
        battery_percent = float(file.readline().strip())
        file.close()

        msg = Float32()
        msg.data = battery_percent
        self.controller_battery_pub.publish(msg)

        file = open(self.path + "/status", "r")
        status = file.readline().strip()
        file.close()

        # msg = String()
        # msg.data = String(status)
        # self.controller_battery_pub.publish(msg)

        # updates ps4 controller LED depending on battery level
        if battery_percent > 70.0:
            os.system("echo 255 | sudo tee -a " + self.led_folder_path + "/" + self.green_file + "/brightness >/dev/null 2>&1")
            os.system("echo 0 | sudo tee -a " + self.path + "/" + self.blue_file + "/brightness >/dev/null 2>&1")
            os.system("echo 0 | sudo tee -a " + self.path + "/" + self.red_file + "/brightness >/dev/null 2>&1")
        elif battery_percent > 60.0:
            os.system("echo 155 | sudo tee -a " + self.path + "/" + self.green_file + "/brightness >/dev/null 2>&1")
            os.system("echo 155 | sudo tee -a " + self.path + "/" + self.blue_file + "/brightness >/dev/null 2>&1")
            os.system("echo 0 | sudo tee -a " + self.path + "/" + self.red_file + "/brightness >/dev/null 2>&1")
        elif battery_percent > 40.0:
            os.system("echo 0 | sudo tee -a " + self.path + "/" + self.green_file + "/brightness >/dev/null 2>&1")
            os.system("echo 255 | sudo tee -a " + self.path + "/" + self.blue_file + "/brightness >/dev/null 2>&1")
            os.system("echo 0 | sudo tee -a " + self.path + "/" + self.red_file + "/brightness >/dev/null 2>&1")
        elif battery_percent > 20.0:
            os.system("echo 0 | sudo tee -a " + self.path + "/" + self.green_file + "/brightness >/dev/null 2>&1")
            os.system("echo 155 | sudo tee -a " + self.path + "/" + self.blue_file + "/brightness >/dev/null 2>&1")
            os.system("echo 155 | sudo tee -a " + self.path + "/" + self.red_file + "/brightness >/dev/null 2>&1")
        elif battery_percent > 10.0:
            os.system("echo 0 | sudo tee -a " + self.path + "/" + self.green_file + "/brightness >/dev/null 2>&1")
            os.system("echo 0 | sudo tee -a " + self.path + "/" + self.blue_file + "/brightness >/dev/null 2>&1")
            os.system("echo 255 | sudo tee -a " + self.path + "/" + self.red_file + "/brightness >/dev/null 2>&1")
        else:
            os.system("echo 0 | sudo tee -a " + self.path + "/" + self.green_file + "/brightness >/dev/null 2>&1")
            os.system("echo 0 | sudo tee -a " + self.path + "/" + self.blue_file + "/brightness >/dev/null 2>&1")
            os.system("echo 100 | sudo tee -a " + self.path + "/" + self.red_file + "/brightness >/dev/null 2>&1")

        return




def main(args=None):
    rclpy.init()

    node = battery_node()  
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
