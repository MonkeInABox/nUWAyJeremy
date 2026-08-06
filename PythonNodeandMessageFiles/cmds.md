# Some useful commands

To filter an mcap file with regex
mcap filter rosbag2_2023_01_23-14_03_33/rosbag2_2023_01_23-14_03_33_0.mcap -o test.mcap -y "/imu/.*" -y "/ins0/.*" -y "/sbg/.*"

``` bash
# old docker command, not used anymore but kept 
docker run -it --rm --privileged --net=host --env=DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix innoc3nt/humble-ros:latest /bin/bash

# set datum of the navasat transform node from robot localization
ros2 service call /datum robot_localization/srv/SetDatum '{geo_pose: {position: {latitude: 33.83, longitude: -84.42, altitude: 254.99568}, orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}}}'

# service to get parameters
ros2 service call /controller_server/get_parameters rcl_interfaces/srv/GetParameters "{"names": {FollowPath.approach_velocity_scaling_dist}}"

# CAN bus viewer
python3 -m can.viewer -c can0 -i socketcan -f {0x193:0xfff,0x214:0xfff}

# for launching gazebo simulation in dev container
ros2 launch nav2_bringup tb3_simulation_launch.py headless:=True params_file:=./src/master/config/nav2_reeds_params.yaml map:=./src/master/maps/Tomscombined.yaml world:=/usr/share/gazebo-11/worlds/empty.world

# Sending waypoints to server
ros2 action send_goal /follow_gps_waypoints gps_interfaces/action/FollowGPSWaypoints "{gps_poses: [{position: {x: 37.151, y: -44.464, z: 0.0}, orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}},{position: {x: 27.151, y: -34.464, z: 0.0}, orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}}]}"


ros2 topic pub /plan nav_msgs/msg/Path "{header: {frame_id: map}, poses: [header: {}, pose: {position: {x: 37.151, y: -44.464, z: 0.0}, orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}}, header: {}, pose: {position: {x: 27.151, y: -34.464, z: 0.0}, orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}}]}"

ros2 action send_goal -f /navigate_to_pose nav2_msgs/action/NavigateToPose '{pose: {header: {frame_id: "map"}, pose: {position: {x: 6.74, y: 0.13, z: 0.0}, orientation: {x: 0.0, y: 0.0, z: 0.8578, w: 0.513}}}, behavior_tree: ""}'

docker exec -it nav2 bash && source install/setup.bash && ros2 run python_nodes bus_follow_path 

source install/setup.bash && ros2 run python_nodes bus_follow_path 

[INFO] [1702791668.370307593] [basic_navigator]: Nav2 is ready for use!
Start index is:  11
Goal pose length is:  2544
Order waypoint length 2555
[INFO] [1702791668.492448779] [basic_navigator]: Following 2544 path points....
Traceback (most recent call last):
  File "/workspaces/humble_nuway2_ros2_ws/install/python_nodes/lib/python_nodes/bus_follow_path", line 33, in <module>
    sys.exit(load_entry_point('python-nodes', 'console_scripts', 'bus_follow_path')())
  File "/workspaces/humble_nuway2_ros2_ws/build/python_nodes/python_nodes/bus_follow_path.py", line 528, in main
    if Duration.from_msg(feedback.navigation_time) > Duration(seconds=1000000.0):
AttributeError: 'FollowPath_Feedback' object has no attribute 'navigation_time'
[ros2run]: Process exited with failure 1


```
