# nUWAy ROS 2 workspace for the bus PC

## Introduction

The repository contains code for the main bus PC which is one of 2 PC's used on the nUWAy shuttle bus at the main UWA campus.

To access the PC you need to connect to the local network and SSH to the PC. It's current IP address is statically set to *192.168.5.30*, the username is *uwara*. Please ask one of the other team members for the password (**A full LAN schematic of devices can be found on teams**).

Packages within the repository can be seperated into two distinct groups, developer packages created by the REV team and imported packages.

## Initial download (If you are building on a PC that supports humble i.e. Ubuntu 22.04, else look down at the humble section)

This workspace uses [vcstool](https://github.com/dirk-thomas/vcstool) to manage external repos, install according to here 

``` bash
vcs import --recursive < src/ros2.repos src
# or run the script
./setup.sh
```

 To build the workspace, use the build script or the vscode task "build". This will only work if you can run humble on your machine, else look at the docker information below.

## Developer Packages

There are currently 4 developer packages:

1. master
2. sbg_ros2_driver
3. python_nodes (probably need to work on this name TODO).
4. gps_waypoint_follower

### master

The master package contains the ROS 2 launch files, parameters and runtime information (such as map files). No source code is used in the master package as it is only used for **startup, params and initial values TODO**.

### sbg_ros2_driver

This has been forked from the manufacturer repo and some enhancements made, mainly in setting the GPS Datum to project the odometry from a datum that is set in the node yaml file.

### python_nodes

Provides a bunch of auxiliary nodes which are not required for operations such as:

- tbs_talker          : for reporting battery information serially connected to the PC at /dev/ttyS1 - superceded by reading CAN bus for the E4BMS
- nuway_gps_tracker   : logs GPS to therevproject.com/tracking/gps_pos.php
- nuway_ip_publisher  : logs the public IP of the bus to threrevproject.com/tracking/public_ip.php
- can_bridge          : this translates cmd_vel commands to CAN bus commands and limits the angular rate change to the limits specified by EZMile

Some other nodes which don't work properly

- safety_soft_scale - superceded by velocity monitor in navigation2 humble
- safety_event_monitor
- incident_recorder

### gps_waypoint_follower

Provides three nodes:

- Client : A node that requests the server to follow a list of waypoints
- Server : A node that provides the FollowGPSWaypoints service, this sits in between the client and nav2 by converting a list of GPS waypoints into the map frame that nav2 uses
- Logger : Logs waypoints into a csv file, currently time based, work on creating it distance based

## Imported packages

There are currently 2 vendor packages that need to be built for running the SICK LiDARS:

- [sick_scan_xd](https://github.com/SICKAG/sick_scan_xd)
- [libsick_ldmrs](https://github.com/SICKAG/libsick_ldmrs)

The build process for these packages handled with the build.sh script and are prebuilt in the docker image.

Current node setup using RQT graph:

**TODO**

## Humble and docker

This branch builds humble and a docker image with this workspace built is available from docker hub at innoc3nt/humble-ros:latest. You can get it with

``` bash
docker pull innoc3nt/humble-ros:latest
```

Replaced by:

```bash
docker pull ghcr.io/uwa-rev/humble-ros:latest
```

In order to pull this image you will need to generate a **classic** personal access token on github and then login to docker using that token:

```bash
sudo docker login ghcr.io
```

It will then ask for your username, use your github username, and then password, use the personal access token. If you still can't pull from the github package try logging out of ghcr.io and then in again.

```bash
sudo docker logout
```

To develop on this branch, you need to install the necessary extensions below. The development container config lives in .devcontainer folder. Install the extension from vscode and reopen in devcontainer. Install docker on your computer then click on the bottom left of the vscode window and click on the **Reopen in container**.

### Extensions

[Remote Development Extension Pack](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack)
[Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

More info about devcontainers:

- https://code.visualstudio.com/docs/containers/overview
- https://docs.github.com/en/codespaces/setting-up-your-project-for-codespaces/adding-a-dev-container-configuration/introduction-to-dev-containers

It is advisable to go through the docker [quickstart](https://docs.docker.com/get-started/) to familiarise yourself with how docker works if you haven't used it before.

The devcontainer will take a while to load when you use it the first time as it has to pull in all the dependencies. Don't be surprised if it takes more then 5 minutes.

The Dockerfile has three main targets:

- dev : which is the target for the devcontainer and mounts the workspace into the container environment so you can push your code to Github.
- staging : which is used for preparing the workspace to be built into the production one
- prod : which is the image that is published to docker hub and used in normal operations

If you are developing, you will only be using the dev stage. The full image build process is slightly more involved and won't be covered here.

## Running on the shuttle bus with docker

Docker compose is used to start up the system, the config lives in the compose.yaml file in the workspace root. Please note that variable interpolation for the docker compose file occurs from a .env file in the root. You will have to create this on your system. You need the IMAGE and MAP variables to be in the .env file. (e.g. IMAGE=innoc3nt/humble-ros:latest) See the [docker compose specification](https://docs.docker.com/compose/compose-file/) for more info. Note the config options in the compose file which allow quick reconfiguration of parameters for the nodes, this is expected to be the main way to change node parameters.
