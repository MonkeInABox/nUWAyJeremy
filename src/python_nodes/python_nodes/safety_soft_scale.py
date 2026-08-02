#!/usr/bin/env python3

# Safety node using the corner LiDARs to detect surrounding obstacles
# and publish a value between 0 and 1 for the proportional control of
# speed, where 0 corresponds to a speed of 0 is required, and 1 corresponds
# to the speed required by the local planner is ok.
#
# Written by Jai Castle

import rclpy
from rclpy.node import Node
import numpy as np
import math

from sensor_msgs.msg import LaserScan
from std_msgs.msg import Float64
from geometry_msgs.msg import Twist

SAFETY_THRESHOLD_LOWER_METRES = 1.5 # Metres
SAFETY_THRESHOLD_UPPER_METRES = 3 # Metres

EXPECTED_LIDAR_LENGTH = 1081 # Elements
STRAIGHT_AHEAD_INDEX_ONE_THIRD = int(2*EXPECTED_LIDAR_LENGTH/3) # Indices
STRAIGHT_AHEAD_INDEX_TWO_THIRDS = int(1*EXPECTED_LIDAR_LENGTH/3) # Indices
LIDAR_VIEWING_ANGLE_RANGE = 1.5 * math.pi # Radians
STRAIGHT_AHEAD_INDEX_TOLERANCE = int(EXPECTED_LIDAR_LENGTH * 0.05) # 5% of the array
START_INDEX = 50 # So that we don't see the LiDAR on the other side


class SoftScale(Node):
    def __init__(self):
        global pub
        super().__init__("safety_soft_scale")

        # Starting at front left, front right, rear left, rear right
        self.cornerScales = [1, 1, 1, 1] # Scales in the range [0, 1]
        self.scalesHistory = []

        # Current velocity measurements
        self.currentSpeed = 0
        self.currentSteeringAngle = 0
        self.steeringLidarIndexChange = 0

        self.pub = self.create_publisher(Float64, "safety_soft_stop_scale", 1000)
        
        self.create_subscription(LaserScan, "/lidar_safety/front_left/scan", self.frontLeftReceived, 10)
        self.create_subscription(LaserScan, "/lidar_safety/front_right/scan", self.frontRightReceived, 10)
        self.create_subscription(LaserScan, "/lidar_safety/rear_left/scan", self.rearLeftReceived, 10)
        self.create_subscription(LaserScan, "/lidar_safety/rear_right/scan", self.rearRightReceived, 10)

        # Current bus velocity & direction
        self.create_subscription(Twist, "/cmd_vel", self.updateSteering, 1)
    
    def updateSteering(self, data):
        self.currentSpeed = data.linear.x
        self.currentSteeringAngle = float(data.angular.z)
        if abs(currentSteeringAngle) > 0.2:
            self.steeringLidarIndexChange = int((EXPECTED_LIDAR_LENGTH/5) * (currentSteeringAngle/LIDAR_VIEWING_ANGLE_RANGE))
        else:
            self.steeringLidarIndexChange = 0

    def frontLeftReceived(self, data):
        if self.currentSpeed < 0:
            return
        ranges = data.ranges[STRAIGHT_AHEAD_INDEX_ONE_THIRD - STRAIGHT_AHEAD_INDEX_TOLERANCE - self.steeringLidarIndexChange : len(data.ranges) - START_INDEX]
        self.lidarDataReceived(ranges, data.range_min, data.range_max, 0)


    def frontRightReceived(self, data):
        if self.currentSpeed < 0:
            return
        ranges = data.ranges[START_INDEX: STRAIGHT_AHEAD_INDEX_TWO_THIRDS + STRAIGHT_AHEAD_INDEX_TOLERANCE + self.steeringLidarIndexChange]
        self.lidarDataReceived(ranges, data.range_min, data.range_max, 1)


    def rearLeftReceived(self, data):
        if self.currentSpeed >= 0:
            return
        ranges = data.ranges[START_INDEX: STRAIGHT_AHEAD_INDEX_TWO_THIRDS + STRAIGHT_AHEAD_INDEX_TOLERANCE + self.steeringLidarIndexChange]
        self.lidarDataReceived(ranges, data.range_min, data.range_max, 2)


    def rearRightReceived(self, data):
        if self.currentSpeed >= 0:
            return
        ranges = data.ranges[STRAIGHT_AHEAD_INDEX_ONE_THIRD - STRAIGHT_AHEAD_INDEX_TOLERANCE - self.steeringLidarIndexChange : len(data.ranges) - START_INDEX]
        self.lidarDataReceived(ranges, data.range_min, data.range_max, 3)


    def lidarDataReceived(self, ranges, minValue, maxValue, index):
        lidarRanges = [i for i in ranges if i > minValue and i <= maxValue]

        if (len(lidarRanges) == 0): # E.g. all values infinite
            self.cornerScales[index] = 1 
        else:
            value = np.percentile(lidarRanges, 10)

            smallerThanThreshold = 0
            largerThanThreshold = 0
            for dataPoint in lidarRanges:
                if dataPoint <= SAFETY_THRESHOLD_LOWER_METRES:
                    smallerThanThreshold += 1
                elif dataPoint >= SAFETY_THRESHOLD_UPPER_METRES:
                    largerThanThreshold += 1

            if value <= SAFETY_THRESHOLD_LOWER_METRES:
                self.cornerScales[index] = 0.0  # Stop is required
            elif value >= SAFETY_THRESHOLD_UPPER_METRES:
                self.cornerScales[index] = 1.0  # No speed restrictions
            else:
                # Proportional speed to distance
                self.cornerScales[index] = (value - SAFETY_THRESHOLD_LOWER_METRES) / (SAFETY_THRESHOLD_UPPER_METRES-SAFETY_THRESHOLD_LOWER_METRES)

        # Publish the minimum scale recorded to allow for a stop if necessary
        if self.currentSpeed >= 0:
            scales = self.cornerScales[0:2]  # Forward scales
        else:
            scales = self.cornerScales[2:4]  # Rear scales

        scale = float(min(scales))


        self.scalesHistory.append(scale)
        length = len(self.scalesHistory)
        if length > 5:
            self.scalesHistory.pop(0)
            length -= 1
        message = Float64()
        message.data = float(0 if any([s == 0 for s in self.scalesHistory]) else scale)
        self.pub.publish(message)

def main(args=None):
    rclpy.init(args=args)
    node = SoftScale()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == "__main__":
    main()