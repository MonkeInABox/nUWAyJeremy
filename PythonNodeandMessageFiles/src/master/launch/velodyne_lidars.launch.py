import os
import yaml

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    pkg_directory = os.path.join(get_package_share_directory("master"))
    params = os.path.join(pkg_directory, "config", "velodyne.yaml")

    share_dir = get_package_share_directory("velodyne_pointcloud")

    params_file = os.path.join(
        share_dir, "config", "VLP16-velodyne_transform_node-params.yaml"
    )
    with open(params_file, "r") as f:
        params2 = yaml.safe_load(f)["velodyne_transform_node"]["ros__parameters"]
    params2["calibration"] = os.path.join(share_dir, "params", "VLP16db.yaml")

    ld = LaunchDescription(
        [
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
                package="velodyne_laserscan",
                executable="velodyne_laserscan_node",
                name="velodyne_laserscan_front",
                parameters=[params],
                remappings=[
                    ("velodyne_points", "/lidar/velodyne/front/cloud"),
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
                name="velodyne_laserscan_rear",
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
