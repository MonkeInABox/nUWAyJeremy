from launch_ros.actions import Node

import launch
from launch import LaunchDescription


def generate_launch_description():
    ld = LaunchDescription(
        [
            Node(
                package="python_nodes",
                executable="safety_event_monitor",
                name="safety_event_monitor",
                output="screen",
                on_exit=launch.actions.Shutdown(),
                parameters=[{"min_dist": 3.0}],
            ),
            Node(
                package="python_nodes",
                executable="incident_recorder",
                name="incident_recorder",
                output="screen",
                on_exit=launch.actions.Shutdown()
                # parameters=[{'min_dist': 2.0}]
            ),
        ]
    )

    return ld
