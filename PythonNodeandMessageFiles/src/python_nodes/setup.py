from setuptools import setup

package_name = "python_nodes"

setup(
    name=package_name,
    version="0.0.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="uwara",
    maintainer_email="uwara@todo.todo",
    description="TODO: Package description",
    license="TODO: License declaration",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "nuway_gps_tracker = python_nodes.nuway_gps_tracker:main",
            "nuway_ip_publisher = python_nodes.nuway_ip_publisher:main",
            "tbs_talker = python_nodes.tbs_talker:main",
            "safety_soft_scale = python_nodes.safety_soft_scale:main",
            "safety_event_monitor = python_nodes.safety_event_monitor:main",
            "incident_recorder = python_nodes.incident_recorder:main",
            "can_bridge = python_nodes.can_bridge:main",
            "robot_navigator = python_nodes.robot_navigator",
            "bus_nav_through_poses= python_nodes.nav_through_poses2:main",
            "bus_follow_path= python_nodes.bus_follow_path:main",
            "gps_location= python_nodes.gps_location:main",
            "gps_location2= python_nodes.gps_location2:main",
            "gps_location_novatel= python_nodes.gps_location_novatel:main",
            "stamped_conversion= python_nodes.stamped_conversion:main",
            "speech_node= python_nodes.speech_node:main",
            "battery_node= python_nodes.battery_node:main",
            "lidarScan= python_nodes.lidarScan:main",
            "slow_zone= python_nodes.stop_node:main"
        ],
    },
)
