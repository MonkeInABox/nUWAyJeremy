from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    packageDirectory = get_package_share_directory("master")

    localisationSickConfig = os.path.join(packageDirectory, "config", "sick_ldmrs.yaml")
    config2 = os.path.join(packageDirectory, "config", "sickdocker container cp_params.yaml")
    pc2Config = os.path.join(packageDirectory, "config", "pc2_assembler.yaml")

    ld = LaunchDescription(
        [
            # # localisation lidars
            Node(
                name="front",
                namespace="lidar_localisation",
                package="sick_scan",
                executable="sick_generic_caller",
                # output="screen",
                parameters=[localisationSickConfig, config2],
                remappings=[
                    ("cloud", "front/cloud"),
                    ("objects", "front/objects"),
                ],
            ),
            Node(
                name="rear",
                namespace="lidar_localisation",
                package="sick_scan",
                executable="sick_generic_caller",
                # output="screen",
                parameters=[localisationSickConfig, config2],
                remappings=[
                    ("cloud", "rear/cloud"),
                    ("objects", "rear/objects"),
                ],
            ),
            Node(
                package="pointcloud2_assembler",
                name="pointcloud2_assembler",
                executable="pointcloud2_assembler",
                parameters=[pc2Config],
                remappings=[
                    ("cloud_merged", "/lidar/localisation_merged/cloud"),
                ],
            ),
            Node(
                package="pointcloud_to_laserscan",
                name="laserscan_converter",
                executable="pointcloud_to_laserscan_node",
                parameters=[pc2Config],
                remappings=[
                    ("cloud_in", "/lidar/localisation_merged/cloud"),
                    ("scan", "/lidar/localisation_merged/scan"),
                ],
            ),
        ]
    )

    return ld
