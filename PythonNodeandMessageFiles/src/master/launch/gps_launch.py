# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch_ros.actions import LifecycleNode, Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from nav2_common.launch import RewrittenYaml

import os


def generate_launch_description():
    pkg_share = get_package_share_directory("master")

    autostart = LaunchConfiguration("autostart")
    params = LaunchConfiguration("params_file")

    param_substitutions = {
        "autostart": autostart,
    }

    configured_params = RewrittenYaml(
        source_file=params, param_rewrites=param_substitutions, convert_types=True
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "autostart",
                default_value="True",
                description="Automatically startup GPS server node",
            ),
            DeclareLaunchArgument(
                "params_file",
                default_value=os.path.join(pkg_share, "config/ekfs_params.yaml"),
                description="Parameter file for RL nodes",
            ),
            Node(
                package="robot_localization",
                executable="navsat_transform_node",
                name="navsat_transform",
                output="screen",
                parameters=[configured_params],
                remappings=[
                    ("imu", "imu/data"),
                    ("gps/fix", "imu/nav_sat_fix"),
                    ("gps/filtered", "gps/filtered"),
                    ("odometry/gps", "odometry/gps"),
                    ("odometry/filtered", "odometry/global"),
                ],
            ),
            Node(
                package="python_nodes",
                executable="gps_location2",
                name="gps_location2",
            ),
            # ! GLOBAL EKF NODE
            Node(
                package="robot_localization",
                executable="ekf_node",
                name="ekf_filter_node_map",
                output="screen",
                parameters=[configured_params],
                remappings=[
                    ("odometry/filtered", "odometry/global"),
                    ("/set_pose", "/initialpose"),
                ],
            ),
            # # ! LOCAL EKF NODE
            # Node(
            #     package="robot_localization",
            #     executable="ekf_node",
            #     name="ekf_filter_node_odom",
            #     output="screen",
            #     parameters=[configured_params],
            #     remappings=[
            #         ("odometry/filtered", "odometry/local"),
            #         ("/set_pose", "/initialpose"),
            #     ],
            # ),

            
        ]
    )
