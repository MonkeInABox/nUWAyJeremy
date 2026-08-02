

#!/bin/bash

# Script to start nUWAy via launch file
# V1 (ROS 2 foxy) - erik


function quit()
{
    #killall firefox
    #killall GeckoMain
    #killall -s SIGKILL $(ps -aux | grep ros2 | awk '{$print 2}')
    killall ros2
    #killall tbs_talker
    #killall nuway_gps_tracker
    # killall nuway_ros2_monitor
    exit
}

#trap quit SIGINT

function start() {

  # set monitor
  #export DISPLAY=:0
#  fast-discovery-server -i 0 & 

  # Source R
  # Start Safety lidars first
  #ros2 launch master safety_lidars.launch.py &

  #sleep 5

  #ps -aux | grep safety_lidar | grep -v grep | awk '{print $2}' | xargs kill -9

  #killall sick_generic_caller

  #sleep 2


  #rviz2 &

  # start ntrip client
  #echo 'starting bnc'
  #~/Downloads/bnc-2.12.18/bnc --conf ~/.config/BKG/BNC.bnc &

  # npx serve -s ~/nUWAy-UI/nuway-ui/build &
  #firefox -kiosk http://localhost:80 &
  #while true; do
  #	WID=$(DISPLAY=:0 wmctrl -l -p | grep -i firefox | awk '{print $1}')
  #	if [ "$WID" == "" ]; then
  #		sleep 1
  #	else
  #		break	
  #	fi
  #done
  #wmctrl -ir $WID -e 0,0,1050,1024,768

  #DISPLAY=:0 xset -dpms
 
  #  sleep 5
  echo 'ssh orin'
  ssh -t -i /home/nuway1/.ssh/id_rsa_orin orin@192.168.5.29 "/home/orin/nUWAy_Xavier_ros2_ws/start_orin_nuway2.bash"

  # Start the main launch file

  #echo 'start master'
  #ros2 launch master datacollection.launch.py
 # &
  # ros2 launch master buspc_monitor.launch.py 

#  ps -aux | grep safety_lidar | grep -v grep | awk '{print $2}' | xargs kill -9

#  killall sick_generic_caller

  # Start Safety lidars first
#  ros2 launch master safety_lidars.launch.py &

  #echo 'nUWAy: Started.'
  #echo 'nUWAy: Press Ctrl + C to exit.'
}


##################################### MAIN ####################################


start

while :; do
    sleep 1 # Keep in foreground forever so Control+C can safely exit the script
done
