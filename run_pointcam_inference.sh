set -e

CHECKPOINT_PATH="${1:-/pointcam_shuttle_lane_following.pth}"
CMD_VEL_TOPIC="${2:-/cmd_vel}"

docker run -it --rm \
    --runtime nvidia \
    --network host \
    --ipc host \
    -v "$(dirname "$CHECKPOINT_PATH")":/checkpoints:ro \
    pointcam-inference:latest \
    python3 lidarCmdVelPublisher.py --ros-args \
        -p checkpoint_path:="/checkpoints/$(basename "$CHECKPOINT_PATH")" \
        -p cmd_vel_topic:="$CMD_VEL_TOPIC"
