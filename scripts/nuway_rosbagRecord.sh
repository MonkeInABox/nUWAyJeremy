#!/bin/bash

source /opt/ros/galactic/setup.bash

source /home/uwara/nuway_ros2_ws/install/setup.bash

timestamp=$(date +%Y%m%d%H%M)

ros2 bag record -o ${timestamp}_rosbag /map /map_updates /lidar/localisation_merged/scan /plan /lookahead_point /lookahead_collision_arc /local_costmap/costmap /local_costmap/costmap_updates /ins0/orientation /ins0/position /CameraFront
