# All My Working Files for Honours 2026 - nUWAy Shuttle Bus LiDAR Model Dev

- Thank you to Kieran Quirke-Brown et al. for the basis for a lot of these files
- Files edited or created by Jeremy Butson are commented on top
- This repository is about adapting https://github.com/szacho/pointcam for use on the Shuttle Buses as part of REV at the University of Western Australia, along with some additional features. Feel free to use with proper referencing
- Note that PointCAM's base backbone from https://github.com/szacho/pointcam is required


# Running the Sweep
```bash
#ensure all requirements are set up, for reference look at the PointCam requirements
python3 ./sweep2.py # or sweepmamba.py for PointMamba - note different reqs
```

# Running on the Bus
- Note that all files in SimRunning are required for bus driving
```bash
cd ./SimRunning
# ensure topic names and the path to the model that you want to run are correct in ./busControlNode.py
# also make sure that the transforms are the same in here as those used to train the model

python3 ./busControlNode.py
```

# Convert LiDAR and cmd_vel data into Numpy 
```bash
colcon build --packages-select python_nodes_interfaces

source ./install/setup.bash

source /opt/ros/humble/setup.bash

conda deactivate
# ensure that the path has been changed in the python file
python3 convertLidarData.py
```

# Setting Up Simulator
```bash
cd ./Unity/Exec
./REVSIMv1.3.1.x86_64

# new terminal
cd ~/nUWAy_ros2_ws-nuway3_humble_dev/
source install/setup.bash
ros2 run python_nodes stamped_conversion

# new terminal
cd ~/Unity/REVSIM_ros2_ws
source ./install/setup.bash
ros2 launch robot_description controller_js1.launch.py
# if this doesnt work:
ros2 launch robot_description controller.launch.py

ros2 bag record -a -o ~/media/sim/BCC8-9211 -s mcap
```

