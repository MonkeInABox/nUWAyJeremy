import rclpy
import can
import numpy
import time


from rclpy.callback_groups import MutuallyExclusiveCallbackGroup, ReentrantCallbackGroup
import rclpy.duration
from rclpy.executors import MultiThreadedExecutor
from enum import Enum

from rclpy.node import Node
from geometry_msgs.msg import Twist
from can.interface import Bus
from sensor_msgs.msg import Joy
from can_msgs.msg import Frame

from std_msgs.msg import Float32, Int32MultiArray, String, Int32, Float32MultiArray
# from python_nodes_interfaces.msg import BoolStamped, Int32Stamped, StringMultiArrayStamped

from rosbag2_interfaces.srv import Snapshot

from mppi_controller import MPPIController

MAX_LINEAR_VALUE = 5550 #5550
MAX_ANGULAR_VALUE = 0.28
RAD_PER_SEC = 0.29  # rad/s
# left is positive right is negative
CMD_MSG = 0x193
ESTOP_PCNAV_NOT_REQUESTED = 0x293  # 1 = no estop, 0 estop requested
ACCESORY_MSG = 0x214
HB_MSG = 0x293
# TODO: set as param
RAD_PER_FRAME = 0.004
SPEED_SCALE_FACTOR = -1000
ANGULAR_SCALE_FACTOR = 10000
WAIT_TIME = 100  # ms

#error codes
NAV_ESTOP = 1
NAV_ESTOP_TEXT = "PC ESTOP"
FL_LIDAR = 2
FL_LIDAR_TEXT = "Front Left Lidar triggered"
FR_LIDAR = 3
FR_LIDAR_TEXT = "Front Right Lidar triggered"
RL_LIDAR = 4
RL_LIDAR_TEXT = "Rear Left Lidar triggered"
RR_LIDAR = 5
RR_LIDAR_TEXT = "Rear Right Lidar triggered"
OBSTACLE_DETECTED = 6
OBSTACLE_DETECTED_TEXT = "Lidar Obstacle Detected"

DOOR_FATAL_ERROR = 7
DOOR_FATAL_ERROR_TEXT = "Door Fatal Error occured"
DOOR_UNAUTHORISED_ERROR = 8
DOOR_UNAUTHORISED_ERROR_TEXT = "Door did not authorise traction"
ESTOP_BUTTON_PUSHED_ERROR = 9
ESTOP_BUTTON_PUSHED_ERROR_TEXT = "Estop button has been pushed"
FRONT_STEERING_FAULT = 10
FRONT_STEERING_FAULT_TEXT = "Front steering controller faulted"
REAR_STEERING_FAULT = 11
REAR_STEERING_FAULT_TEXT = "Rear steering controller faulted"
BRAKE_CONTROLLER_FAULT = 12
BRAKE_CONTROLLER_FAULT_TEXT = "Brake controller faulted"
RAMP_UNAUTHORISED_ERROR = 13
RAMP_UNAUTHORISED_ERROR_TEXT = "Ramp not authorizing traction"
LOW_BATTERY_FAULT = 14
LOW_BATTERY_FAULT_TEXT = "Low battery soft stop"
AUTO_ESTOP = 15
AUTO_ESTOP_TEXT = "Automatic mode estop engaged"

# Buttons:

# X – 0
# circle – 1
# triangle -2
# square – 3
# L1 – 4
# R1 – 5
# L2 – 6
# R2 – 7
# select – 8
# start – 9
# ps button – 10
# left stick – 11
# right stick – 12

# Axes:
# d up – 7 (1)
# d down - 7 (-1)
# d left – 15
# d right - 16

class BUTTONS(Enum):
    X = 1
    L1 = 4
    L5 = 5


class CANBridge(Node):
    def __init__(self):
        super().__init__("minimal_subscriber")
        self.subscription = self.create_subscription(
            Twist, "gps_cmd_vel", self.listener_callback, 10
        )
        self.joy_subscription = self.create_subscription(
            Twist, "joy_cmd_vel", self.joy_listener_callback, 10
        )
        self.nn_subscription = self.create_subscription(
            Twist, "nn_cmd_vel", self.nn_listener_callback, 10
        )
        _joy_buttons_cb_group = ReentrantCallbackGroup()

        # TODO: Add as parameters
        can.rc["interface"] = "socketcan"
        can.rc["channel"] = "can0"
        can.rc["bitrate"] = 500000

        self.mode = 0
        self.mode_string = "Manual"
        self.joy_mode = True #inital in manual mode
        self.nav_mode = False 
        self.nn_mode_pullin = False
        self.nn_mode_lane = False
        self.nn_mode_pullout = False
        self.nn_mode_roundabout = False

        self.peripherals=0x00
        self.last_change = self.get_clock().now()
        # message filtering
        filters = [
            {"can_id": 0x206, "can_mask": 0xFFF, "extended": False},
            {"can_id": 0x194, "can_mask": 0xFFF, "extended": False},
            {"can_id": 0x294, "can_mask": 0xFFF, "extended": False},
            {"can_id": 0x394, "can_mask": 0xFFF, "extended": False},
            {"can_id": 0x580, "can_mask": 0xFFF, "extended": False},
            {"can_id": 0x193, "can_mask": 0xFFF, "extended": False},
            {"can_id": 0x214, "can_mask": 0xFFF, "extended": False},
            {"can_id": 0x293, "can_mask": 0xFFF, "extended": False},
        ]

        can.rc["can_filters"] = filters

        self.at_station = False
        self.frequency = 50
        self.bus = Bus()

        # initialization values
        self.last_angular = 0
        self.byte0 = 0x00
        self.byte3 = 0x40
        self.count = 0
        self.angular = 0.0
        self.speed = 0.0
        self.acceleration = 500
        self.nn_angular = 0.0
        self.nn_speed = 0.0
        self.joy_angular = 0.0
        self.joy_speed = 0.0
        self.speed_fb = 0.0
        self.front_steering_fb = 0.0
        self.rear_steering_fb = 0.0
        self.engaged = False
        self.hb_period=0.15
        self.hb_count=int(0.2/self.hb_period)
        # heartbeat management timer
        #self.timer_cb = self.create_timer(0.05, self._timer_cb)# 50ms
        self.timer_cb = self.create_timer(self.hb_period, self._timer_cb)# 10ms

        # can publisher
        self.can_timer = self.create_timer(1 / self.frequency, self._can_cb)

        # # can read Messages
        self.can_read_timer = self.create_timer(1 / 200, self._can_read_cb)

        self.publisher = self.create_publisher(Frame, 'candata', 10)

        self.speed_fb_pub = self.create_publisher(Float32, 'speed_fb', 10)
        self.front_steering_fb_pub = self.create_publisher(Float32, 'front_steering_fb', 10)
        self.rear_steering_fb_pub = self.create_publisher(Float32, 'rear_steering_fb', 10)

        self.accel_pub = self.create_publisher(Float32, 'accel_fb', 10)

        self.battery_pub = self.create_publisher(Float32, 'battery_voltage', 10)
        self.battery_percent_pub = self.create_publisher(Float32, 'battery_percent', 10)

        self.mode_pub = self.create_publisher(Int32, 'driving_mode', 10)
        self.mode_text_pub = self.create_publisher(String, 'driving_text_mode', 10)
        self.drive_cmd_pub = self.create_publisher(Float32MultiArray, 'drive_cmds', 10)

        # #0 is normal speed, 1 is high speed
        # self.speed_mode_pub = self.create_publisher(Int32Stamped, 'speed_mode_stamped', 10)
        self.speed_mode_disp_pub = self.create_publisher(Float32, 'speed_mode', 10)

        temp_msg = Int32()
        temp_msg.data = self.mode
        self.mode_pub.publish(temp_msg)

        temp_msg = String()
        temp_msg.data = self.mode_string
        self.mode_text_pub.publish(temp_msg)

        self.drive_enable = False
        self.gear=1 #1=forward steering 0=rear steering 2=both steering
        # self.gear_pub = self.create_publisher(Int32Stamped, 'gear_stamped', 10)
        self.gear_float_pub = self.create_publisher(Float32, 'gear_float', 10)
        
        # joystick subscriber
        self.joy_cb_subscription = self.create_subscription(
            Joy, "joy", self._joy_cb, 10
        )

        # self.snapshot_client = self.create_client(Snapshot, '/rosbag2_recorder/snapshot')
        # while not self.snapshot_client.wait_for_service(timeout_sec=1.0):
        #     self.get_logger().info('service not available, waiting again...')

        self.error_codes = []
        self.error_text = []
        self.fl_triggered = False
        self.fr_triggered = False
        self.rl_triggered = False
        self.rr_triggered = False
        self.nav_estop = False
        self.door_failure_triggered = False
        self.door_traction_unauthorized = False
        self.estop_button_pushed = False
        self.front_steering_fault = False
        self.rear_steering_fault = False
        self.brake_controller_fault = False
        self.ramp_traction_unauthorised = False
        self.low_battery_fault = False
        self.automatic_estop = False
        
        self.error_pub = self.create_publisher(Int32MultiArray, 'error_codes', 10)
        self.error_pub_disp = self.create_publisher(String, 'errorCodesDisp', 10)

        self.mppi = MPPIController(num_samples=10, horizon=5, lambda_=1.0, dt=0.02)

        # self.voice_subscription = self.create_subscription(
        #     StringMultiArrayStamped, "/speech_commands_stamped", self.voice_callback, 10
        # )

    # Used for speed and acceleration control
    def _can_cb(self):
        # Dead man switch held
        if self.drive_enable == True:
            # GPS mode
            if self.nav_mode:
                self.selected_speed=self.speed
                self.selected_angular=self.angular
            elif self.nn_mode_pullin or self.nn_mode_pullout or self.nn_mode_lane or self.nn_mode_roundabout:
                self.selected_speed=self.nn_speed
                self.selected_angular=self.nn_angular
            elif self.joy_mode:
                self.selected_speed=self.joy_speed
                self.selected_angular=self.joy_angular
            else:
                self.selected_speed = 0
                self.selected_angular = 0

            drive_cmds_msg = Float32MultiArray()
            drive_cmds_msg.data = [self.selected_speed, self.selected_angular]
            self.drive_cmd_pub.publish(drive_cmds_msg)
            
            speed_scaled = int(SPEED_SCALE_FACTOR * self.selected_speed)
            speed_scaled = max(min(speed_scaled, MAX_LINEAR_VALUE), -MAX_LINEAR_VALUE)
            speed_lsb = speed_scaled & 0xFF
            speed_msb = (speed_scaled >> 8) & 0xFF

            # self.acceleration = -0.5

            # if self.selected_speed > self.speed_fb and self.speed_fb > 0:
            #     self.acceleration = -0.5
            # elif self.selected_speed < self.speed_fb and self.speed_fb > 0:
            #     self.acceleration = 0.5
            # elif self.selected_speed < self.speed_fb and self.speed_fb < 0:
            #     self.acceleration = 0.5
            # elif self.selected_speed > self.speed_fb and self.speed_fb < 0:
            #     self.acceleration = -0.5

            # accel_lsb = self.acceleration & 0xFF
            # accel_msb = (self.acceleration >> 8) & 0xFF

            # self.get_logger().info(
            #     'speed_lsb: %s, speed_msb: %s' %
            #         (
            #             speed_lsb, 
            #             speed_msb
            #         )
            #     )

            # clamp angular max rates
            angular_target = max(min(self.selected_angular, MAX_ANGULAR_VALUE), -MAX_ANGULAR_VALUE)
            #angular_target = -angular_target
            # angular_target = self.angular
            # get the diff between current target and last sent value
            angular_diff = angular_target - self.last_angular

            # angular rate limiter
            angular_target = (
                self.last_angular + numpy.sign(angular_diff) * RAD_PER_FRAME
                if abs(angular_diff) > RAD_PER_FRAME
                else self.last_angular + angular_diff
            )

            self.get_logger().debug(
                f"speed_sign:{numpy.sign(self.speed)}\t\tangular_sign:{numpy.sign(self.angular)}\t\ttarget_sign:{numpy.sign(angular_target)}"
            )

            # update the last setn value
            angular_target = max(min(angular_target, MAX_ANGULAR_VALUE), -MAX_ANGULAR_VALUE)
            # self.get_logger().info(f"angular taget is: {angular_target}")
            self.last_angular = angular_target
            angular_scaled = int(ANGULAR_SCALE_FACTOR * angular_target)
            # if abs(self.speed_fb) <= 0.02:
            #     angular_scaled = 0
            

            # cmd_message = can.Message(
            #     data=[0, 0, speed_lsb, speed_msb, 0, 0, angular_lsb, angular_msb],
            #     arbitration_id=CMD_MSG,
            #     is_extended_id=False,
            # )

            # self.bus.send(cmd_message)

            # self.acceleration = 500

            if self.selected_speed > self.speed_fb and self.speed_fb > 0:
                self.acceleration = 300
            elif self.selected_speed < self.speed_fb and self.speed_fb > 0:
                self.acceleration = -1500
            elif self.selected_speed < self.speed_fb and self.speed_fb < 0:
                self.acceleration = -300
            elif self.selected_speed > self.speed_fb and self.speed_fb < 0:
                self.acceleration = 1500 #500 each before

            # self.acceleration = int(self.mppi.optimize(self.speed_fb, self.selected_speed) * -1000)
            
            print("Acceleration: ", self.acceleration)

            accel_lsb = self.acceleration & 0xFF
            accel_msb = (self.acceleration >> 8) & 0xFF

            if self.gear == 0:
                angular_scaled = -angular_scaled
                angular_lsb = angular_scaled & 0xFF
                angular_msb = (angular_scaled >> 8) & 0xFF
                cmd_message = can.Message(
                    data=[accel_lsb, accel_msb, speed_lsb, speed_msb, angular_lsb, angular_msb, 0, 0],
                    arbitration_id=CMD_MSG,
                    is_extended_id=False,
                )
                self.bus.send(cmd_message)
            elif self.gear == 1:
                angular_lsb = angular_scaled & 0xFF
                angular_msb = (angular_scaled >> 8) & 0xFF
                cmd_message = can.Message(
                    data=[accel_lsb, accel_msb, speed_lsb, speed_msb, 0, 0, angular_lsb, angular_msb],
                    arbitration_id=CMD_MSG,
                    is_extended_id=False,
                )
                self.bus.send(cmd_message)
            elif self.gear == 2:
                angular_lsb = angular_scaled & 0xFF
                angular_msb = (angular_scaled >> 8) & 0xFF
                reverse_angular_scaled = -angular_scaled
                reverse_angular_lsb = reverse_angular_scaled & 0xFF
                reverse_angular_msb = (reverse_angular_scaled >> 8) & 0xFF
                cmd_message = can.Message(
                    data=[accel_lsb, accel_msb, speed_lsb, speed_msb, reverse_angular_lsb, reverse_angular_msb, angular_lsb, angular_msb],
                    arbitration_id=CMD_MSG,
                    is_extended_id=False,
                )
                self.bus.send(cmd_message)
        
        else:
            drive_cmds_msg = Float32MultiArray()
            drive_cmds_msg.data = [0.0, 0.0]
            self.drive_cmd_pub.publish(drive_cmds_msg)
            
            self.selected_speed = 0
            speed_scaled = self.selected_speed
            speed_lsb = speed_scaled & 0xFF
            speed_msb = (speed_scaled >> 8) & 0xFF


            self.selected_angular = 0

            # clamp angular max rates
            angular_target = max(min(self.selected_angular, MAX_ANGULAR_VALUE), -MAX_ANGULAR_VALUE)
            #angular_target = -angular_target
            # angular_target = self.angular
            # get the diff between current target and last sent value
            angular_diff = angular_target - self.last_angular

            # angular rate limiter
            angular_target = (
                self.last_angular + numpy.sign(angular_diff) * RAD_PER_FRAME
                if abs(angular_diff) > RAD_PER_FRAME
                else self.last_angular + angular_diff
            )

            # update the last setn value
            angular_target = max(min(angular_target, MAX_ANGULAR_VALUE), -MAX_ANGULAR_VALUE)
            # self.get_logger().info(f"angular taget is: {angular_target}")
            self.last_angular = angular_target
            angular_scaled = int(ANGULAR_SCALE_FACTOR * angular_target)
            angular_lsb = angular_scaled & 0xFF
            angular_msb = (angular_scaled >> 8) & 0xFF

            # self.get_logger().info('gear mode is: {0}'.format(self.gear))
            self.acceleration = -5

            if self.speed_fb > 0:
                self.acceleration = 5

            accel_lsb = self.acceleration & 0xFF
            accel_msb = (self.acceleration >> 8) & 0xFF

            self.acceleration = -500

            if self.speed_fb > 0:
                self.acceleration = 500


            accel_lsb = self.acceleration & 0xFF
            accel_msb = (self.acceleration >> 8) & 0xFF

            if self.gear == 0:
                angular_scaled = -angular_scaled
                angular_lsb = angular_scaled & 0xFF
                angular_msb = (angular_scaled >> 8) & 0xFF
                cmd_message = can.Message(
                    data=[accel_lsb, accel_msb, speed_lsb, speed_msb, angular_lsb, angular_msb, 0, 0],
                    arbitration_id=CMD_MSG,
                    is_extended_id=False,
                )
                self.bus.send(cmd_message)
            elif self.gear == 1:
                angular_lsb = angular_scaled & 0xFF
                angular_msb = (angular_scaled >> 8) & 0xFF
                cmd_message = can.Message(
                    data=[accel_lsb, accel_msb, speed_lsb, speed_msb, 0, 0, angular_lsb, angular_msb],
                    arbitration_id=CMD_MSG,
                    is_extended_id=False,   
                )
                self.bus.send(cmd_message)
            elif self.gear == 2:
                reverse_angular_scaled = -angular_scaled
                reverse_angular_lsb = reverse_angular_scaled & 0xFF
                reverse_angular_msb = (reverse_angular_scaled >> 8) & 0xFF
                cmd_message = can.Message(
                    data=[accel_lsb, accel_msb, speed_lsb, speed_msb, reverse_angular_lsb, reverse_angular_msb, angular_lsb, angular_msb],
                    arbitration_id=CMD_MSG,
                    is_extended_id=False,
                )
                self.bus.send(cmd_message)

            # Return to manual mode if driving no longer engaged
            self.changeMode(self.mode, 0)


    def changeMode(self, currentMode, newMode):
        if currentMode == 0:
            self.joy_mode = False
        elif currentMode == 1:
            self.nav_mode = False
        elif currentMode == 2:
            self.nn_mode_lane = False
        elif currentMode == 3:
            self.nn_mode_pullin = False
        elif currentMode == 4:
            self.nn_mode_pullout = False
        elif currentMode == 5:
            self.nn_mode_roundabout = False

        if newMode == 0:
            self.joy_mode = True
            self.mode_string = "Manual"
        elif newMode == 1:
            self.nav_mode = True
            self.mode_string = "GPS"
        elif newMode == 2:
            self.nn_mode_lane = True
            self.mode_string = "NN Lane Following"
        elif newMode == 3:
            self.nn_mode_pullin = True
            self.mode_string = "NN Pullin"
        elif newMode == 4:
            self.nn_mode_pullout = True
            self.mode_string = "NN Pullout"
        elif newMode == 5:
            self.nn_mode_roundabout = True
            self.mode_string = "NN Turn Around"

        # print("self mode was: ", self.mode)
        self.mode = newMode
        # print("self mode is now: ", self.mode)
        
    
    def _joy_cb(self, msg):
        if msg.buttons[0]:
            self.changeMode(self.mode, 2)
            # self.get_logger().info("X pressed!")
            # pedestrian alert 0x214.0.4
            # self.bus.send(
            #     can.Message(
            #         data=[0b00010000], arbitration_id=ACCESORY_MSG, is_extended_id=False
            #     )
            # )

            # time.sleep(1 / 100)

            # self.bus.send(
            #     can.Message(data=[0], arbitration_id=ACCESORY_MSG, is_extended_id=False)
            # )
        
        if msg.buttons[1]:
            # self.get_logger().info("circle pressed!")
            # self.get_logger().info("Switch to Manual!")
            self.changeMode(self.mode, 5)
            # self.nav_mode=False
            # self.nn_mode=False
            # command doors 0x214.0.0-1
            # self.bus.send(
            #     can.Message(
            #         data=[1],
            #         arbitration_id=ACCESORY_MSG,
            #         is_extended_id=False,
            #     )
            # )
            # time.sleep(0.1)
            # self.bus.send(
            #     can.Message(
            #         data=[0],
            #         arbitration_id=ACCESORY_MSG,
            #         is_extended_id=False,
            #     )
            # )
            # self.hb_message[1] = 1

        if msg.buttons[2]:
            # self.get_logger().info("triangle pressed!")
            self.changeMode(self.mode, 4)
             # self.get_logger().info("Switch to Nav!")
             # self.nav_mode=True
             # self.nn_mode=False
             # rearm

        
        if msg.buttons[3]:
            # self.get_logger().info("square pressed!")
            # self.get_logger().info("Switch to NN!")
            # self.nav_mode=False
            # self.nn_mode=True
            self.changeMode(self.mode, 3)
            # stop at station 0x214.0.2
            # if self.at_station:

            #     self.at_station = False
            #     self.bus.send(
            #         can.Message(
            #             data=[0],
            #             arbitration_id=ACCESORY_MSG,
            #             is_extended_id=False,
            #         )
            #     )
            # else:
            #     self.at_station = True
            #     self.bus.send(
            #         can.Message(
            #             data=[4],
            #             arbitration_id=ACCESORY_MSG,
            #             is_extended_id=False,
            #         )
            #     )

        if msg.buttons[4]:
            # self.get_logger().info("L1 pressed!")
            self.changeMode(self.mode, 1)

        if msg.buttons[5]:
            # self.get_logger().info("ESTOP!")
            # self.get_logger().info("R1 prssed!")
            self.changeMode(self.mode, 0)
            # 0x293.0.7 1 = no estop, 0 estop requested
            # self.bus.send(
            #     can.Message(
            #         data=[0b00000000],
            #         arbitration_id=ESTOP_PCNAV_NOT_REQUESTED,
            #         is_extended_id=False,
            #     )
            # )

            # time.sleep(WAIT_TIME)

            # self.bus.send(
            #     can.Message(
            #         data=[0b10000000],
            #         arbitration_id=ESTOP_PCNAV_NOT_REQUESTED,
            #         is_extended_id=False,
            #     )
            # )

        if msg.buttons[6] or msg.buttons[7]:
            self.drive_enable = True
        else:
            self.drive_enable = False

        if msg.buttons[7]:
            # msg_new = Int32Stamped()
            msg_new2 = Float32()
            # msg_new.data = 1
            msg_new2.data = 1.0
            # msg_new.header.stamp = self.get_clock().now().to_msg()
            # self.speed_mode_pub.publish(msg_new)
            self.speed_mode_disp_pub.publish(msg_new2)
        else:
            # msg_new = Int32Stamped()
            msg_new2 = Float32()
            # msg_new.data = 0
            msg_new2.data = 0.0
            # msg_new.header.stamp = self.get_clock().now().to_msg()
            # self.speed_mode_pub.publish(msg_new)
            self.speed_mode_disp_pub.publish(msg_new2)
            
        
        msg_mode = Int32()
        msg_mode.data = self.mode
        self.mode_pub.publish(msg_mode)

        msg_string_mode = String()
        msg_string_mode.data = self.mode_string
        self.mode_text_pub.publish(msg_string_mode)

        if (self.front_steering_fb == 0.0 and self.rear_steering_fb == 0.0):
            if msg.axes[7] == 1:
                print("up d pressed")
                self.gear=0
                # self.get_logger().info("duration is %s" % (self.get_clock().now().nanoseconds - self.last_change.nanoseconds))
                if ((self.get_clock().now().nanoseconds - self.last_change.nanoseconds) > 500000000):
                    if (self.peripherals&0x04)==0x04:
                        self.peripherals = self.peripherals & 0xFB
                    else:
                        self.peripherals = self.peripherals | 0x04
                    self.last_change = self.get_clock().now()
                
            if msg.axes[7] == -1:
                print("down d pressed")
                self.gear=1
                # self.get_logger().info((self.get_clock().now().nanoseconds - self.last_change.nanoseconds))
                if ((self.get_clock().now().nanoseconds - self.last_change.nanoseconds) > 500000000):
                    if (self.peripherals&0x06)==0x06:
                        self.peripherals = self.peripherals & 0xBF
                    else:
                        self.peripherals = self.peripherals | 0x40
                    self.last_change = self.get_clock().now()

            if msg.axes[6] == -1:
                print("right d pressed")
                self.gear=2

        # gear_msg = Int32Stamped()
        gear_float_msg = Float32()
        # gear_msg.data = self.gear
        gear_float_msg.data = float(self.gear)
        # gear_msg.header.stamp = self.get_clock().now().to_msg()
        # self.gear_pub.publish(gear_msg)
        self.gear_float_pub.publish(gear_float_msg)
        # if msg.buttons[13]:
        #     print("up d pressed")
        #     # pedestrian alert 0x214.0.4
        #     self.bus.send(
        #         can.Message(
        #             data=[0b00010000], arbitration_id=0x214, is_extended_id=False
        #         )
        #     )

        #     self.bus.send(
        #         can.Message(
        #             data=[0b00000000], arbitration_id=0x214, is_extended_id=False
        #         )
        #     )

    def _timer_cb(self):
        # self.byte0 = self.byte0 | 0x01 if self.count<(self.hb_count/2) else self.byte0 & 0xFE
        self.byte0 = self.byte0 | 0x01 if ((self.byte0 & 0x01) == 0) else self.byte0 & 0xFE

        # self.count = (self.count + 1) % self.hb_count

        self.byte0 = self.byte0 | 0x80

        hb_message = can.Message(
            data=[self.peripherals, 128, self.byte0, self.byte3, 0, 0, 0, 0],
            arbitration_id=HB_MSG,
            is_extended_id=False,
        )
        self.bus.send(hb_message)

    def _send_accessory_msg(self, byte, bit):
        # WIP - need to figure out how to send the correct message
        value = pow(2, bit)
        hex_value = hex(value)
        final_value = hex_value | 0x00

        self.bus.send(
            can.Message(
                data=[1],
                arbitration_id=ACCESORY_MSG,
                is_extended_id=False,
            )
        )
        time.sleep(0.1)
        self.bus.send(
            can.Message(
                data=[0],
                arbitration_id=ACCESORY_MSG,
                is_extended_id=False,
            )
        )

    def listener_callback(self, msg):
        self.speed = -msg.linear.x
        self.angular = msg.angular.z if msg.linear.x < 0 else -msg.angular.z
    
    def joy_listener_callback(self, msg):
        self.joy_speed = msg.linear.x
        self.joy_angular = -msg.angular.z if msg.linear.x < 0 else msg.angular.z

    def nn_listener_callback(self, msg):
        self.nn_speed = msg.linear.x
        self.nn_angular = -msg.angular.z if msg.linear.x < 0 else msg.angular.z

    def voice_callback(self, msg):
        if self.joy_mode or self.nav_mode:
            return

        if len(msg.action_commands) != 0:
            action = msg.action_commands[0]

            if action == 'turn':
                if len(msg.direction_commands) != 0:
                    if msg.direction_commands[0] == 'left':
                        self.changeMode(self.mode, 3)
                        return
                    if msg.direction_commands[0] == 'right':
                        self.changeMode(self.mode, 3)
                        return
                else:
                    return
                
            if action == 'pullin' or action == 'park':
                self.changeMode(self.mode, 3)
                return

            if action == 'pullout':
                self.changeMode(self.mode, 4)
                return

            if action == 'stop':
                self.changeMode(self.mode, 0)
                return

            if action == 'turn around':
                if len(msg.tertiary_commands) != 0:
                    if 'round about' in msg.tertiary_commands:
                        self.changeMode(self.mode, 5)
                        return


    def _can_read_cb(self):
        msg = self.bus.recv()

        if msg != None:
            self.publish_message(msg)

            if msg.arbitration_id == 0x206:
                # speed_fb_lsb = msg.data[0]
                # speed_fb_msb = msg.data[1]
                speed_fb = (msg.data[1]<<8|msg.data[0])
                if msg.data[1] >= 0x80:
                    speed_fb -= 0x10000
                speed_fb = float(speed_fb) * 0.001
                speed_fb = -speed_fb
                self.speed_fb = speed_fb

                front_steering_fb = (msg.data[3]<<8|msg.data[2])
                if msg.data[1] >= 0x80:
                    front_steering_fb -= 0x10000
                front_steering_fb = float(front_steering_fb) * 0.001
                if front_steering_fb < -5.0 or front_steering_fb > 5.0:
                    front_steering_fb = 0.0
                self.front_steering_fb = front_steering_fb

                rear_steering_fb = (msg.data[5]<<8|msg.data[4])
                if msg.data[1] >= 0x80:
                    rear_steering_fb -= 0x10000
                rear_steering_fb = float(rear_steering_fb) * 0.001
                if rear_steering_fb < -5.0 or front_steering_fb > 5.0:
                    rear_steering_fb = 0.0
                self.rear_steering_fb = rear_steering_fb

                # self.get_logger().info('speed_msb: %#X, speed_lsb: %#X, speed: %s' %
                #         (
                #             speed_fb_msb,
                #             speed_fb_lsb,
                #             speed_fb
                #         )
                # )
                msg1 = Float32()
                msg2 = Float32()
                msg3 = Float32()
                msg4 = Float32()
                msg1.data = speed_fb
                msg2.data = front_steering_fb
                msg3.data = rear_steering_fb
                msg4.data = float(self.acceleration)
                self.speed_fb_pub.publish(msg1)
                self.front_steering_fb_pub.publish(msg2)
                self.rear_steering_fb_pub.publish(msg3)
                self.accel_pub.publish(msg4)

            if msg.arbitration_id == 0x580:
                batteryVoltage = (msg.data[3]<<8|msg.data[2])
                batteryVoltage = float(batteryVoltage) * 0.01

                batteryPercent = float(msg.data[5])

                msg1 = Float32()
                msg1.data = batteryVoltage
                self.battery_pub.publish(msg1)

                msg2 = Float32()
                msg2.data = batteryPercent
                self.battery_percent_pub.publish(msg2)

            if msg.arbitration_id == 0x194:
            #    if (msg.data[4]&0x40 == 0x00 and self.engaged == True):
            #        snapshot_req = Snapshot.Request()
            #        self.future = self.snapshot_client.call_async(snapshot_req)
            #     #    rclpy.spin_until_future_complete(self, self.future)
            #        while(self.future.result() == False):
            #            self._timer_cb()
                       
            #         #        self.future = self.snapshot_client.call_async(snapshot_req)
            #         #        rclpy.spin_until_future_complete(self, self.future)

            #        self.engaged = False
            #        self.get_logger().info("Snapshot has captured incident")

            #    elif (msg.data[4]&0x40 == 0x40 and not self.engaged):
            #        self.engaged = True
            #        self.get_logger().info("Snapshot has been enabled")
            #        self.error_codes.clear()
            #        self.error_text.clear()
            #        self.fl_triggered = False
            #        self.fr_triggered = False
            #        self.rr_triggered = False
            #        self.rl_triggered = False
            #        self.nav_estop = False
            #        self.door_failure_triggered = False
            #        self.door_traction_unauthorized = False
            #        self.estop_button_pushed = False

               if (msg.data[0]&0x08 == 0x00 and not self.fl_triggered):
                   self.error_codes.append(FL_LIDAR)
                   self.error_text.append(FL_LIDAR_TEXT)
                   self.get_logger().info("Front left lidar triggered enabled")
                   self.fl_triggered = True

               if ((msg.data[0]&0x04) == 0x00 and not self.fr_triggered):
                   self.error_codes.append(FR_LIDAR)
                   self.error_text.append(FR_LIDAR_TEXT)
                   self.get_logger().info("Front right lidar triggered enabled")
                   self.fr_triggered = True

               if (msg.data[0]&0x02 == 0x00 and not self.rl_triggered):
                   self.error_codes.append(RL_LIDAR)
                   self.error_text.append(RL_LIDAR_TEXT)
                   self.get_logger().info("Rear left lidar triggered enabled")
                   self.rl_triggered = True

               if (msg.data[0]&0x01 == 0x00 and not self.rr_triggered):
                   self.error_codes.append(RR_LIDAR)
                   self.error_text.append(RR_LIDAR_TEXT)
                   self.get_logger().info("Rear right lidar triggered enabled")
                   self.rr_triggered = True

               if (msg.data[1]&0x08 == 0x08 and not self.door_failure_triggered):
                   self.error_codes.append(DOOR_FATAL_ERROR)
                   self.error_text.append(DOOR_FATAL_ERROR_TEXT)
                   self.get_logger().info("Door Fatal Failure triggered")
                   self.door_failure_triggered = True

               if (msg.data[1]&0x40 == 0x40 and not self.door_traction_unauthorized):
                   self.error_codes.append(DOOR_UNAUTHORISED_ERROR)
                   self.error_text.append(DOOR_UNAUTHORISED_ERROR_TEXT)
                   self.get_logger().info("Door not authorizing traction")
                   self.door_traction_unauthorized = True

               if (msg.data[2]&0x01 == 0x00 and not self.estop_button_pushed):
                   self.error_codes.append(ESTOP_BUTTON_PUSHED_ERROR)
                   self.error_text.append(ESTOP_BUTTON_PUSHED_ERROR_TEXT)
                   self.get_logger().info("Estop button has been pushed")
                   self.estop_button_pushed = True

               if (msg.data[3]&0x01 == 0x00 and not self.front_steering_fault):
                   self.error_codes.append(FRONT_STEERING_FAULT)
                   self.error_text.append(FRONT_STEERING_FAULT_TEXT)
                   self.get_logger().info("Front steering controller faulted")
                   self.front_steering_fault = True

               if (msg.data[3]&0x01 == 0x00 and not self.rear_steering_fault):
                   self.error_codes.append(REAR_STEERING_FAULT)
                   self.error_text.append(REAR_STEERING_FAULT_TEXT)
                   self.get_logger().info("Rear steering controller faulted")
                   self.rear_steering_fault = True

               if (msg.data[3]&0x01 == 0x00 and not self.brake_controller_fault):
                   self.error_codes.append(BRAKE_CONTROLLER_FAULT)
                   self.error_text.append(BRAKE_CONTROLLER_FAULT_TEXT)
                   self.get_logger().info("Brake controller faulted")
                   self.brake_controller_fault = True

               if (msg.data[5]&0x10 == 0x10 and not self.ramp_traction_unauthorised):
                   self.error_codes.append(RAMP_UNAUTHORISED_ERROR)
                   self.error_text.append(RAMP_UNAUTHORISED_ERROR_TEXT)
                   self.get_logger().info("Ramp not authorizing traction")
                   self.ramp_traction_unauthorised = True

               if (msg.data[6]&0x80 == 0x80 and not self.low_battery_fault):
                   self.error_codes.append(LOW_BATTERY_FAULT)
                   self.error_text.append(LOW_BATTERY_FAULT_TEXT)
                   self.get_logger().info("Low battery soft stop")
                   self.low_battery_fault = True

            if msg.arbitration_id == 0x294 and ((msg.data[3]&0x10) == 0x10) and not self.automatic_estop:
                self.error_codes.append(AUTO_ESTOP)
                self.error_text.append(AUTO_ESTOP_TEXT)
                self.get_logger().info("Automatic mode estop engaged")
                self.automatic_estop = True
                
            if msg.arbitration_id == 0x394 and ((msg.data[5]&0b10000000) == 0b00000000) and not self.nav_estop:
                self.error_codes.append(NAV_ESTOP)
                self.error_text.append(NAV_ESTOP_TEXT)
                self.get_logger().info("PC ESTOP engaged")
                self.nav_estop = True
            
            msg_error = Int32MultiArray()
            msg_error.data = self.error_codes
            self.error_pub.publish(msg_error)


            if (len(self.error_text) != 0):
                errorCodeDisp = "Current error codes: "
                # self.get_logger().info("printing Error Codes")
                for x in self.error_text:
                    errorCodeDisp += x + ", "

                msg_error_disp = String()
                msg_error_disp.data = errorCodeDisp
                self.error_pub_disp.publish(msg_error_disp)
            
            # open door code
            if msg.arbitration_id == 0x194:
                if (msg.data[4]&0b00000010) == 0b00000010:
                    self.byte0 = self.byte0|0b00000100
                else:
                    self.byte0 = self.byte0&0b11111011

    def publish_message(self, msg):
        # convert can.Message to can_msgs/Frame
        # print("before", len(msg.data))

        data = msg.data + b'0' * (8 - len(msg.data))
        # print("after", len(data))
        #print(msg.arbitration_id)
        # if msg.arbitration_id == int('185',16):
        #     print("fsteer msg")
        
        # TODO: Find out why passing is_extended/is_error/is_rtr
        # doesn't work within this constructor
        out = Frame(
            id = msg.arbitration_id,
            # is_rtr = msg.is_remote_frame,
            # is_extended = msg.is_extended_id,
            # is_error = msg.is_error_frame,
            dlc = msg.dlc,
            data = data,
            )
        
        out.header.stamp=self.get_clock().now().to_msg()

        self.publisher.publish(out)
        # self.get_logger().info('Publishing CAN msg: "%s"' % out.data) # DEBUG


def main(args=None):
    rclpy.init(args=args)

    can_bridge = CANBridge()
    executor = MultiThreadedExecutor(num_threads=6)
    executor.add_node(can_bridge)
    # rclpy.spin(minimal_subscriber)
    executor.spin()
    executor.shutdown()
    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    can_bridge.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
