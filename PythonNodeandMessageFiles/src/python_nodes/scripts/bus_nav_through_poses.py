#! /usr/bin/env python3
# Copyright 2021 Samsung Research America
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Modified by AutomaticAddison.com 
#
# 2023 Sep 28: Modified by UWA REV Team
import time # Time library
import numpy as np
from geometry_msgs.msg import PoseStamped # Pose with ref frame and timestamp
from rclpy.duration import Duration # Handles time for ROS 2
import rclpy # Python client library for ROS 2
from rclpy.node import Node
from python_nodes.scripts.robot_navigator import BasicNavigator, NavigationResult # Helper module

'''
Navigates a nUWAy through goal poses from a csv file.
'''
class BusNavThroughPoses(Node):
    def __init__(self):
        super().__init__('bus_nav_through_poses')
        # Launch the ROS 2 Navigation Stack
        self.navigator = BasicNavigator()
        # Wait for navigation to fully activate. Use this line if autostart is set to true.
        self.navigator.waitUntilNav2Active()
        self.poses_arr=np.loadtxt(self.file_path,delimiter=",", dtype=float)
        # Set the robot's goal poses
        self.goal_poses = []
        for i in range (len(self.poses_arr)):
          self.goal_pose = PoseStamped()
          self.goal_pose.header.frame_id = 'map'
          self.goal_pose.header.stamp = self.navigator.get_clock().now().to_msg()
          self.goal_pose.pose.position.x = self.poses_arr[i][1]
          self.goal_pose.pose.position.y = self.poses_arr[i][2]
          self.goal_pose.pose.position.z = 0.0
          self.goal_pose.pose.orientation.x = 0.0
          self.goal_pose.pose.orientation.y = 0.0
          self.goal_pose.pose.orientation.z = self.poses_arr[i][3]
          self.goal_pose.pose.orientation.w = self.poses_arr[i][4]
          self.goal_poses.append(self.goal_pose)

        # Go through the goal poses
        self.navigator.goThroughPoses(self.goal_poses)

        i = 0
        # Keep doing stuff as long as the robot is moving towards the goal poses
        while not self.navigator.isNavComplete():
          ################################################
          #
          # Implement some code here for your application!
          #
          ################################################

          # Do something with the self.feedback
          i = i + 1
          self.feedback = self.navigator.getFeedback()
          if self.feedback and i % 10 == 0:
            self.get_logger().info('Distance remaining: ' + '{:.2f}'.format(
                  self.feedback.distance_remaining) + ' meters.')

            # Some navigation timeout to demo cancellation
            if Duration.from_msg(self.feedback.navigation_time) > Duration(seconds=1000000.0):
              self.navigator.cancelNav()

        # Do something depending on the return code
        self.result = self.navigator.getResult()
        if self.result == NavigationResult.SUCCEEDED:
          self.get_logger().info('Goal succeeded!')
        elif self.result == NavigationResult.CANCELED:
          self.get_logger().info('Goal was canceled!')
        elif self.result == NavigationResult.FAILED:
          self.get_logger().info('Goal failed!')
        else:
          self.get_logger().info('Goal has an invalid return status!')

        # Close the ROS 2 Navigation Stack
        self.navigator.lifecycleShutdown()

      

def main(args=None):

  # Start the ROS 2 Python Client Library
  rclpy.init(args=args)
  bus_nav_through_poses=BusNavThroughPoses()
  try:
    rclpy.spin(bus_nav_through_poses)
  except KeyboardInterrupt:
      pass
  rclpy.shutdown()

if __name__ == '__main__':
  main()
