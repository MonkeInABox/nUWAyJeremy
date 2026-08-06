FROM osrf/ros:humble-desktop as base
SHELL ["/bin/bash", "-c"]

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ="Australia/Perth"
RUN apt-get update \
        && apt-get -y install \
        ros-humble-navigation2 ros-humble-nav2-bringup ros-humble-rviz2 ros-humble-robot-localization \
        ros-humble-rosbridge-suite ros-humble-rosbag2-storage-mcap ros-humble-cyclonedds ros-humble-velodyne \
        ros-humble-pointcloud-to-laserscan ros-humble-teleop-twist-joy ros-humble-teleop-twist-keyboard ros-humble-joy \
        ros-humble-joy-linux ros-humble-pcl-msgs ros-humble-pcl-conversions ros-humble-can-msgs ros-humble-gps-msgs \
        xsel evince tmux tmuxinator libqt5svg5 wget can-utils net-tools libasound-dev libportaudio2 libportaudiocpp0 portaudio19-dev \
        ros-humble-tf-transformations ros-humble-sick-scan-xd \
        # 
        # Clean up
        && apt-get autoremove -y \
        && apt-get clean -y \
        && rm -rf /var/lib/apt/lists/*

#RUN apt install python3-pyaudio

# ros tooling uses setuptools but is deprecated in current python, this is a workaround
RUN wget https://bootstrap.pypa.io/get-pip.py && python3 get-pip.py && pip3 install setuptools==58.2.0 && rm get-pip.py 

# Default powerline10k theme, no plugins installed
RUN sh -c "$(wget -O- https://github.com/deluan/zsh-in-docker/releases/download/v1.1.5/zsh-in-docker.sh)"

# Fix rviz black screen
RUN apt update && apt install -y software-properties-common && add-apt-repository ppa:kisak/kisak-mesa && apt upgrade -y
# ============================== install additional dependencies  ========================================= #
FROM base as common
#ENV WS=nUWAy_ros2_ws
ENV WS=humble_nuway2_ros2_ws
ENV WORKSPACE=/workspaces/$WS
ENV ROS_DOMAIN_ID=5
WORKDIR /workspaces
SHELL [ "/usr/bin/zsh", "-c" ]
ENV DEBIAN_FRONTEND=dialog
ENV PATH=${PATH}:/home/root/.local/bin
RUN adduser ros
RUN gpasswd --add ros dialout

COPY --chown=ros .zshrc /home/ros/.zshrc
COPY --chown=ros ros_entrypoint.sh /ros_entrypoint.sh
RUN chmod +x  /ros_entrypoint.sh

RUN mkdir -p -m 0700 /root/.ssh  && ssh-keyscan github.com >> /root/.ssh/known_hosts
RUN pip3 install python-can requests SpeechRecognition
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install PyAudio transforms3d
# pyaudio
ENTRYPOINT [ "/ros_entrypoint.sh" ]

# ========================================== dev container ================================================ # 
FROM common as dev
WORKDIR ${WORKSPACE}
# Set up auto-source of workspace for ros user
# RUN sh -c "$(wget https://raw.githubusercontent.com/ohmyzsh/ohmyz sh/master/tools/install.sh -O -)"
# RUN echo "if [ -f ${WORKSPACE}/install/setup.zsh ]; then source ${WORKSPACE}/install/setup.zsh; fi" >> /home/ros/.zshrc
RUN apt-get update && apt-get -y install ros-humble-gazebo-ros ros-humble-gazebo-ros-pkgs \ 
        ros-humble-xacro "ros-humble-turtlebot3*"

USER ros

# ====================================== staging container ================================================ #
# ! IMPORTANT! Must be run from the workspace root to be able to add in the files as per Docker security permissions
FROM common as staging
USER root
COPY --chown=ros:ros --chmod=700 . ${WORKSPACE}
# RUN chown=ros:ros ${WORKSPACE}
# RUN chmod=700 ${WORKSPACE}
RUN chown -R ros ${WORKSPACE}

WORKDIR ${WORKSPACE}
USER ros
RUN ./build.sh
# ======================================== production container =========================================== #
FROM common as prod
RUN ssh -T git@github.com
RUN --mount=type=ssh git clone git@github.com:uwa-rev/nUWAy_ros2_ws.git -b nuway2_humble
RUN --mount=type=ssh cd nUWAy_ros2_ws && ./setup.sh
RUN chown -R ros ${WORKSPACE}
WORKDIR ${WORKSPACE}
#WORKDIR /workspaces/nUWAy_ros2_ws
USER ros
RUN ./build.sh
