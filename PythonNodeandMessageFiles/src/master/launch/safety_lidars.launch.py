import os

from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node

from launch import LaunchDescription


def generate_launch_description():
    pkg_share = get_package_share_directory("master")

    safetySickConfig = os.path.join(pkg_share, "config", "sick_lms_1xx.yaml")
    config2 = os.path.join(pkg_share, "config", "sick_params.yaml")

    ld = LaunchDescription(
        [
            # lidar_safety
            Node(
                name="front_left",
                namespace="lidar_safety",
                package="sick_scan_xd",
                executable="sick_generic_caller",
                parameters=[safetySickConfig, config2],
                remappings=[
                    ("cloud", "front_left/cloud"),
                    ("sick_lms_1xx/encoder", "front_left/encoder"),
                    ("sick_lms_1xx/imu", "front_left/imu"),
                    ("sick_lms_1xx/scan", "front_left/scan"),
                ],
                # arguments=['--ros-args', '--log-level', 'debug'],
            ),
            Node(
                name="front_right",
                namespace="lidar_safety",
                package="sick_scan_xd",
                executable="sick_generic_caller",
                parameters=[safetySickConfig, config2],
                remappings=[
                    ("cloud", "front_right/cloud"),
                    ("sick_lms_1xx/encoder", "front_right/encoder"),
                    ("sick_lms_1xx/imu", "front_right/imu"),
                    ("sick_lms_1xx/scan", "front_right/scan"),
                ],
                # arguments=['--ros-args', '--log-level', 'debug'],
            ),
            Node(
                name="rear_right",
                namespace="lidar_safety",
                package="sick_scan_xd",
                executable="sick_generic_caller",
                parameters=[safetySickConfig, config2],
                remappings=[
                    ("cloud", "rear_right/cloud"),
                    ("sick_lms_1xx/encoder", "rear_right/encoder"),
                    ("sick_lms_1xx/imu", "rear_right/imu"),
                    ("sick_lms_1xx/scan", "rear_right/scan"),
                ],
                # arguments=['--ros-args', '--log-level', 'debug'],
            ),
            Node(
                name="rear_left",
                namespace="lidar_safety",
                package="sick_scan_xd",
                executable="sick_generic_caller",
                parameters=[safetySickConfig, config2],
                remappings=[
                    ("cloud", "rear_left/cloud"),
                    ("sick_lms_1xx/encoder", "rear_left/encoder"),
                    ("sick_lms_1xx/imu", "rear_left/imu"),
                    ("sick_lms_1xx/scan", "rear_left/scan"),
                ],
                # arguments=['--ros-args', '--log-level', 'debug']
            ),
        ]
    )

    return ld
