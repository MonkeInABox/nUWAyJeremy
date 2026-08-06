#!/bin/bash
set -e

vcs import --recursive  < src/ros2.repos src
sed -i '/catkin/d' ./src/libsick_ldmrs/package.xml