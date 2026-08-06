import os
import yaml

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    pkg_directory = os.path.join(get_package_share_directory("master"))
    params = os.path.join(pkg_directory, "config", "velodyne.yaml")
    safetySickConfig = os.path.join(pkg_directory, "config", "sick_lms_1xx.yaml")
    config2 = os.path.join(pkg_directory, "config", "sick_params.yaml")
    share_dir = get_package_share_directory("velodyne_pointcloud")
    localisationSickConfig = os.path.join(pkg_directory, "config", "sick_ldmrs.yaml")
    pc2Config = os.path.join(pkg_directory, "config", "pc2_assembler.yaml")
    params_file = os.path.join(
        share_dir, "config", "VLP16-velodyne_transform_node-params.yaml"
    )
    with open(params_file, "r") as f:
        params2 = yaml.safe_load(f)["velodyne_transform_node"]["ros__parameters"]
    params2["calibration"] = os.path.join(share_dir, "params", "VLP16db.yaml")

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
                    ("encoder", "front_left/encoder"),
                    ("imu", "front_left/imu"),
                    ("scan", "front_left/scan"),
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
                    ("encoder", "front_right/encoder"),
                    ("imu", "front_right/imu"),
                    ("scan", "front_right/scan"),
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
                    ("encoder", "rear_right/encoder"),
                    ("imu", "rear_right/imu"),
                    ("scan", "rear_right/scan"),
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
                    ("encoder", "rear_left/encoder"),
                    ("imu", "rear_left/imu"),
                    ("scan", "rear_left/scan"),
                ],
                # arguments=['--ros-args', '--log-level', 'debug']
            ),
        # # localisation lidars
            Node(
                name="front",
                namespace="lidar_localisation",
                package="sick_scan_xd",
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
                package="sick_scan_xd",
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
            Node(
                package="velodyne_driver",
                executable="velodyne_driver_node",
                name="velodyne_driver_front",
                parameters=[params],
                remappings=[
                    ("velodyne_packets", "/lidar/velodyne/front/raw"),
                ],
            ),
            Node(
                package="velodyne_pointcloud",
                executable="velodyne_transform_node",
                name="velodyne_transform_front",
                parameters=[params2, params],
                remappings=[
                    ("velodyne_packets", "/lidar/velodyne/front/raw"),
                    ("velodyne_points", "/lidar/velodyne/front/cloud"),
                ],
            ),
            Node(
                package="velodyne_driver",
                executable="velodyne_driver_node",
                name="velodyne_driver_rear",
                parameters=[params],
                remappings=[
                    ("velodyne_packets", "/lidar/velodyne/rear/raw"),
                ],
            ),
            Node(
                package="velodyne_laserscan",
                executable="velodyne_laserscan_node",
                name="velodyne_laser_scan",
                parameters=[params],
                remappings=[
                    ("velodyne_points", "/lidar/velodyne/rear/cloud"),
                ],
            ),
            Node(
                package="velodyne_pointcloud",
                executable="velodyne_transform_node",
                name="velodyne_transform_rear",
                parameters=[params2, params],
                remappings=[
                    ("velodyne_packets", "/lidar/velodyne/rear/raw"),
                    ("velodyne_points", "/lidar/velodyne/rear/cloud"),
                ],
            ),
        ]
    )
    return ld


if __name__ == "__main__":
    generate_launch_description()
