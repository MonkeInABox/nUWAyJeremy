########################
# Author: Lemar Haddad
# Version: 01.02.22
# ----------------------
# Processes lidar scans to detect if an object is close
# to the vehicle, which acts as a trigger to begin
# recording an incident.
########################

import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import ParameterDescriptor

import math

from std_msgs.msg import String
from sensor_msgs.msg import LaserScan


class IncidentDetector(Node):

    def __init__(self):
        super().__init__('incident_detector')
        self.publisher_ = self.create_publisher(String, 'safety_event_flag', 1)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.publish_flag)


        min_dist_param_descriptor = ParameterDescriptor(description='The distance that a safety incident will flag at.')
        self.declare_parameter('min_dist', 2.0, min_dist_param_descriptor)

        self.create_subscription(LaserScan, "/lidar_safety/front_left/scan", self.received_fl_scan, 1)
        self.create_subscription(LaserScan, "/lidar_safety/front_right/scan", self.received_fr_scan, 1)
        self.create_subscription(LaserScan, "/lidar_safety/rear_right/scan", self.received_rl_scan, 1)
        self.create_subscription(LaserScan, "/lidar_safety/rear_left/scan", self.received_rr_scan, 1)


        self.fl_flag = False # safety flag for front left lidar
        self.fr_flag = False # safety flag for front right lidar
        self.rl_flag = False # safety flag for rear left lidar
        self.rr_flag = False # safety flag for rear right lidar
    

    def received_fl_scan(self, scan):
        safetyFlag = self.process_lidar_scan(scan)
        self.fl_flag = safetyFlag
    
    def received_fr_scan(self, scan):
        safetyFlag = self.process_lidar_scan(scan)
        self.fr_flag = safetyFlag
    
    def received_rl_scan(self, scan):
        safetyFlag = self.process_lidar_scan(scan)
        self.rl_flag = safetyFlag
    
    def received_rr_scan(self, scan):
        safetyFlag = self.process_lidar_scan(scan)
        self.rr_flag = safetyFlag
    
    """
    Processes and samples the lidar scan
    # Based off code for the turtlebot obstacle detection
    # https://github.com/ROBOTIS-GIT/turtlebot3/blob/master/turtlebot3_example/nodes/turtlebot3_obstacle
    """
    def process_lidar_scan(self, scan):
        samples = len(scan.ranges)

        scan_filter = scan.ranges
        
        for i in range(samples):
            # max lidar range may be represented as inf
            if scan_filter[i] == float('Inf'):
                scan_filter[i] = scan.range_max
            # min lidar range may be represented as NaN
            elif math.isnan(scan_filter[i]):
                scan_filter[i] = scan.range_max

            elif scan_filter[i] <= 0.1:
                scan_filter[i] = scan.range_max


        min_dist = min(scan_filter)
        
        # we have a point which triggers a safety incident
        if min_dist < self.get_parameter('min_dist').value:
            self.get_logger().info("Distance: %f" % min_dist)
            return True
        
        return False



    def publish_flag(self):
        msg = String()
        isIncident = self.fl_flag or self.fr_flag or \
                        self.rl_flag or self.rr_flag
        msg.data = '%s' % isIncident
        self.publisher_.publish(msg)
        self.get_logger().info('Incident Flag: "%s"' % msg.data)


def main(args=None):
    rclpy.init(args=args)

    incident_detector = IncidentDetector()

    rclpy.spin(incident_detector)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    incident_detector.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()