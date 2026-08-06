#######################
# Author: Lemar Haddad
# Version: 02.02.22
# ---------------------
# Acts on a trigger to begin a rosbag recording
# of Camera and LiDAR data for an 'incident'.
#######################

import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from geometry_msgs.msg import Twist
import time
import subprocess
import signal
import libtmux


class IncidentRecorder(Node):

    def __init__(self):
        super().__init__('incident_recorder')
        self.subscription = self.create_subscription(
            String,
            'safety_event_flag',
            self.listener_callback,
            4)
        self.subscription  # prevent unused variable warning

        self.server = libtmux.Server()
        try:
            s = self.server.kill_session("incident_recorder")
            self.get_logger().info("Killing previous tmux session...")
        except Exception:
            self.get_logger().info("No previous tmux sessions...")
            pass
        finally:
            self.get_logger().info("Starting new tmux session...")
            self.main_session = self.server.new_session(
                session_name="incident_recorder"
            )

        self.window = self.main_session.new_window(attach=False, window_name="win1")
        self.pane = self.window.select_pane(0)
        self.pane.send_keys("cd /home/uwara/ShuttleBusData/BaseDrive/", enter=True)

        self.cmd_vel_ts = None
        self.cmdvel_subscription = self.create_subscription(
            Twist,
            'cmd_vel',
            self.cmd_vel_received,
            4)

        self.eventTrigger = False # if true, records rosbag
        self.rosbagPID = None
        self.time_elapsed = time.time()
        self.timer = self.create_timer(1.0, self.rosbag_recorder)

    def cmd_vel_received(self, msg):
        self.cmd_vel_ts = time.time()

    def listener_callback(self, msg):
        if msg.data == "True":
            self.eventTrigger = True
        else:
            self.eventTrigger = False
    
    def stop_recorder(self):
        self.pane.send_keys('C-c', enter=False, suppress_history=False)

    def rosbag_recorder(self):
        if self.cmd_vel_ts == None:
            # dont record unless autonomous driving
            return False
        # if we don't have a rosbag currently being
        # recorded but do have an event trigger
        # start a new rosbag recording
        if not self.rosbagPID and self.eventTrigger:
            if time.time() - self.cmd_vel_ts >= 200:
                # dont record unless autonomous driving has happened recently
                return False
            # 'source',
            # '/opt/ros/foxy/setup.bash',
            # 'source',
            # '~/nuway_ros2_ws/install/setup.bash',
            self.get_logger().info("Starting incident recording...")
            # self.rosbagPID = subprocess.Popen(
            #     [
            #         'ros2',
            #         'bag',
            #         'record',
            #         '/Camera0',
            #         '/lidar/localisation_merged/scan'
            #     ],
            #     cwd="/home/uwara/ShuttleBusData/BaseDrive/",
            #     shell=False
            # )
            self.rosbagPID = self.pane
            self.pane.send_keys("ros2 bag record /CameraFront /CameraRear /lidar/localisation_merged/scan")
            self.get_logger().info("Incident recording started.")
            self.time_elapsed = time.time()
        # if we do have a rosbag currently being recorded
        # and a new event trigger has arrived,
        # reset the timer and continue recording.
        elif self.rosbagPID and self.eventTrigger:
            self.time_elapsed = time.time()
            self.get_logger().info("Incident recording continuing...")
        # if we do have a rosbag currently being recorded
        # and 5 seconds have elapsed since the last
        # event trigger, stop the rosbag recording.
        elif self.rosbagPID and \
            (time.time() - self.time_elapsed) >= 6:
            self.get_logger().info("Stopping incident recording...")
            # self.rosbagPID.send_signal(signal.SIGINT)
            self.pane.send_keys('C-c', enter=False, suppress_history=False)
            # self.wait()
            # self.rosbagPID.terminate()
            # self.rosbagPID.communicate()
            self.rosbagPID = None
            self.get_logger().info("Incident saved.")


            


def main(args=None):
    rclpy.init(args=args)

    incident_recorder = IncidentRecorder()
    try:
        rclpy.spin(incident_recorder)
    except KeyboardInterrupt:
        pass

    
    incident_recorder.stop_recorder()

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    incident_recorder.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
