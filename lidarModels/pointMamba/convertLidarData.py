#!/usr/bin/env python3
from rosidl_runtime_py.utilities import get_message
from rclpy.serialization import deserialize_message
from mcap.reader import make_reader
import yaml
import sys, getopt
import matplotlib.pyplot as plt
import numpy as np
import datetime
import math
import os
import cv2
from os.path import join, exists, dirname, abspath
import sensor_msgs_py.point_cloud2 as pc2
from numpy.lib.recfunctions import structured_to_unstructured
from collections import deque
from python_nodes_interfaces.msg import BoolStamped, Int32Stamped, Float32MultiArrayStamped
from cv_bridge import CvBridge

'''
Ros2bag file parser factory class
'''
class BagFileParserFactory():
    def __init__(self, bag_file:str): 
        self.bag_file = bag_file
        self.parser = None
        self.file_type = None
        self.file_type = self.get_file_type()
        print("start parsing...")

        with open(f"{dirname(self.bag_file)}/metadata.yaml", 'r') as stream:
            self.metadata = yaml.safe_load(stream)
            self.start_time = self.metadata['rosbag2_bagfile_information']["starting_time"]['nanoseconds_since_epoch']
            self.duration = self.metadata['rosbag2_bagfile_information']["duration"]['nanoseconds']

        if self.file_type == "db3":
            self.parser = db3Parser(self.bag_file)
        elif self.file_type == "mcap":
            self.parser = mcapParser(self.bag_file)
        print("parsing done")
    
    def get_file_type(self):
        if self.bag_file.split(".")[-1]=="db3":
            return "db3"
        elif self.bag_file.split(".")[-1]=="mcap":
            return "mcap"
        else:
            print("Error: unknown file type")
            exit(1)
    
    def get_parser(self):
        return self.parser

'''
Load .mcap ros2bag file 
'''
class mcapParser():
    def __init__(self, file:str) -> None:
        self.reader =  make_reader(open(file, "rb"))

    def get_messages(self, topic_name:str, start_time=None, end_time=None):
        print(f"get_messages: {topic_name}")
        reader = self.reader
        messages = []
        if start_time is not None and end_time is not None:
            for msg in reader.iter_messages(topics=[topic_name], start_time=start_time, end_time=end_time):
                topic = deserialize_message(msg[2].data, get_message(msg[0].name))
                timestamp = topic.header.stamp.sec * 1e9 + topic.header.stamp.nanosec
                messages.append([timestamp, topic])
        else:
            for msg in reader.iter_messages(topics=[topic_name]):
                topic = deserialize_message(msg[2].data, get_message(msg[0].name))
                timestamp = topic.header.stamp.sec * 1e9 + topic.header.stamp.nanosec
                messages.append([timestamp, topic])
        print(f"get_messages: {len(messages)}")
        return messages

    def get_msg_frame(self, topic_name:str, timestamp):
        #print(f"get_msg_frame: {topic_name}")
        reader = self.reader
        messages = []
        for msg in reader.iter_messages(topics=[topic_name], start_time=timestamp - 5e8, end_time=timestamp + 5e8):
            topic = deserialize_message(msg[2].data, get_message(msg[0].name))
            cur_timestamp = topic.header.stamp.sec * 1e9 + topic.header.stamp.nanosec
            messages.append([cur_timestamp, topic])
        #print(f"get_msg_frame: {len(messages)}")
        return messages[math.floor(len(messages)/2)] if messages else None

def get_topic(topic_list, pre_timestamp, post_timestamp):
    topic_list_part = [topic_list[j] for j in range(len(topic_list))
            if 
            (topic_list[j][0])<post_timestamp and
            (topic_list[j][0])>pre_timestamp]
    return (
        topic_list_part[math.floor(len(topic_list_part) / 2)] if topic_list_part else None
    )

def get_topic_cmd_vel(topic_list, pre_timestamp, post_timestamp):
    j_list = [j for j in range(len(topic_list))
            if 
            (topic_list[j][0])<post_timestamp and
            (topic_list[j][0])>pre_timestamp]
    j_use = math.floor((j_list[-1] - j_list[0] + 1) / 2) if j_list else None
    try: return(topic_list[j_use:j_use+5] if j_list else None)
    except: return None

def print_help():
    print('''
Usage: ./save_ros2bag.py -p <ros2bag_filename> -t <hh:mm:ss.ff>        

Options:
-h --help     Show this screen.
-p --path     Ros2bag file path.
-t --time     How much time has elapsed since the start of ros2bag.
    ''')

def plot_point_cloud(point_cloud):
    """
    Visualizes a 3D point cloud with intensity values using a scatter plot.
    
    Parameters:
    point_cloud (numpy.ndarray): An Nx4 array where each row represents a point [x, y, z, intensity].
    """
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')
    
    # Scatter plot with intensity as color map
    sc = ax.scatter(point_cloud[:, 0],  # x-coordinates
                    point_cloud[:, 1],  # y-coordinates
                    point_cloud[:, 2],  # z-coordinates
                    c=point_cloud[:, 3],  # intensity values
                    cmap='viridis',      # colormap
                    marker='s',          # point marker
                    s=15)                # marker size
    
    # Adding color bar to show intensity scale
    cb = plt.colorbar(sc, ax=ax, pad=0.1)
    cb.set_label('Intensity')
    
    # Label axes
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    
    # Set plot title
    ax.set_title('3D Point Cloud with Intensity Visualization')
    
    plt.show()


def extract_ros2bag_lidar_cmd(rosbag_path,time_str,output_path):
    try:    
        parser = BagFileParserFactory(rosbag_path)
    except IOError:
        print(f'Cannot open file: {rosbag_path}')
        sys.exit(2)

    try:
        time_obj = datetime.datetime.strptime(time_str, '%H:%M:%S.%f').time()
        timestamp = datetime.timedelta(
            hours=time_obj.hour, 
            minutes=time_obj.minute, 
            seconds=time_obj.second, 
            microseconds=time_obj.microsecond).total_seconds() * 1e9
    except ValueError:
        print(f"Time format error{time_str}, should be <hh:mm:ss.ff>")
        sys.exit(2)

    pointcloud_count = 0
    divisor= parser.duration//300000000000+2#split ros2bag by divisor, about 5 minutes
    print(f"divisor: {divisor}")
    start_time = parser.start_time
    batch_duration = parser.duration // divisor
    vel_limit = 0.5
    data_sorting = True
    # x_max = 50
    # x_min = -20
    # y_limit = 20
    # z_limit = 5
    vel_arr = np.empty([1,4])
    steer_arr = np.empty([1,4])
    d = deque(maxlen=4)
    deqvel = deque(maxlen=4)
    deqsteer = deque(maxlen=4)

    # drive_cmds_topic_list = parser.get_parser().get_messages("/drive_cmds_stamped")
    if data_sorting == True:
        driving_mode_topic_list = parser.get_parser().get_messages("/driving_mode_stamped")
        #gear_topic_list = parser.get_parser().get_messages("/gear_stamped")
        #speed_mode_topic_list = parser.get_parser().get_messages("/speed_mode_stamped")
        map_pos_topic_list = parser.get_parser().get_messages("/odometry/global")
    cmd_vel_topic_list = parser.get_parser().get_messages("/joy_cmd_vel_stamped")
    for j in range(divisor):
        front_lidar_topic_list = parser.get_parser().get_messages("/lidar/velodyne/rear/cloud",start_time=start_time+batch_duration*j, end_time=start_time+batch_duration*(j+1))
        rear_lidar_topic_list = parser.get_parser().get_messages("/lidar/velodyne/front/cloud",start_time=start_time+batch_duration*j, end_time=start_time+batch_duration*(j+1))
        front_img_topic_list = parser.get_parser().get_messages("/CameraFront",start_time=start_time+batch_duration*j, end_time=start_time+batch_duration*(j+1))
        if len(front_lidar_topic_list)!=0:
            for i in range(len(front_lidar_topic_list)):
                #pointcloud_list = []
                timestamp = front_lidar_topic_list[i][0]
                pre_timestamp=timestamp - 5e8
                post_timestamp=timestamp + 5e8
                cmd_vel_topic = get_topic(cmd_vel_topic_list, pre_timestamp, post_timestamp)
                rear_lidar_topic = get_topic(rear_lidar_topic_list, pre_timestamp, post_timestamp)
                front_img_topic = get_topic(front_img_topic_list, pre_timestamp, post_timestamp)

                if data_sorting == True:
                    driving_mode_topic = get_topic(driving_mode_topic_list, pre_timestamp, post_timestamp)
                    # gear_topic = get_topic(gear_topic_list, pre_timestamp, post_timestamp)
                    # speed_mode_topic = get_topic(speed_mode_topic_list, pre_timestamp, post_timestamp)
                    map_pos_topic = get_topic(map_pos_topic_list, pre_timestamp, post_timestamp)
                    if map_pos_topic is not None:
                        map_pos_orien_topic=[
                        map_pos_topic[1].pose.pose.position.x, map_pos_topic[1].pose.pose.position.y,
                        map_pos_topic[1].pose.pose.orientation.z, map_pos_topic[1].pose.pose.orientation.w]
                    else:
                        map_pos_orien_topic=None

                    if (cmd_vel_topic is not None) and (rear_lidar_topic is not None) and (front_img_topic is not None): #and (driving_mode_topic is not None) and (gear_topic is not None))
                        # if speed_mode_topic is not None:
                        #     if speed_mode_topic[1].data==0:
                        #         vel = cmd_vel_topic[1].data[0]/4.0
                        #         steer = cmd_vel_topic[1].data[1]/0.3
                        #     else:
                        #         vel = cmd_vel_topic[1].data[0]/5.4
                        #         steer = cmd_vel_topic[1].data[1]/0.3
                        #     speed_mode_data=speed_mode_topic[1].data
                        # else:
                        #     vel = cmd_vel_topic[1].data[0]/4.0
                        #     steer = cmd_vel_topic[1].data[1]/0.3
                        #     speed_mode_data=0
                        #if vel >= vel_lim:
                        vel = cmd_vel_topic[1].twist.linear.x
                        steer = cmd_vel_topic[1].twist.angular.z
                        if (abs(vel) > 5.5) or (abs(steer) > 0.32):
                            print("Warning: Corrupt data detected. Skipping this entry.")
                            print((vel, steer))
                            continue
                        else:
                            bridge = CvBridge()
                            front_points = structured_to_unstructured(pc2.read_points(front_lidar_topic_list[i][1], field_names=("x", "y", "z", "intensity"), skip_nans=True))
                            rear_points = structured_to_unstructured(pc2.read_points(rear_lidar_topic[1], field_names=("x", "y", "z", "intensity"), skip_nans=True))
                            cv_img_front = bridge.imgmsg_to_cv2(front_img_topic[1], desired_encoding='passthrough')
                            img_front=cv2.resize(cv_img_front[104:,:],(480,240))

                            Data_Array=np.array([front_points, rear_points, vel_arr, steer_arr, img_front, map_pos_orien_topic], dtype=object)
                            d.appendleft(Data_Array)
                            deqvel.append(vel)
                            deqsteer.append(steer)

                            if len(d) == 4:
                                PointCloud_Filename = f"Pcl_{pointcloud_count}_{deqvel[0]:.3f}_{deqsteer[0]:.3f}_.npy"
                                Data_Array = np.array(d.pop())
                                Data_Array[2], Data_Array[3] = np.array(deqvel), np.array(deqsteer)

                                np.save(join(output_path, PointCloud_Filename), Data_Array)


                            pointcloud_count += 1
                            if pointcloud_count%1000==0:
                                print(pointcloud_count)
                else:
                    if(cmd_vel_topic is not None):
                        vel = cmd_vel_topic[1].twist.linear.x
                        steer = cmd_vel_topic[1].twist.angular.z
                        if vel >= vel_limit:
                            points = structured_to_unstructured(pc2.read_points(front_lidar_topic_list[i][1], field_names=("x", "y", "z", "intensity"), skip_nans=True))

                            Data_Array=np.array([points, vel_arr, steer_arr], dtype=object)
                            d.appendleft(Data_Array)
                            deqvel.append(vel)
                            deqsteer.append(steer)

                            if len(d) == 4:
                                PointCloud_Filename = f"Pcl_{pointcloud_count}_{deqvel[0]:.3f}_{deqsteer[0]:.3f}_.npy"
                                Data_Array = np.array(d.pop())
                                Data_Array[1], Data_Array[2] = np.array(deqvel), np.array(deqsteer)

                                np.save(join(output_path, PointCloud_Filename), Data_Array)

                            pointcloud_count += 1
                            if pointcloud_count%1000==0:
                                print(pointcloud_count)


def main(argv):
    search_folder = '/media/ubuntu22/data/BCC8-9211/newbag'#/home/erik/Data/sim_data/Eglinton/rosbags/rosbag2_2025_01_02-12_43_13'
    output_folder_path = "/home/ubuntu22/jeremybutson/output"
    time_str = '00:00:00.00'
    try:
        opts, args = getopt.getopt(argv,"hp:t:",["help","path=", "time="])
    except getopt.GetoptError:
        print ('See -h --help')
        sys.exit(2)

    for opt, arg in opts:
        if opt in ['-h', '--help']:
            print_help()
            sys.exit()
        elif opt in ("-p", "--path"):
            search_folder = arg
        elif opt in ("-t", "--time"):
            time_str = arg
    try:
        if exists(search_folder):
            for File in os.listdir(search_folder):
                if File.split(".")[-1]=="mcap":
                    #print(os.listdir(Search_Folder))
                    rosbag_path=join(search_folder, File)
                    output_path=join(output_folder_path, File.split(".")[0])
                    if not exists(output_path):
                        os.mkdir(output_path)#need to remove existing folder
                        print(f"created folder: {File.split('.')[0]}")
                    extract_ros2bag_lidar_cmd(rosbag_path,time_str,output_path)
    except IOError:
        print(f'lidar cmd extraction failed at folder: {search_folder}')
        sys.exit(2)

if __name__ == "__main__":
    main(sys.argv[1:])