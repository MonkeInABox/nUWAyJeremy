import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, Point
from sensor_msgs.msg import LaserScan, PointCloud2
from sensor_msgs_py import point_cloud2
from visualization_msgs.msg import Marker
from std_msgs.msg import String, Float32, Int32, Bool

from rclpy.qos import ReliabilityPolicy, QoSProfile, DurabilityPolicy

import math
#comment
class StopNode(Node):
    def __init__(self):
        super().__init__('stop_node')

        #Publisher for control signals
        self.signal_publisher_ = self.create_publisher(
            String,
            '/stop_slow_signal',
            QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)
        )
        self.control_signal_last = ""

        self.publisher_ = self.create_publisher(
            Twist,
            '/stop_slow_speed',
            QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)
        )

        self.alive_pub_ = self.create_publisher(
            Bool,
            '/alive',
            QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)
        )

        # Publisher for RViz marker
        self.marker_publisher_ = self.create_publisher(
            Marker,
            '/visualization_marker',
            QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)
        )

        # self.left_marker_publisher_ = self.create_publisher(
        #     Marker,
        #     '/left_visualization_marker',
        #     QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)
        # )

        # self.right_marker_publisher_ = self.create_publisher(
        #     Marker,
        #     '/right_visualization_marker',
        #     QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)
        # )

        self.front_lidar_pub = self.create_publisher(
            LaserScan,
            '/front_lidar_section',
            QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)
        )

        self.front_pointcloud_pub = self.create_publisher(
            PointCloud2,
            '/front_pointcloud_section',
            QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)
        )

        self.rear_pointcloud_pub = self.create_publisher(
            PointCloud2,
            '/rear_pointcloud_section',
            QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)
        )

        self.lock_left_pub = self.create_publisher(
            Float32,
            '/lock_left_angular',
            QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)
        )

        self.lock_right_pub = self.create_publisher(
            Float32,
            '/lock_right_angular',
            QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)
        )

        # Subscriber for /scan topic
        # self.subscription = self.create_subscription(
        #     LaserScan,
        #     '/lidar/safety_merged/scan', ### Often just called '/scan'
        #     self.scan_callback,
        #     QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        # )

        # Subscriber for /point cloud topic
        self.point_subscription = self.create_subscription(
            PointCloud2,
            '/lidar/safety_merged/cloud',
            self.pointcloud_callback,
            QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        )
        
        # Subscriber for /cmd_vel topic to get the current velocity
        self.velocity_subscription = self.create_subscription(
            Float32,
            '/speed_fb',
            self.velocity_callback,
            QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)
        )

        # Subscriber for /cmd_vel topic to get the current velocity
        self.steering_subscription = self.create_subscription(
            Float32,
            '/rear_steering_fb',
            self.steering_callback,
            QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)
        )

        self.driving_mode_subscription = self.create_subscription(
            Int32,
            '/driving_mode',
            self.driving_mode_callback,
            QoSProfile(depth=10, reliability=ReliabilityPolicy.RELIABLE)
        )

        self.timer_ = self.create_timer(0.2, self.publishAlive)
        
        # self.subscription  # prevents unused variable warning
        self.point_subscription
        self.velocity_subscription
        self.steering_subscription
        self.driving_mode_subscription
        
        self.timer_val = 0.5   # Timer for checking distance to nearest object. Consider increasing with speed and/or when an obstacle has been detected nearby
        #self.timer = self.create_timer(self.timer_val, self.publish_stop_or_slow)
        
        self.stop_required = False
        self.slow_down_required = False
        self.last_stop = self.get_clock().now()

        self.x_bound = 2.2
        self.y_upper_bound = 1.45
        self.y_lower_bound = -1.45

        self.max_speed = 5.3
        
        # Default stop and slow zone disatances. Set at your own preferences
        self.stop_threshold_min = 2.0 + 0.5
        self.slow_down_threshold_min = 4.7 + 0.7

        self.side_stop_threshold_min = 1.1
        self.side_slow_down_threshold_min = 1.3

        self.stop_threshold = self.stop_threshold_min
        self.slow_down_threshold = self.slow_down_threshold_min

        # self.current_velocity = Float32()
        self.current_velocity = 0.0
        self.current_steering = 0.0
        self.steering_offset = self.current_steering / 3.3 * 0.8
        self.driving_mode = 0
        
        self.get_logger().info('Node has been started.')

    # def scan_callback(self, msg):
    #     '''
    #     Callback function that publishes "stop", "slow", or "clear" strings to
    #     the /stop_slow_signal topic for /cmd_vel publisher to respond to.
        
    #     '''

    #     num_ranges = len(msg.ranges)
    #     # min_distance = min(msg.ranges)
    #     self.update_thresholds()

    #     min_distance, direction = self.adjust_zones_based_on_movement(msg)

    #     # Publish the polygon marker to visualize min_distance
    #     self.publish_polygon_marker(direction)

    #     control_signal = String()
    #     current_time = self.get_clock().now()

    #     # if (current_time - self.last_stop < 1):
    #     #     return

    #     if min_distance < self.stop_threshold:
    #         if self.control_signal_last != "stop":
    #             control_signal.data = "stop"
    #             self.control_signal_last = "stop"
    #             self.signal_publisher_.publish(control_signal)
    #             self.get_logger().info('Publishing stop signal.')
    #     elif min_distance < self.slow_down_threshold:
    #         if self.control_signal_last != "slow_down":
    #             control_signal.data = "slow_down"
    #             self.control_signal_last = "slow_down"
    #             self.signal_publisher_.publish(control_signal)
    #             self.get_logger().info('Publishing slow down signal.')
    #     else:
    #         if self.control_signal_last != "normal":
    #             control_signal.data = "normal"
    #             self.control_signal_last = "normal"
    #             self.signal_publisher_.publish(control_signal)
    #             self.get_logger().info('Publishing normal signal.')
        # else:
        #     control_signal.data = "clear"
        #     self.signal_publisher_.publish(control_signal)
        #     self.get_logger().info('Publishing clear signal.')

    def publishAlive(self):
        msg = Bool()
        msg.data = True
        self.alive_pub_.publish(msg)

    def pointcloud_callback(self, msg):
        '''
        Callback function that publishes "stop", "slow", or "clear" strings to
        the /stop_slow_signal topic for /cmd_vel publisher to respond to.
        
        '''

        data_points = point_cloud2.read_points(msg)
        
        num_ranges = len(data_points)
        # min_distance = min(msg.ranges)
        self.update_thresholds()

        front_sector, rear_sector, min_distance, direction = self.adjust_pointcloud_zones_based_on_movement(data_points)

        # Publish the polygon marker to visualize min_distance
        # self.publish_polygon_marker(direction)

        new_cloud = point_cloud2.create_cloud_xyz32(msg.header, front_sector)
        new_cloud.header.stamp = self.get_clock().now().to_msg()

        self.front_pointcloud_pub.publish(new_cloud)

        new_cloud = point_cloud2.create_cloud_xyz32(msg.header, rear_sector)
        new_cloud.header.stamp = self.get_clock().now().to_msg()

        self.rear_pointcloud_pub.publish(new_cloud)

        control_signal = String()
        current_time = self.get_clock().now()

        # if (current_time - self.last_stop < 1):
        #     return

        if min_distance < self.stop_threshold:
            if self.control_signal_last != "stop":
                control_signal.data = "stop"
                self.control_signal_last = "stop"
                self.signal_publisher_.publish(control_signal)
                self.stop_required = True
                self.get_logger().info('Publishing stop signal.')
        elif min_distance < self.slow_down_threshold:
            if self.control_signal_last != "slow_down":
                control_signal.data = "slow_down"
                self.control_signal_last = "slow_down"
                self.signal_publisher_.publish(control_signal)
                self.slow_down_required = True
                self.get_logger().info('Publishing slow down signal.')
        else:
            if self.control_signal_last != "normal":
                control_signal.data = "normal"
                self.control_signal_last = "normal"
                self.signal_publisher_.publish(control_signal)
                self.slow_down_required = False
                self.stop_required = False
                self.get_logger().info('Publishing normal signal.')
        self.publish_stop_or_slow(min_distance)
        # else:
        #     control_signal.data = "clear"
        #     self.signal_publisher_.publish(control_signal)
        #     self.get_logger().info('Publishing clear signal.')

    def divide_pointcloud_into_sectors(self, data_points):

        front_sector, rear_sector = [], []
        left_lock_sector, right_lock_sector = [], []
        front_min, rear_min = 10000.0, 10000.0
        left_min_angle = 0.28
        right_min_angle = -0.28

        self.steering_offset = self.current_steering / 3.3 * 0.9
        
        for p in data_points:
            #Middle
            if p[1] > self.y_lower_bound / 2 and p[1] < self.y_upper_bound / 2:
                if p[0] < -self.x_bound and p[0] > -self.slow_down_threshold:
                    front_sector.append(p)
                    dist = math.sqrt(p[0] ** 2 + p[1] ** 2)
                    if dist < front_min:
                        front_min = dist
                if p[0] > self.x_bound and p[0] < self.slow_down_threshold:
                    rear_sector.append(p)
                    dist = math.sqrt(p[0] ** 2 + p[1] ** 2)
                    if dist < rear_min:
                        rear_min = dist
            #Left
            if p[1] > self.y_lower_bound and p[1] < self.y_lower_bound / 2:
                if p[0] < -self.x_bound and p[0] > -(self.slow_down_threshold + self.steering_offset):
                    front_sector.append(p)
                    dist = math.sqrt(p[0] ** 2 + p[1] ** 2)
                    if dist < front_min:
                        front_min = dist
                if p[0] > self.x_bound and p[0] < (self.slow_down_threshold + self.steering_offset):
                    rear_sector.append(p)
                    dist = math.sqrt(p[0] ** 2 + p[1] ** 2)
                    if dist < rear_min:
                        rear_min = dist
            #Right
            if p[1] > self.y_upper_bound / 2 and p[1] < self.y_upper_bound:
                if p[0] < -self.x_bound and p[0] > -(self.slow_down_threshold - self.steering_offset):
                    front_sector.append(p)
                    dist = math.sqrt(p[0] ** 2 + p[1] ** 2)
                    if dist < front_min:
                        front_min = dist
                if p[0] > self.x_bound and p[0] < (self.slow_down_threshold - self.steering_offset):
                    rear_sector.append(p)
                    dist = math.sqrt(p[0] ** 2 + p[1] ** 2)
                    if dist < rear_min:
                        rear_min = dist
            #Short Left
            if p[1] < self.y_lower_bound and p[1] > self.y_lower_bound - 0.13 * max(self.current_velocity - 2.0, 0.1):
                if p[0] < -self.x_bound and p[0] > -(self.slow_down_threshold + self.steering_offset):
                    front_sector.append(p)
                    dist = math.sqrt(p[0] ** 2 + p[1] ** 2)
                    if dist < front_min:
                        front_min = dist
                if p[0] > self.x_bound and p[0] < (self.slow_down_threshold + self.steering_offset):
                    rear_sector.append(p)
                    dist = math.sqrt(p[0] ** 2 + p[1] ** 2)
                    if dist < rear_min:
                        rear_min = dist
            #Short Right
            if p[1] > self.y_upper_bound and p[1] < self.y_upper_bound + 0.13 * max(self.current_velocity - 2.0, 0.1):
                if p[0] < -0.5 and p[0] > -2.5:
                    front_sector.append(p)
                    dist = math.sqrt(p[0] ** 2 + p[1] ** 2)
                    if dist < front_min:
                        front_min = dist
                if p[0] > 0.5 and p[0] < 2.5:
                    rear_sector.append(p)
                    dist = math.sqrt(p[0] ** 2 + p[1] ** 2)
                    if dist < rear_min:
                        rear_min = dist


            

            # lock left
            if p[1] < self.y_lower_bound - 0.35 and p[1] > self.y_lower_bound - 0.6:
                if (p[0] < -0.5 and p[0] > -6.5 and self.current_velocity > 0.0) or (p[0] > 0.5 and p[0] < 6.5 and self.current_velocity < 0.0):
                    left_lock_sector.append(p)
                    if left_min_angle < 0.0:
                        left_min_angle = 0.0

            # lock Right
            if p[1] > self.y_upper_bound + 0.35 and p[1] < self.y_upper_bound + 0.6:
                if (p[0] < -0.5 and p[0] > -6.5 and self.current_velocity > 0.0) or (p[0] > 0.5 and p[0] < 6.5 and self.current_velocity < 0.0):
                    right_lock_sector.append(p)
                    if right_min_angle > 0.0:
                        right_min_angle = 0.0

            # force right
            if p[1] < self.y_lower_bound and p[1] > self.y_lower_bound - 0.36:
                if (p[0] < -0.5 and p[0] > -5.5 and self.current_velocity > 0.0) or (p[0] > 0.5 and p[0] < 5.5 and self.current_velocity < 0.0):
                    left_lock_sector.append(p)
                    if left_min_angle > -0.01:
                        left_min_angle = -0.06


            # force left
            if p[1] > self.y_upper_bound and p[1] < self.y_upper_bound + 0.36:
                if (p[0] < -0.5 and p[0] > -5.5 and self.current_velocity > 0.0) or (p[0] > 0.5 and p[0] < 5.5 and self.current_velocity < 0.0):
                    right_lock_sector.append(p)
                    if right_min_angle < 0.01:
                        right_min_angle = 0.06

            # ensure that the vehicle isn't trying to turn both left and right
            if right_min_angle > 0.0 and left_min_angle < 0.0:
                right_min_angle = 0.0
                left_min_angle = 0.0

        msg1 = Float32()
        msg1.data = left_min_angle
        msg2 = Float32()
        msg2.data = right_min_angle
            
        self.lock_left_pub.publish(msg1)
        self.lock_right_pub.publish(msg2)
            
                # if p[1] > self.y_lower_bound and p[1] < self.y_upper_bound:
                    # rear_sector.append(p)
                    # dist = math.sqrt(p[0] ** 2 + p[1] ** 2)
                    # if dist < rear_min:
                    #     rear_min = dist

        self.publish_polygon_marker()

        return front_sector, rear_sector, front_min, rear_min
            

    def adjust_pointcloud_zones_based_on_movement(self, point_data):
        '''
        Adjusts the stop and slow-down zones based on the robot's movement direction.
        '''
        front_sector, rear_sector, front_min, rear_min = self.divide_pointcloud_into_sectors(point_data)

        # self.get_logger().info(f"front points are: {front_sector}")
        # self.get_logger().info(f"rear points are: {rear_sector}")
        speed_threshold = 1.1
        if self.driving_mode == 0:
            speed_threshold = 2.0

        # Determine movement direction based on linear and angular velocities
        if self.current_velocity > speed_threshold:  # Moving forward
            # min_front_distance = min(front_sector)
            return front_sector, rear_sector, front_min, 'front'

        elif self.current_velocity < -speed_threshold:  # Moving backward (reverse)
            # min_rear_distance = min(rear_sector)  # Use actual rear sector data
            return front_sector, rear_sector, rear_min, 'rear'

        # elif self.current_velocity.angular.z > 0:  # Turning left
        #     min_left_distance = min(left_sector)
        #     return min_left_distance, 'left'

        # elif self.current_velocity.angular.z < 0:  # Turning right
        #     min_right_distance = min(right_sector)
        #     return min_right_distance, 'right'

        elif self.control_signal_last == "stop" and self.current_velocity > 0:
            return front_sector, rear_sector, front_min, 'front'
        
        elif self.control_signal_last == "stop" and self.current_velocity < 0:
            return front_sector, rear_sector, rear_min, 'rear'

        return front_sector, rear_sector, float('inf'), 'clear'  # No significant movement, assume clear
    
    # def divide_scan_into_sectors(self, msg):
    #     '''
    #     Divides the LaserScan data into front, left, right, and rear sectors.
    #     '''
    #     num_ranges = len(msg.ranges)
    #     sector_size = num_ranges // 8    # Must divide into 8 sectors due to rear comprising start and end of /scan array
        
    #     front_sector = msg.ranges[sector_size * 7:] + msg.ranges[0 : sector_size]
    #     rear_sector = msg.ranges[sector_size * 3 : sector_size * 5]
    #     left_sector = msg.ranges[sector_size * 5 : sector_size * 7]
    #     right_sector = msg.ranges[sector_size : sector_size * 3]
        
    #     front_lidar_message = msg
    #     front_lidar_message.header.stamp = self.get_clock().now().to_msg()

    #     for i in range(0, sector_size * 3):
    #         front_lidar_message.ranges[i] = 0

    #     for i in range(sector_size * 5, sector_size * 8):
    #         front_lidar_message.ranges[i] = 0

    #     self.front_lidar_pub.publish(front_lidar_message)
    #     return front_sector, left_sector, right_sector, rear_sector

    # def adjust_zones_based_on_movement(self, msg):
    #     '''
    #     Adjusts the stop and slow-down zones based on the robot's movement direction.
    #     '''
    #     front_sector, left_sector, right_sector, rear_sector = self.divide_scan_into_sectors(msg)

    #     # Determine movement direction based on linear and angular velocities
    #     if self.current_velocity > 0:  # Moving forward
    #         min_front_distance = min(front_sector)
    #         return min_front_distance, 'front'

    #     elif self.current_velocity < 0:  # Moving backward (reverse)
    #         min_rear_distance = min(rear_sector)  # Use actual rear sector data
    #         return min_rear_distance, 'rear'

    #     # elif self.current_velocity.angular.z > 0:  # Turning left
    #     #     min_left_distance = min(left_sector)
    #     #     return min_left_distance, 'left'

    #     # elif self.current_velocity.angular.z < 0:  # Turning right
    #     #     min_right_distance = min(right_sector)
    #     #     return min_right_distance, 'right'

    #     return float('inf'), 'clear'  # No significant movement, assume clear

    def velocity_callback(self, msg):
        '''
        Callback function that updates the current velocity of the robot.
        '''

        self.current_velocity = msg.data
        # self.get_logger().info(f"current velocity is: {self.current_velocity}")
        # self.get_logger().info(f'Current velocity: linear={msg.linear.x:.2f}, angular={msg.angular.z:.2f}')

    def steering_callback(self, msg):
        '''
        Callback function that updates the current velocity of the robot.
        '''

        self.current_steering = msg.data
        # self.get_logger().info(f"current velocity is: {self.current_velocity}")
        # self.get_logger().info(f'Current velocity: linear={msg.linear.x:.2f}, angular={msg.angular.z:.2f}')

    def driving_mode_callback(self, msg):
        self.driving_mode = msg.data

    def update_thresholds(self):
        '''
        Updates the stop and slow down thresholds based on current velocity
        Current implementation is just for testing, define your own logic here...
        '''

        current_speed = abs(self.current_velocity)
        # self.get_logger().info(f"current speed is: {current_speed}")
        # if current_speed < 0.5:
        #     self.get_logger().info(f"current speed is: {current_speed}")
        #     self.stop_threshold = self.stop_threshold_min
        #     self.slow_down_threshold = self.slow_down_threshold_min
        #     return

        # Linearly scale the thresholds based on speed, with a minimum threshold.
        dynamic_scale = current_speed * 1.95  # Adjust the scaling factor as needed

        addition = (current_speed // 0.5) * 0.25

        # Ensure the stop and slow-down thresholds don't decrease below the minimum
        self.stop_threshold = self.stop_threshold_min + dynamic_scale + addition
        self.slow_down_threshold = self.slow_down_threshold_min + dynamic_scale + addition

    def publish_stop_or_slow(self, min_distance):
        '''
        Timer callback to ensure stop command takes precedence if required.
        '''
        twist = Twist()

        if self.stop_required:
            twist.linear.x = 0.0
            twist.angular.z = 0.0
            self.publisher_.publish(twist)
            self.get_logger().info('Publishing stop command to override other commands.')
        elif self.slow_down_required:
            # Calculate the slow-down command based on current velocity
            x_slow = max(self.max_speed * (min((min_distance - self.stop_threshold_min) / (self.slow_down_threshold_min - self.stop_threshold_min), 1.0)), 0.1)
            # y_slow = max(self.max_speed * (min(min_distance / self.slow_down_threshold_min), 1.0), 0.1)
            twist.linear.x = min(x_slow, self.max_speed)
            # twist.linear.x = max(self.max_speed * (0.5 -  ((3.86 / min_distance) ** 2)), 0.1)  # Slow down by half, minimum speed 0.1
            # twist.angular.z = self.current_velocity.angular.z * 0.5  # Reduce angular speed similarly
            twist.angular.z = 0.0
            self.publisher_.publish(twist)
            self.get_logger().info('Publishing slow-down command to override other commands.')
        else:
            twist.linear.x = self.max_speed
            twist.angular.z = 0.0
            self.publisher_.publish(twist)
            self.get_logger().info('Publishing normal speed command.')


    def publish_polygon_marker(self):
        """
        Publishes polygon markers around the robot in RViz to denote the stop and slow-down distances,
        and adjusts the zones dynamically based on movement direction.
        """
        # Adjust the size of the zones based on the direction
        # front_stop = self.stop_threshold if direction == 'front' else self.stop_threshold_min / 2
        # rear_stop = self.stop_threshold if direction == 'rear' else self.stop_threshold_min / 2
    
        # # Adjust left and right stop zones dynamically based on direction of movement
        # left_stop = self.side_stop_threshold_min if direction == 'left' else self.side_stop_threshold_min
        # right_stop = self.side_stop_threshold_min if direction == 'right' else self.side_stop_threshold_min
    
        # # Adjust slow-down distances similarly
        # front_slow = self.slow_down_threshold if direction == 'front' else self.slow_down_threshold_min / 2
        # rear_slow = self.slow_down_threshold if direction == 'rear' else self.slow_down_threshold_min / 2
    
        # left_slow = self.side_slow_down_threshold_min if direction == 'left' else self.side_slow_down_threshold_min
        # right_slow = self.side_slow_down_threshold_min if direction == 'right' else self.side_slow_down_threshold_min
    
        # Stop zone marker
        stop_marker = Marker()
        stop_marker.header.frame_id = "base_link"
        stop_marker.header.stamp = self.get_clock().now().to_msg()
        stop_marker.ns = "stop_threshold_polygon"
        stop_marker.id = 0
        stop_marker.type = Marker.LINE_STRIP
        stop_marker.action = Marker.ADD
        stop_marker.scale.x = 0.05  # Line width
        stop_marker.color.a = 1.0
        stop_marker.color.r = 1.0
        stop_marker.color.g = 0.0
        stop_marker.color.b = 0.0
    
        # Define the stop zone shape, adjusting based on direction
        stop_points = [
            Point(x=-self.x_bound, y=self.y_upper_bound, z=0.0),  # Front-right corner
            Point(x=-self.x_bound, y=self.y_lower_bound, z=0.0),  # Front-left corner
            Point(x=-self.stop_threshold, y=self.y_lower_bound, z=0.0),  # Rear-left corner
            Point(x=-self.stop_threshold, y=self.y_upper_bound, z=0.0),  # Rear-right corner
            Point(x=-self.x_bound, y=self.y_upper_bound, z=0.0)   # Close the loop
        ]
        stop_marker.points = stop_points
        self.marker_publisher_.publish(stop_marker)
    
        # Slow-down zone marker
        slow_marker = Marker()
        slow_marker.header.frame_id = "base_link"
        slow_marker.header.stamp = self.get_clock().now().to_msg()
        slow_marker.ns = "slow_distance_polygon"
        slow_marker.id = 1
        slow_marker.type = Marker.LINE_STRIP
        slow_marker.action = Marker.ADD
        slow_marker.scale.x = 0.05
        slow_marker.color.a = 1.0
        slow_marker.color.r = 0.0
        slow_marker.color.g = 1.0
        slow_marker.color.b = 0.0
    
        # Define the slow-down zone shape, adjusting based on direction
        slow_points = [
            Point(x=-self.x_bound, y=self.y_upper_bound / 2, z=0.0),  # Front-right corner
            Point(x=-self.x_bound, y=self.y_lower_bound / 2, z=0.0),  # Front-left corner
            Point(x=-self.slow_down_threshold, y=self.y_lower_bound / 2, z=0.0),  # Rear-left corner
            Point(x=-self.slow_down_threshold, y=self.y_upper_bound / 2, z=0.0),  # Rear-right corner
            Point(x=-self.x_bound, y=self.y_upper_bound / 2, z=0.0)   # Close the loop
        ]
        slow_marker.points = slow_points
        self.marker_publisher_.publish(slow_marker)

        # Slow-down zone marker
        slow_marker_left = Marker()
        slow_marker_left.header.frame_id = "base_link"
        slow_marker_left.header.stamp = self.get_clock().now().to_msg()
        slow_marker_left.ns = "slow_distance_polygon_left"
        slow_marker_left.id = 2
        slow_marker_left.type = Marker.LINE_STRIP
        slow_marker_left.action = Marker.ADD
        slow_marker_left.scale.x = 0.05
        slow_marker_left.color.a = 1.0
        slow_marker_left.color.r = 1.0
        slow_marker_left.color.g = 0.0
        slow_marker_left.color.b = 1.0
    

        # Define the slow-down zone shape, adjusting based on direction
        slow_points = [
            Point(x=-self.x_bound, y=self.y_lower_bound, z=0.0),  # Front-right corner
            Point(x=-self.x_bound, y=(self.y_lower_bound / 2.0), z=0.0),  # Front-left corner
            Point(x=-self.slow_down_threshold + self.steering_offset, y=(self.y_lower_bound / 2.0), z=0.0),  # Rear-left corner
            Point(x=-self.slow_down_threshold + self.steering_offset, y=self.y_lower_bound, z=0.0),  # Rear-right corner
            Point(x=-self.x_bound, y=self.y_lower_bound, z=0.0)   # Close the loop
        ]
        slow_marker_left.points = slow_points
        self.marker_publisher_.publish(slow_marker_left)

        # Slow-down zone marker
        slow_marker_right = Marker()
        slow_marker_right.header.frame_id = "base_link"
        slow_marker_right.header.stamp = self.get_clock().now().to_msg()
        slow_marker_right.ns = "slow_distance_polygon"
        slow_marker_right.id = 3
        slow_marker_right.type = Marker.LINE_STRIP
        slow_marker_right.action = Marker.ADD
        slow_marker_right.scale.x = 0.05
        slow_marker_right.color.a = 1.0
        slow_marker_right.color.r = 1.0
        slow_marker_right.color.g = 0.0
        slow_marker_right.color.b = 1.0
    
        # Define the slow-down zone shape, adjusting based on direction
        slow_points = [
            Point(x=-self.x_bound, y=self.y_upper_bound, z=0.0),  # Front-right corner
            Point(x=-self.x_bound, y=self.y_upper_bound / 2, z=0.0),  # Front-left corner
            Point(x=-self.slow_down_threshold - self.steering_offset, y=self.y_upper_bound / 2, z=0.0),  # Rear-left corner
            Point(x=-self.slow_down_threshold - self.steering_offset, y=self.y_upper_bound, z=0.0),  # Rear-right corner
            Point(x=-self.x_bound, y=self.y_upper_bound, z=0.0)   # Close the loop
        ]
        slow_marker_right.points = slow_points
        self.marker_publisher_.publish(slow_marker_right)


def main(args=None):
    rclpy.init(args=args)
    
    node = StopNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Node stopped by user.')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()