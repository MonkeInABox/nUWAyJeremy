import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory("master")
    config = os.path.join(pkg_share, "config", "sbg_params.yaml")
    return LaunchDescription(
        [
            Node(
                package="sbg_driver",
                name="sbg_device",
                executable="sbg_device",
                output="screen",
                parameters=[config],
            )
        ]
    )
