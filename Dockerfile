FROM nvcr.io/nvidia/l4t-jetpack:r36.4.0
 
SHELL ["/bin/bash", "-c"]
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ="Australia/Perth"
 

RUN apt-get update && apt-get install -y curl gnupg lsb-release software-properties-common \
    && add-apt-repository universe \
    && curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" \
        | tee /etc/apt/sources.list.d/ros2.list > /dev/null \
    && apt-get update \
    && apt-get install -y \
        ros-humble-ros-base \
        ros-humble-cyclonedds \
        ros-humble-sensor-msgs-py \
        ros-humble-message-filters \
        python3-pip python3-colcon-common-extensions \
    && apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/*
 

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install \
    torch==2.11.0 torchvision==0.26.0 xformers==0.0.32+8ed0992.d20250724 \
    --index-url=https://pypi.jetson-ai-lab.io/jp6/cu126
 
RUN python3 -m pip install omegaconf timm einops pytorch-lightning

ENV TORCH_CUDA_ARCH_LIST="8.7"
RUN python3 -m pip install 'pytorch3d @ git+https://github.com/facebookresearch/pytorch3d.git' --no-build-isolation

RUN python3 -m pip install hatchling editables
 
RUN git clone https://github.com/szacho/pointcam.git /opt/pointcam \
    && cd /opt/pointcam && python3 -m pip install -e . --no-build-isolation
 

WORKDIR /workspace/pointcam_inference
COPY model.py driveModel.py lidarCmdVelPublisher.py ./

ENV ROS_DOMAIN_ID=5
ENV RMW_IMPLMENTATION=rmw_cyclonedds_cpp
 
COPY docker_entrypoint.sh /docker_entrypoint.sh
RUN chmod +x /docker_entrypoint.sh
ENTRYPOINT ["/docker_entrypoint.sh"]
CMD ["python3", "lidarCmdVelPublisher.py"]
