#!/usr/bin/zsh

shell=zsh
distro=humble

#ls src
sudo apt-get update
rosdep update
rosdep install --from-paths src --ignore-src -y --rosdistro ${distro}

# rm -rf install log build
source /opt/ros/${distro}/setup.${shell}
# SICK LiDAR packages
colcon build --packages-select libsick_ldmrs --event-handlers console_direct+
source install/setup.${shell} && colcon build --packages-select sick_scan --cmake-args " -DROS_VERSION=2" " -DSCANSEGMENT_XD=0" --event-handlers console_direct+

# # user packages
source install/setup.${shell} && colcon build --symlink-install --packages-select master python_nodes python_nodes_interfaces sbg_driver pointcloud2_assembler --cmake-args -DCMAKE_EXPORT_COMPILE_COMMANDS=1
source install/setup.${shell} && colcon build --packages-select rviz_2d_overlay_msgs rviz_2d_overlay_plugins --cmake-args -DCMAKE_EXPORT_COMPILE_COMMANDS=1

export PYTHONPATH="${PYTHONPATH}:/workspaces/humble_nuway2_ros2_ws/build/python_nodes/python_nodes"


source aliases
