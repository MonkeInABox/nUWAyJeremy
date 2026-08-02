"""Launch an example driver that communicates using TCP"""

from launch import LaunchDescription
import launch_ros.actions

from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    novatel_config = os.path.join(get_package_share_directory("master"), "config", "novatel.yaml")
    container = launch_ros.actions.ComposableNodeContainer(
        name='novatel_gps_container',
        namespace='',
        package='rclcpp_components',
        executable='component_container',
        composable_node_descriptions=[
            launch_ros.descriptions.ComposableNode(
                package='novatel_gps_driver',
                plugin='novatel_gps_driver::NovatelGpsNode',
                name='novatel_gps',
                parameters=[novatel_config]
            )
        ],
        output='screen'
    )

    return LaunchDescription([container])