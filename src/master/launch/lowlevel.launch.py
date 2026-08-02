import os

from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    pkg_share = get_package_share_directory("master")
    urdf = os.path.join(pkg_share, "urdf", "nuway.urdf.xml")
    params_file = LaunchConfiguration("params_file")

    with open(urdf, "r") as infp:
        robot_desc = infp.read()

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "params_file",
                default_value=os.path.join(pkg_share, "config", "sbg_params.yaml"),
                description="Full path to the ROS2 parameters file to use for all launched nodes",
            ),
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                parameters=[{"robot_description": robot_desc}],
                arguments=[urdf],
            ),
            # Node(
            #     package="sbg_driver",
            #     name="sbg_device",
            #     executable="sbg_device",
            #     output="screen",
            #     parameters=[params_file],
            # ),
        #    Node(
        #     package='python_nodes',
        #     executable='tbs_talker',
        #     name='tbs_talker',

            Node(
            package='python_nodes',
            executable='nuway_gps_tracker',
            name='nuway_gps_tracker',
            ),
        ]
    )
