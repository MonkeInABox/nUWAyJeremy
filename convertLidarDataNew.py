#!/usr/bin/env python3
 
import os
import sys
import yaml
import datetime
import argparse
import numpy as np
from collections import deque
from os.path import join, exists, dirname
 
# ROS 2 & Sensor Processing Libraries
import sensor_msgs_py.point_cloud2 as pc2
from rosidl_runtime_py.utilities import get_message
from rclpy.serialization import deserialize_message
from mcap.reader import make_reader
from numpy.lib.recfunctions import structured_to_unstructured
 
 
class db3Parser:
    """Parser for ROS2 SQLite3 (.db3) bag files (Stub implementation)."""
    def __init__(self, file: str) -> None:
        self.file = file
        raise NotImplementedError("db3 parsing is not fully implemented in this script.")
 
    def get_messages(self, topic_name: str, start_time=None, end_time=None):
        return []
 
 
class mcapParser:
    """Parser for MCAP (.mcap) ROS 2 bag files."""
    def __init__(self, file: str) -> None:
        self.reader = make_reader(open(file, "rb"))
 
    def get_messages(self, topic_name: str, start_time=None, end_time=None):
        print(f"Fetching messages for topic: {topic_name}")
        messages = []
        iter_kwargs = {"topics": [topic_name]}
        if start_time is not None and end_time is not None:
            iter_kwargs["start_time"] = start_time
            iter_kwargs["end_time"] = end_time
 
        for msg in self.reader.iter_messages(**iter_kwargs):
            topic_data = deserialize_message(msg[2].data, get_message(msg[0].name))
            timestamp = msg[2].log_time  # bag recording time - consistent across all topics
            messages.append([timestamp, topic_data])
 
        print(f"Retrieved {len(messages)} messages for {topic_name}")
        return messages
 
    def get_msg_frame(self, topic_name: str, timestamp: float):
        messages = []
        start_t = timestamp - 5e8
        end_t = timestamp + 5e8
        for msg in self.reader.iter_messages(topics=[topic_name], start_time=start_t, end_time=end_t):
            topic_data = deserialize_message(msg[2].data, get_message(msg[0].name))
            cur_timestamp = msg[2].log_time  # bag recording time - consistent across all topics
            messages.append([cur_timestamp, topic_data])
 
        return messages[len(messages) // 2] if messages else None
 
 
class BagFileParserFactory:
    """Factory class to instantiate appropriate parser based on bag format."""
    def __init__(self, bag_file: str):
        self.bag_file = bag_file
        self.parser = None
        self.file_type = self.get_file_type()
 
        print("Start parsing bag metadata...")
        metadata_path = join(dirname(self.bag_file), "metadata.yaml")
 
        if not exists(metadata_path):
            raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
 
        with open(metadata_path, 'r') as stream:
            self.metadata = yaml.safe_load(stream)
            bag_info = self.metadata['rosbag2_bagfile_information']
            self.start_time = bag_info["starting_time"]['nanoseconds_since_epoch']
            self.duration = bag_info["duration"]['nanoseconds']
 
        if self.file_type == "db3":
            self.parser = db3Parser(self.bag_file)
        elif self.file_type == "mcap":
            self.parser = mcapParser(self.bag_file)
 
        print("Metadata parsing complete.")
 
    def get_file_type(self) -> str:
        extension = self.bag_file.split(".")[-1].lower()
        if extension in ["db3", "mcap"]:
            return extension
        else:
            print(f"Error: Unknown file type '.{extension}'")
            sys.exit(1)
 
    def get_parser(self):
        return self.parser
 
 
def get_topic(topic_list, pre_timestamp, post_timestamp):
    """Filter list to find messages within temporal boundaries and pick median."""
    topic_list_part = [
        msg for msg in topic_list
        if pre_timestamp < msg[0] < post_timestamp
    ]
    return topic_list_part[len(topic_list_part) // 2] if topic_list_part else None
 
 
def extract_ros2bag_lidar_cmd(rosbag_path: str, time_str: str, output_path: str):
    try:
        factory = BagFileParserFactory(rosbag_path)
        parser = factory.get_parser()
    except Exception as e:
        print(f"Cannot open file {rosbag_path}: {e}")
        sys.exit(2)
 
    try:
        time_obj = datetime.datetime.strptime(time_str, '%H:%M:%S.%f').time()
        _ = datetime.timedelta(
            hours=time_obj.hour,
            minutes=time_obj.minute,
            seconds=time_obj.second,
            microseconds=time_obj.microsecond
        ).total_seconds() * 1e9
    except ValueError:
        print(f"Time format error: '{time_str}'. Expected format: <hh:mm:ss.ff>")
        sys.exit(2)
 
    pointcloud_count = 0
    divisor = max(1, factory.duration // 300000000000 + 2)  # ~5 min splits
    print(f"Splitting processing into {divisor} batch interval(s)...")
 
    start_time = factory.start_time
    batch_duration = factory.duration // divisor
    vel_limit = 0.5
    data_sorting = True
 
    vel_arr = np.empty([1, 4])
    steer_arr = np.empty([1, 4])
 
    d = deque(maxlen=4)
    deqvel = deque(maxlen=4)
    deqsteer = deque(maxlen=4)
 
    if data_sorting:
        _ = parser.get_messages("/driving_mode_stamped")
 
    cmd_vel_topic_list = parser.get_messages("/joy_cmd_vel_stamped")
    print(f"Total cmd_vel messages: {len(cmd_vel_topic_list)}")
    if cmd_vel_topic_list:
        print(f"First cmd_vel timestamp: {cmd_vel_topic_list[0][0]}")
        print(f"Last cmd_vel timestamp: {cmd_vel_topic_list[-1][0]}")
 
    for j in range(divisor):
        batch_start = start_time + batch_duration * j
        batch_end = start_time + batch_duration * (j + 1)
 
        front_lidar_topic_list = parser.get_messages(
            "/lidar_localisation/front/cloud", start_time=batch_start, end_time=batch_end
        )
        rear_lidar_topic_list = parser.get_messages(
            "/lidar_localisation/rear/cloud", start_time=batch_start, end_time=batch_end
        )
 
        print(f"Batch {j}: front_lidar={len(front_lidar_topic_list)}, rear_lidar={len(rear_lidar_topic_list)}")
        if front_lidar_topic_list:
            print(f"  front_lidar first ts: {front_lidar_topic_list[0][0]}, last ts: {front_lidar_topic_list[-1][0]}")
 
        if not front_lidar_topic_list:
            continue
 
        for i in range(len(front_lidar_topic_list)):
            timestamp = front_lidar_topic_list[i][0]
            pre_timestamp = timestamp - 5e8
            post_timestamp = timestamp + 5e8
 
            cmd_vel_topic = get_topic(cmd_vel_topic_list, pre_timestamp, post_timestamp)
            rear_lidar_topic = get_topic(rear_lidar_topic_list, pre_timestamp, post_timestamp)
 
            print(f"  frame {i}: ts={timestamp}, cmd_vel_found={cmd_vel_topic is not None}, rear_lidar_found={rear_lidar_topic is not None}")
 
            if data_sorting:
                if (cmd_vel_topic is not None) and (rear_lidar_topic is not None):
 
                    vel = cmd_vel_topic[1].twist.linear.x
                    steer = cmd_vel_topic[1].twist.angular.z
 
                    if abs(vel) > 5.5 or abs(steer) > 0.32:
                        print(f"Warning: Corrupt data detected (vel={vel}, steer={steer}). Skipping.")
                        continue
 
                    front_points = structured_to_unstructured(
                        pc2.read_points(front_lidar_topic_list[i][1], field_names=("x", "y", "z", "intensity"), skip_nans=True)
                    )
                    rear_points = structured_to_unstructured(
                        pc2.read_points(rear_lidar_topic[1], field_names=("x", "y", "z", "intensity"), skip_nans=True)
                    )
 
                    data_array = np.array([front_points, rear_points, vel_arr, steer_arr], dtype=object)
 
                    d.appendleft(data_array)
                    deqvel.append(vel)
                    deqsteer.append(steer)
 
                    if len(d) == 4:
                        filename = f"Pcl_{pointcloud_count}_{deqvel[0]:.3f}_{deqsteer[0]:.3f}_.npy"
                        saved_array = np.array(d.pop())
                        saved_array[2], saved_array[3] = np.array(deqvel), np.array(deqsteer)
 
                        np.save(join(output_path, filename), saved_array)
 
                        pointcloud_count += 1
                        if pointcloud_count % 1000 == 0:
                            print(f"Processed {pointcloud_count} samples...")
 
            else:
                if cmd_vel_topic is not None:
                    vel = cmd_vel_topic[1].twist.linear.x
                    steer = cmd_vel_topic[1].twist.angular.z
 
                    if vel >= vel_limit:
                        points = structured_to_unstructured(
                            pc2.read_points(front_lidar_topic_list[i][1], field_names=("x", "y", "z", "intensity"), skip_nans=True)
                        )
 
                        data_array = np.array([points, vel_arr, steer_arr], dtype=object)
                        d.appendleft(data_array)
                        deqvel.append(vel)
                        deqsteer.append(steer)
 
                        if len(d) == 4:
                            filename = f"Pcl_{pointcloud_count}_{deqvel[0]:.3f}_{deqsteer[0]:.3f}_.npy"
                            saved_array = np.array(d.pop())
                            saved_array[1], saved_array[2] = np.array(deqvel), np.array(deqsteer)
 
                            np.save(join(output_path, filename), saved_array)
 
                            pointcloud_count += 1
                            if pointcloud_count % 1000 == 0:
                                print(f"Processed {pointcloud_count} samples...")
 
    print(f"Done. Total pointclouds saved: {pointcloud_count}")
 
 
def main():
    parser = argparse.ArgumentParser(description="Extract LiDAR and Command Vel data from ROS 2 bag files.")
    parser.add_argument("-p", "--path", type=str, default="/home/ubuntu22/jeremybutson/newbag/",
                        help="Ros2bag file directory path.")
    parser.add_argument("-o", "--output", type=str, default="/home/ubuntu22/jeremybutson/output",
                        help="Target output directory path.")
    parser.add_argument("-t", "--time", type=str, default="00:00:00.00",
                        help="Time elapsed since start of ros2bag (<hh:mm:ss.ff>).")
 
    args = parser.parse_args()
 
    search_folder = args.path
    output_folder_path = args.output
    time_str = args.time
 
    if not exists(search_folder):
        print(f"Error: Search path '{search_folder}' does not exist.")
        sys.exit(1)
 
    try:
        for file in os.listdir(search_folder):
            if file.endswith(".mcap"):
                rosbag_path = join(search_folder, file)
                output_path = join(output_folder_path, file.split(".")[0])
 
                os.makedirs(output_path, exist_ok=True)
                print(f"Processing bag file: {file} | Output target: {output_path}")
 
                extract_ros2bag_lidar_cmd(rosbag_path, time_str, output_path)
 
    except IOError as e:
        print(f"Extraction failed at folder '{search_folder}': {e}")
        sys.exit(2)
 
 
if __name__ == "__main__":
    main()

