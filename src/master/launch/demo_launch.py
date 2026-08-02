import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from nav2_common.launch import RewrittenYaml


def generate_launch_description():
    pkg_share = get_package_share_directory("master")
    launch_dir = os.path.join(pkg_share, "launch")

    basic_mobile_robot = get_package_share_directory("basic_mobile_robot")
    basic_launch_dir = os.path.join(basic_mobile_robot, "launch")

    gps_wpf = get_package_share_directory("gps_waypoint_follower")
    gps_launch_dir = os.path.join(gps_wpf, "launch")

    nav2_params = LaunchConfiguration("nav2_params")
    gps_params = LaunchConfiguration("gps_params")
    map_yaml_file = LaunchConfiguration("map")

    use_sim_time = "True"

    declare_map_yaml_cmd = DeclareLaunchArgument(
        "map",
        description="Full path to map yaml file to load",
        default_value=os.path.join(basic_mobile_robot, "maps", "smalltown_world.yaml"),
    )

    declare_gps_params_file_cmd = DeclareLaunchArgument(
        "gps_params",
        default_value=os.path.join(gps_wpf, "params", "ekfs_demo.yaml"),
        description="Full path to the ROS2 parameters file to use for all launched nodes",
    )

    declare_nav2_params_file_cmd = DeclareLaunchArgument(
        "nav2_params",
        default_value=os.path.join(basic_mobile_robot, "params", "nav2_params.yaml"),
        description="Full path to the ROS2 parameters file to use for all launched nodes",
    )

    param_substitutions = {"use_sim_time": use_sim_time, "yaml_filename": map_yaml_file}

    configured_params = RewrittenYaml(
        source_file=nav2_params,
        # root_key=namespace,
        param_rewrites=param_substitutions,
        convert_types=True,
    )

    basic_mobile_robot_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(basic_launch_dir, "basic_mobile_bot_v5.launch.py")
        ),
        launch_arguments={
            "use_sim_time": use_sim_time,
            # "use_respawn": use_respawn,
            # "use_composition
            "map": map_yaml_file,
            "params_file": nav2_params,
        }.items(),
    )
    gps_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(gps_launch_dir, "demo_launch.py")),
        launch_arguments={
            "params_file": gps_params,
        }.items(),
    )
    ld = LaunchDescription()

    ld.add_action(declare_gps_params_file_cmd)
    ld.add_action(declare_nav2_params_file_cmd)
    ld.add_action(declare_map_yaml_cmd)
    ld.add_action(basic_mobile_robot_launch)
    ld.add_action(gps_launch)
    # ld.add_action(bringup_cmd_group)

    return ld
