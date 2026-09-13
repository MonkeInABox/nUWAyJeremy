import torch
from torch import nn
from functools import partial

from torchvision import datasets, models, transforms
from PIL import Image

from einops import rearrange, repeat
from einops.layers.torch import Rearrange
from shuttlebusTrain import drivePointMamba

from torch.utils.tensorboard import SummaryWriter

import numpy as np

import cv2
import os
import sys
from os.path import join, exists, dirname, abspath
import matplotlib.cm as cm

import argparse

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import random

import rclpy
from rosbag2_py import SequentialReader, StorageOptions, ConverterOptions
from cv_bridge import CvBridge
import cv2
from sensor_msgs.msg import Image, PointCloud2
from rclpy.serialization import deserialize_message
from numpy.lib.recfunctions import structured_to_unstructured
import sensor_msgs_py.point_cloud2 as pc2
import data_transforms
from pointnet2_ops import pointnet2_utils

tensor_transform = transforms.Compose(
    [
        transforms.ToTensor(),
    ]
)

transform = transforms.Compose(
    [
        data_transforms.PointcloudScaleAndTranslate(),
    ]
)

saliency_transform = transforms.Compose([
    # transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5], std=[0.5])
])

x_max = 30
x_min = -50
y_limit = 30
z_limit = 10

nn_linear=0.1
nn_angular=0.0
driving_mode=0
speed_multi=4.0
padding = 4300
npoints = 3072
points_all = 4300

# Transformation matrices to base_link frame
# translation: (x, y, z)(1.689, 0, 0.9),
# rotation: (r, p, y) (0, 8, 0)
front_LiDAR_transformation_matrix = np.array([
    [np.cos(np.deg2rad(8)), 0, np.sin(np.deg2rad(8)), 1.689],
    [0, 1, 0, 0],
    [-np.sin(np.deg2rad(8)), 0, np.cos(np.deg2rad(8)), 0.9],
    [0, 0, 0, 1]]
    )
# translation: (x, y, z)(-1.689, 0, 0.9),
# rotation: (r, p, y) (0, -8, 180))
rear_LiDAR_transformation_matrix = np.array([
    [-np.cos(np.deg2rad(8)), 0, np.sin(np.deg2rad(8)), -1.689],
    [0, -1, 0, 0],
    [-np.sin(np.deg2rad(8)), 0, np.cos(np.deg2rad(8)), 0.9],
    [0, 0, 0, 1]
])

if __name__ == "__main__":
    #load image
    parser = argparse.ArgumentParser("Load model from checkpoint")
    parser.add_argument("--load_model", action="store_true")
    parser.add_argument("model_name", default="pointMamba_shuttle_lane_following_48_0.0009_0.7621_0.8276.pth", type=str, nargs='?')
    parser.add_argument("model_type", default="lane_following", type=str, nargs='?')

    args = parser.parse_args()

    print(args.model_name)
    print(args.model_type)

    bag_path = "/media/quirky/QuirkySSD/ROSbags for analysis/16Aug/rosbag2_2025_08_16-15_11_50"
    target_topic1 = "/CameraFront"
    target_topic2 = "/lidar/velodyne/front/cloud"
    target_topic3 = "/lidar/velodyne/rear/cloud"

    storage_options = StorageOptions(uri=bag_path, storage_id='mcap')
    converter_options = ConverterOptions(input_serialization_format='cdr', output_serialization_format='cdr')

    reader = SequentialReader()
    reader.open(storage_options, converter_options)

    topics_and_types = reader.get_all_topics_and_types()
    topic_type_dict = {t.name: t.type for t in topics_and_types}

    bridge = CvBridge()

    device = "cuda" if torch.cuda.is_available() else "cpu"

    torch.manual_seed(1234)
    np.random.seed(1234)
    random.seed(1234)
    if device == "cuda":
        torch.cuda.manual_seed_all(1234)

    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    torch.set_float32_matmul_precision('high')

    model = drivePointMamba(
        trans_dim=512,
        depth=12,
        cls_dim= 40,
        group_size= 32,
        num_group= 64,
        encoder_dims= 512,
        rms_norm= False,
        drop_path= 0.1,
        drop_out= 0.1,
        drop_out_block= 0.1,
        use_cls_token=False,
    )

    model.load_state_dict(torch.load(args.model_name, weights_only=True)['model_state_dict'])

    model.eval()
    model.to(device)


    model_name = args.model_type

    while reader.has_next():
        
        (topic, data, t) = reader.read_next()
        if topic == target_topic1:
            msg_type_str = topic_type_dict[topic]
            if msg_type_str != 'sensor_msgs/msg/Image':
                print(f"Topic {topic} is of type {msg_type_str}, not sensor_msgs/msg/Image. Skipping.")
                continue

            msg = deserialize_message(data, Image)

            try:
                current_image = bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
            except Exception as e:
                print(f"Failed to convert image: {e}")

        if topic == target_topic2:
            msg_type_str = topic_type_dict[topic]
            if msg_type_str != 'sensor_msgs/msg/PointCloud2':
                print(f"Topic {topic} is of type {msg_type_str}, not sensor_msgs/msg/PointCloud2. Skipping.")
                continue

            msg = deserialize_message(data, PointCloud2)

            current_front_lidar = structured_to_unstructured(pc2.read_points(
                msg, field_names=("x", "y", "z", "intensity"), skip_nans=True))
            
        if topic == target_topic2:
            msg_type_str = topic_type_dict[topic]
            if msg_type_str != 'sensor_msgs/msg/PointCloud2':
                print(f"Topic {topic} is of type {msg_type_str}, not sensor_msgs/msg/PointCloud2. Skipping.")
                continue

            msg = deserialize_message(data, PointCloud2)

            current_rear_lidar = structured_to_unstructured(pc2.read_points(
                msg, field_names=("x", "y", "z", "intensity"), skip_nans=True))



        if current_front_lidar != None and current_rear_lidar != None and current_image != None:

            # print("no error")
            # print(previous_data)
            front_lidar = np.delete(current_front_lidar, -1, axis=1)
            rear_lidar = np.delete(current_rear_lidar, -1, axis=1)

            front_ones = np.ones((front_lidar.shape[0], 1))
            front_point_cloud_h = np.hstack([front_lidar, front_ones])  # Shape: (N, 4)
            rear_ones = np.ones((rear_lidar.shape[0], 1))
            rear_point_cloud_h = np.hstack([rear_lidar, rear_ones])  # Shape: (N, 4)

            front_lidar = (front_LiDAR_transformation_matrix @ front_point_cloud_h.T).T  # Shape: (N, 4)
            rear_lidar = (rear_LiDAR_transformation_matrix @ rear_point_cloud_h.T).T    # Shape: (N, 4)

            f_x, f_y, f_z = front_lidar[:, 0], front_lidar[:, 1], front_lidar[:, 2]
            r_x, r_y, r_z = rear_lidar[:, 0], rear_lidar[:, 1], rear_lidar[:, 2]

            front_mask = (f_x > x_min) & (f_x < x_max) & (np.abs(f_y) < y_limit) & (f_z < z_limit)
            rear_mask = (r_x > x_min) & (r_x < x_max) & (np.abs(r_y) < y_limit) & (r_z < z_limit)

            front_cropped_points = front_lidar[front_mask, :3]  # Shape: (M, 3)
            rear_cropped_points = rear_lidar[rear_mask, :3]

            if len(front_cropped_points) > padding:
                # Random sampling
                indices = np.random.choice(len(front_cropped_points), padding, replace=False)
                front_cropped_points = front_cropped_points[indices]

            if len(rear_cropped_points) > padding:
                # Random sampling
                indices = np.random.choice(len(rear_cropped_points), padding, replace=False)
                rear_cropped_points = rear_cropped_points[indices]

            front_lidar = tensor_transform(front_cropped_points)
            front_lidar = transform(front_lidar)
            filler = torch.zeros(1,(padding - front_lidar.size(1)), 3)
            front_lidar = torch.cat((front_lidar, filler), 1)
            front_lidar = torch.squeeze(front_lidar)
            rear_lidar = tensor_transform(rear_cropped_points)
            rear_lidar = transform(rear_lidar)
            filler = torch.zeros(1,(padding - rear_lidar.size(1)), 3)
            rear_lidar = torch.cat((rear_lidar, filler), 1)
            rear_lidar = torch.squeeze(rear_lidar)

            if front_lidar.size(1) < points_all:
                points_all = front_lidar.size(1)


            if front_lidar.dtype != torch.float32:
                front_lidar = front_lidar.float()


            fps_idx = pointnet2_utils.furthest_point_sample(front_lidar, points_all)
            fps_idx = fps_idx[:, np.random.choice(points_all, npoints, False)]
            front_lidar = pointnet2_utils.gather_operation(front_lidar.transpose(1, 2).contiguous(), fps_idx).transpose(1, 2).contiguous()
    
            if rear_lidar.dtype != torch.float32:
                rear_lidar = rear_lidar.float()

            fps_idx = pointnet2_utils.furthest_point_sample(rear_lidar, points_all)
            fps_idx = fps_idx[:, np.random.choice(points_all, npoints, False)]
            rear_lidar = pointnet2_utils.gather_operation(rear_lidar.transpose(1, 2).contiguous(), fps_idx).transpose(1, 2).contiguous()

            front_lidar = front_lidar.to(device="cuda")
            rear_lidar = rear_lidar.to(device="cuda")


            cropped_img = current_image[60:, 40:440]
            cropped_img = Image.fromarray(np.uint8(cropped_img), mode='L')

            saliency_img = cropped_img.copy()

            cropped_img = transform(cropped_img)
            cropped_img = rearrange(cropped_img, "c h w -> 1 c h w")
            cropped_img = cropped_img.to(device)

            # print(Speed)
            # print(Steering_Angle)

            target = None

            with torch.no_grad():

                #pass image to model
                if current_model == 0:
                    output1, output2 = model(front_lidar, rear_lidar)


            output1 = output1.item() * 5.4
            output2 = output2.item() * 0.3
            output1 = output1.detach().cpu().numpy()[0]
            output2 = output2.detach().cpu().numpy()[0]
            # print(Steering_Angle)

            Speed = Speed * 5.4
            Steering_Angle = Steering_Angle * 0.3
            

            print(output1)
            print(output2)
            print(Speed)
            print(Steering_Angle)
            print(f"current driving mode is: {data[4]}")

            #draw ground truth
            # x1 = [160, 160 + ((Steering_Angle * 20) / 0.3)]
            x1 = (210, 220)
            y1 = (int(210 - ((Steering_Angle * 20) / 0.3)), int(220 - ((Speed * 60) / 5.4)))
            # y1 = [190, 190 - ((Speed * 20) / 5.4)]
            
            #draw model output
            # x2 = [180, 180 + ((output2 * 20) / 0.3)]
            # y2 = [190, 190 - ((output1 * 20) / 5.4)]
            x2 = (270, 220)
            y2 = (int(270 - ((output2 * 20) / 0.3)), int(220 - ((output1 * 60) / 5.4)))

            # plt.plot(x1, y1, x2, y2, color="white", linewidth=5)
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            cv2.line(img, x1, y1, (0, 255, 0), 5)
            cv2.line(img, x2, y2, (255, 0, 255), 5)
            cv2.imshow('ground truth comparison', img)
        

            #display image
            # plt.imshow(img, cmap='gray')

            #use keys to get next image
            # cv2.waitKey(0)
            # print("waiting for key input")
            current_image = None
            current_front_lidar = None
            current_rear_lidar = None
            k = cv2.waitKey(0)
            # print(k)
            if k == 115:

                ###################### saliency straight #########################

                input_tensor = saliency_transform(saliency_img).unsqueeze(0).to(device)
                input_tensor.requires_grad_()
                target = None

                #pass image to model
                if current_model == 0:
                    saliency_output1, saliency_output2 = model(input_tensor)
                    target = saliency_output1[0, 0] if saliency_output1.dim() == 2 else saliency_output1.squeeze()

                    # Backward pass: compute gradients of output w.r.t. input image
                    model.zero_grad()
                    target.backward()

                saliency = input_tensor.grad.data.abs().squeeze(0).squeeze(0).cpu()   # shape: (3, 224, 224)

                # Original image: resized to match input shape and normalized back to [0, 1]
                original_resized = saliency_img
                original_np = np.array(original_resized) / 255.0  # shape: (224, 224), values in [0, 1]

                # Normalize saliency to [0, 1]
                saliency_np = saliency.numpy()
                saliency_norm = (saliency_np - saliency_np.min()) / (saliency_np.max() - saliency_np.min() + 1e-8)

                # Create a heatmap from the saliency map
                heatmap = cm.jet(saliency_norm)[..., :3]  # shape: (224, 224, 3), ignore alpha channel

                # Convert grayscale to RGB for overlay
                original_rgb = np.stack([original_np]*3, axis=-1)

                # Blend heatmap with original image
                overlay = 0.5 * original_rgb + 0.5 * heatmap
                overlay = np.clip(overlay, 0, 1)
                cv2.namedWindow('Linear Saliency', cv2.WINDOW_NORMAL)
                overlay = cv2.resize(overlay, dsize=(480,240), interpolation=cv2.INTER_CUBIC)
                cv2.resizeWindow('Linear Saliency', 500, 300)

                cv2.imshow('Linear Saliency', overlay)


                ###################### saliency turning #########################

                input_tensor2 = saliency_transform(saliency_img).unsqueeze(0).to(device)
                input_tensor2.requires_grad_()
                target2 = None

                #pass image to model
                if current_model == 0:
                    saliency_output1, saliency_output2 = model(input_tensor2)
                    target2 = saliency_output2[0, 0] if saliency_output2.dim() == 2 else saliency_output2.squeeze()

                    # Backward pass: compute gradients of output w.r.t. input image
                    model.zero_grad()
                    target2.backward()

                saliency2 = input_tensor2.grad.data.abs().squeeze(0).squeeze(0).cpu()   # shape: (3, 224, 224)

                # Original image: resized to match input shape and normalized back to [0, 1]
                original_resized2 = saliency_img
                original_np2 = np.array(original_resized2) / 255.0  # shape: (224, 224), values in [0, 1]

                # Normalize saliency to [0, 1]
                saliency_np2 = saliency2.numpy()
                saliency_norm2 = (saliency_np2 - saliency_np2.min()) / (saliency_np2.max() - saliency_np2.min() + 1e-8)

                # Create a heatmap from the saliency map
                heatmap2 = cm.jet(saliency_norm2)[..., :3]  # shape: (224, 224, 3), ignore alpha channel

                # Convert grayscale to RGB for overlay
                original_rgb2 = np.stack([original_np2]*3, axis=-1)

                # Blend heatmap with original image
                overlay2 = 0.5 * original_rgb2 + 0.5 * heatmap2
                overlay2 = np.clip(overlay2, 0, 1)
                cv2.namedWindow('Rotational Saliency', cv2.WINDOW_NORMAL)
                overlay2 = cv2.resize(overlay2, dsize=(480,240), interpolation=cv2.INTER_CUBIC)
                cv2.resizeWindow('Rotational Saliency', 500, 300)

                cv2.imshow('Rotational Saliency', overlay2)

                k = cv2.waitKey(0)

            if k == 113:
                cv2.destroyAllWindows()
                break
            elif k == 83:
            #     current_file += 1
            #     if current_file > (len(os.listdir(selected_bag))-1):
            #         current_file = (len(os.listdir(selected_bag))-1)
                continue
            # elif k == 81:
            #     current_file -= 1
            #     if current_file < 10:
            #         current_file = 10
                # continue
            # elif k == 82:
            #     current_file += 20
            #     if current_file > (len(os.listdir(selected_bag))-1):
            #         current_file = (len(os.listdir(selected_bag))-1)
                # continue
            # elif k == 84:
            #     current_file -= 20
            #     if current_file < 10:
            #         current_file = 10
            #     continue
            # elif k == 114:
            #     current_model = 3
            #     continue
            # # elif k == 102:
            # #     current_model = 1
            #     continue
            # elif k == 112:
            #     current_model = 2
            #     continue
            elif k == 108:
                current_model = 0
                continue
            # elif k == 99:
            #     # random_category = random.randint(0, len(All_Searchable_Folders)-1)
            #     # category_file = join(All_Searchable_Folders, All_Searchable_Folders[random_category])
            #     # random_bag = random.randint(0, len(os.listdir(category_file))-1)
            #     random_bag = random.randint(0, len(os.listdir(All_Searchable_Folders[0])))
            #     current_file = 0
            #     continue
            
            # elif k == :
            #     random_bag = random.randint(0, len(All_Searchable_Folders))
            #     current_file = 0
            #     continue
            else:
                continue