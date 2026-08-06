from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os
import sys

def generate_launch_description():
    packageDirectory = get_package_share_directory('master')

    safetySickConfig = os.path.join(
        packageDirectory, 'config', 'sick_lms_1xx.yaml')
    
    ld = LaunchDescription([
        # lidar_safety
        Node(
            name="front_left",
            namespace="lidar_safety",
            package="sick_scan",
            executable="sick_generic_caller",
            parameters=[
                safetySickConfig,
                {"frame_id": "lidar_safety_front_left"},
                {"hostname": "192.168.5.11"},
            ],
            remappings=[
                ("cloud", "front_left/cloud"),
                ("encoder", "front_left/encoder"),
                ("imu", "front_left/imu"),
                ("scan", "front_left/scan"),
            ],
            #arguments=['--ros-args', '--log-level', 'debug'],
        ),

        Node(
            name="front_right",
            namespace="lidar_safety",
            package="sick_scan",
            executable="sick_generic_caller",
            parameters=[
                safetySickConfig,
                {"frame_id": "lidar_safety_front_right"},
                {"hostname": "192.168.5.12"},
            ],
            remappings=[
                ("cloud", "front_right/cloud"),
                ("encoder", "front_right/encoder"),
                ("imu", "front_right/imu"),
                ("scan", "front_right/scan"),
            ],
            #arguments=['--ros-args', '--log-level', 'debug'],
        ),

        Node(
            name="rear_right",
            namespace="lidar_safety",
            package="sick_scan",
            executable="sick_generic_caller",
            parameters=[
                safetySickConfig,
                {"frame_id": "lidar_safety_rear_right"},
                {"hostname": "192.168.5.13"},
            ],
            remappings=[
                ("cloud", "rear_right/cloud"),
                ("encoder", "rear_right/encoder"),
                ("imu", "rear_right/imu"),
                ("scan", "rear_right/scan"),
            ],
            #arguments=['--ros-args', '--log-level', 'debug'],
        ),

        Node(
            name="rear_left",
            namespace="lidar_safety",
            package="sick_scan",
            executable="sick_generic_caller",
            parameters=[
                safetySickConfig,
                {"frame_id": "lidar_safety_rear_left"},
                {"hostname": "192.168.5.14"},
            ],
            remappings=[
                ("cloud", "rear_left/cloud"),
                ("encoder", "rear_left/encoder"),
                ("imu", "rear_left/imu"),
                ("scan", "rear_left/scan"),
            ],
            #arguments=['--ros-args', '--log-level', 'debug']
        ),
    ])

    return ld