#!/bin/bash

#Source ROS
source /opt/ros/foxy/setup.bash

#Source nUWAy workspace
source /home/sae/nuway_sae_ros2_ws/install/setup.bash

#Get date and time for storage
year=`date +%Y%m%d%H%M`

echo "Starting new log call ${year}_data.csv in /home/sae/shuttleBusData folder\n"

ros2 topic echo /gps_logging --csv > /home/uwara/ShuttleBusData/cleanDrives/${year}_data.csv

#ros2 topic echo /ins0/gps_pos --csv > /home/sae/shuttleBusData/test.log

#ros2 topic echo /gps_logging --csv

#echo this is a test > /home/sae/shuttleBusData/test.log

