import torch
from torch import nn
import torch.nn.functional as F
from functools import partial

from torchvision import datasets, models, transforms
from PIL import Image

from einops import rearrange, repeat
from einops.layers.torch import Rearrange
from model import PointMamba

from torch.utils.tensorboard import SummaryWriter

import numpy as np

#import cv2
import os
import sys
from os.path import join, exists, dirname, abspath

from sklearn.model_selection import train_test_split

import torch.optim as optim
from torch.optim.lr_scheduler import StepLR, ReduceLROnPlateau #, CosLR
import argparse
#from torchsummary import summary
import time
import random

import data_transforms

from pointnet2_ops import pointnet2_utils

writer = SummaryWriter()

Point_All = []
Speeds_All = []
Steering_Angles_All = []

def pair(t):

    return t if isinstance(t, tuple) else (t,t)

class drivePointMamba(nn.Module):
    def __init__(
            self,
            *,
            trans_dim=384,
            depth=12,
            cls_dim= 40,
            group_size= 32,
            num_group= 64,
            encoder_dims= 384,
            rms_norm= False,
            drop_path= 0.3,
            drop_out= 0.,
            drop_out_block= 0.,
            use_cls_token=False,
    ):
        super().__init__()

        # image_height, image_width = pair(img_size)
        # patch_height, patch_width = pair(patch_size)

        # assert pool in {
        #     "cls",
        #     "mean",
        # }, "pool type must be either cls (cls token) or mean (mean pooling)"

        # num_patches = (image_height // patch_height) * (image_width // patch_width)
        # patch_dim = channels * patch_height * patch_width
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        # self.device = "cpu"

        self.vision_model = PointMamba(
                 trans_dim=trans_dim,
                 depth=depth,
                 cls_dim= cls_dim,
                 group_size= group_size,
                 num_group= num_group,
                 encoder_dims= encoder_dims,
                 rms_norm= rms_norm,
                 drop_path= drop_path,
                 drop_out= drop_out,
                 drop_out_block= drop_out_block,
                 use_cls_token=use_cls_token,
            
        )

        # self.pos_embedding = nn.Parameter(torch.randn(1, num_patches + 1, dim))
        # self.cls_token = nn.Parameter(torch.randn(1, 1, dim))
        # self.dropout = nn.Dropout(emb_dropout)

        # self.mamba = VisionMamba(dim, depth, heads, dim_head, mlp_dim, dropout)


        self.mlp_head1 = nn.Sequential(
                nn.Linear(cls_dim, int(cls_dim / 2)),
                nn.LayerNorm(int(cls_dim / 2)),
                nn.ELU(),
                nn.Linear(int(cls_dim / 2),  int(cls_dim / 4)),
                nn.LayerNorm(int(cls_dim / 4)),
                nn.ELU(),
                nn.Linear(int(cls_dim / 4),  int(cls_dim / 8)),
                nn.LayerNorm(int(cls_dim / 8)),
                nn.ELU(),
                nn.Linear(int(cls_dim / 8), 1)).to(device=self.device)
        
        self.mlp_head2 = nn.Sequential(
                nn.Linear(cls_dim, int(cls_dim / 2)),
                nn.LayerNorm(int(cls_dim / 2)),
                nn.ELU(),
                nn.Linear(int(cls_dim / 2),  int(cls_dim / 4)),
                nn.LayerNorm(int(cls_dim / 4)),
                nn.ELU(),
                nn.Linear(int(cls_dim / 4),  int(cls_dim / 8)),
                nn.LayerNorm(int(cls_dim / 8)),
                nn.ELU(),
                nn.Linear(int(cls_dim / 8), 1)).to(device=self.device)

    def forward(self, front_cloud, rear_cloud):
        # print(front_cloud.shape)
        # front_cloud = torch.squeeze(front_cloud).float()
        # rear_cloud = torch.squeeze(rear_cloud).float()
        # print(front_cloud[0])
        # print(rear_cloud[0])

        # print(front_cloud.shape)
        # print(rear_cloud.shape)

        full_lidar = torch.concat([front_cloud, rear_cloud], axis=1).float()
        # print(full_lidar[0])
        # print(full_lidar.shape)
        x = self.vision_model(full_lidar)
        b, n = x.shape

        speed = self.mlp_head1(x)
        angle = self.mlp_head2(x)
        # print(x.shape)
        return speed[:,0], angle[:,0]
        # return x

padding = 4300

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

class dataset(torch.utils.data.Dataset):
    def __init__(self, file_list1, file_list2, label_list1, label_list2, transform=None):
        self.file_list1 = file_list1
        self.file_list2 = file_list2
        self.label_list1 = label_list1
        self.label_list2 = label_list2
        self.transform = transform

    def __len__(self):
        self.filelength = len(self.file_list1)
        return self.filelength

    def __getitem__(self, idx):
        front_lidar = self.file_list1[idx]
        rear_lidar = self.file_list2[idx]
        label1 = self.label_list1[idx]
        label2 = self.label_list2[idx]
        

        front_lidar = self.transform(front_lidar)
        # print(front_lidar.shape)
        filler = torch.zeros(1,(padding - front_lidar.size(1)), 3)
        front_lidar = torch.cat((front_lidar, filler), 1)
        front_lidar = torch.squeeze(front_lidar)
        # print(front_lidar.shape)
        # F.pad(front_lidar, (5000 - front_lidar.size(1)), "constant", torch.empty(4))
        # print(front_lidar.shape)
        rear_lidar = self.transform(rear_lidar)
        filler = torch.zeros(1,(padding - rear_lidar.size(1)), 3)
        rear_lidar = torch.cat((rear_lidar, filler), 1)
        rear_lidar = torch.squeeze(rear_lidar)
        return front_lidar, rear_lidar, label1, label2
    
def collate_fn(batch):
    # print("batch data looks like ")
    # print(batch[0])
    # print(len(batch))
    data1 = torch.stack([item[0] for item in batch])
    # data1 = tensor_transform(data1)
    data2 = torch.stack([item[1] for item in batch])
    # data2 = tensor_transform(data2)
    label1 = [item[2] for item in batch]
    label2 = [item[3] for item in batch]
    return data1, data2, label1, label2

def load_latest_data(Search_Folder):
        
    try:
        data = np.load(Search_Folder, allow_pickle=True)
    except EOFError:
        return
    except:
        # print("skipping file in {}: {}", Search_Folder, Files)
        return

    # convertLidarData.py writes: [front_points, rear_points, vel_arr, steer_arr, img_front, map_pos_orien_topic]
    #                                    0              1          2         3        4              5
    Speed = data[2][0]
    # print(f"speed value is: {Speed}")
    Steering_Angle = data[3][0]
    # print(f"Steering_Angle value is: {Steering_Angle}")
    front_lidar = np.delete(data[0], -1, axis=1)
    # print(np.delete(data[0], -1, axis=1))
    # bleh
    rear_lidar = np.delete(data[1], -1, axis=1)

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

    # print(front_cropped_points)
    # print(rear_cropped_points)

    try:
        if Speed == None:
            # print(join(Search_Folder, Files))
            return
        if Steering_Angle == None:
            # print(join(Search_Folder, Files))
            return
        # if front_cropped_points == None:
        #     # print(join(Search_Folder, Files))
        #     # print(Files)
        #     return
        # if rear_cropped_points == None:
        #     # print(join(Search_Folder, Files))
        #     # print(Files)
        #     return
    except:
        print(Speed)
        print(Steering_Angle)
        print(Search_Folder)

    # add image shifting here
    # print(len(front_cropped_points))
    # if len(front_lidar) > padding:
    #     padding = len(front_lidar)
    # if len(rear_lidar) > padding:
    #     padding = len(rear_lidar)
    if len(front_cropped_points) > padding:
        # Random sampling
        indices = np.random.choice(len(front_cropped_points), padding, replace=False)
        front_cropped_points = front_cropped_points[indices]


    if len(rear_cropped_points) > padding:
        # Random sampling
        indices = np.random.choice(len(rear_cropped_points), padding, replace=False)
        rear_cropped_points = rear_cropped_points[indices]




    Front_lidar_all.append(front_cropped_points)
    Rear_lidar_all.append(rear_cropped_points)
    # Image_all.append(image)
    Speeds_All.append(Speed)
    Steering_Angles_All.append(Steering_Angle)

rear_LiDAR_transformation_matrix = np.array([
    [np.cos(np.deg2rad(8)), 0, np.sin(np.deg2rad(8)), 1.689],
    [0, 1, 0, 0],
    [-np.sin(np.deg2rad(8)), 0, np.cos(np.deg2rad(8)), 0.9],
    [0, 0, 0, 1]]
    )
front_LiDAR_transformation_matrix = np.array([
    [-np.cos(np.deg2rad(8)), 0, -np.sin(np.deg2rad(8)), -1.689],
    [0, -1, 0, 0],
    [-np.sin(np.deg2rad(8)), 0, np.cos(np.deg2rad(8)), 0.9],
    [0, 0, 0, 1]
])

x_max = 20
x_min = -20
y_min = -20
y_max = 20
y_limit = 20
z_limit = 30

if __name__ == "__main__":
    lr = 1e-4
    weight_decay = 0.05
    gamma = 0.8
    batch_size = 70
    npoints = 3072
    points_all = 4300
    best_loss = 100000

    model_path_name = "pointMamba_shuttle_lane_following_48_0.0009_0.7621_0.8276.pth"
    checkpoint = None

    parser = argparse.ArgumentParser("Load model from checkpoint")
    parser.add_argument("--load_model", action="store_true")
    parser.add_argument("--fine_tune_model", action="store_true")
    parser.add_argument("model_type", default="lane_following", type=str, nargs='?')


    model = drivePointMamba(
        trans_dim=512,
        depth=12,
        cls_dim=1000,
        group_size= 32,
        num_group= 64,
        encoder_dims= 512,
        rms_norm= False,
        drop_path= 0.1,
        drop_out= 0.1,
        drop_out_block= 0.1,
        use_cls_token=False,
    )

    # img = torch.randn(1, 3, 200, 66)

    args = parser.parse_args()

    if args.load_model:
        print("loading model")
        checkpoint = torch.load(model_path_name, weights_only=True)
        
        model.load_state_dict(checkpoint['model_state_dict'])
    elif args.fine_tune_model:
        print("fine tuning model")
        checkpoint = torch.load(model_path_name, weights_only=True)
        model.load_state_dict(checkpoint['model_state_dict'])

    Front_lidar_all = []
    Rear_lidar_all = []
    # Image_all = []
    Speeds_All = []
    Steering_Angles_All = []

    if args.fine_tune_model:
        model_name = args.model_type + '_finetune'
    else:
        model_name = args.model_type
    print(model_name)

    if args.fine_tune_model:
        lane_follow_files = [
            "lane_bay_pass",
            "roundabout_straight",
            # "lane_following",
            "intersection_lane_following",
            "startpoint_out",
            "startpoint_in",
            "carpark_pass",
            "roundabout_right_turn",
            "lane_empty_bay",
            "lane_empty_bay_first_half",
            "lane_empty_bay_second_half",
            "pullout",
        ]
    else:
        lane_follow_files = [
            "lane_bay_pass",
            "roundabout_straight",
            "lane_following",
            "intersection_lane_following",
            "startpoint_out",
            "startpoint_in",
            "carpark_pass",
            "roundabout_right_turn",
            "lane_empty_bay",
            "lane_empty_bay_first_half",
            "lane_empty_bay_second_half",
            "pullout",
        ]

    pullin_files = [
        # "lane_following", #reduce the amount
        "pullin",
        # "roundabout_turn_around_to_office",
        # "intersection_turn_around_to_office",
        # "startpoint_out",
        # "startpoint_in",
        # "carpark_entry",
        # "roundabout_right_turn",
        "pullin_stops",
        # "carpark_left_turn_in",
        # "carpark_left_turn_out"
    ]

    reverse_files = [
        # "lane_following",
        "reverse",
        # "roundabout_turn_around_to_beach",
        # "roundabout_turn_around_to_office",
        # "startpoint_out",
        # "startpoint_in",
        # "carpark_entry",
        # "roundabout_right_turn",
        "pullout_stops",
        "reverse_manual",
        # "carpark_left_turn_in",
        # "carpark_left_turn_out"
    ]

    All_Searchable_Folders = []

    # Base_Path should point at convertLidarData.py's output_folder_path — the parent
    # directory containing one subfolder per converted .mcap bag (each full of .npy frames).
    # With only 3 bags there's no maneuver-based folder filtering to do; just take everything.
    Base_Path = "/home/ubuntu22/jeremybutson/output"

    for bag_output_folder in os.listdir(Base_Path):
        Search_Folder = join(Base_Path, bag_output_folder)
        if os.path.isdir(Search_Folder):
            for file in os.listdir(Search_Folder):
                if file.endswith(".npy"):
                    All_Searchable_Folders.append(join(Search_Folder, file))

    random.shuffle(All_Searchable_Folders)    

    # criterion = nn.MSELoss()
    criterion = nn.L1Loss()
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    if args.load_model:
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        for param_group in optimizer.param_groups:
            current_lr = param_group['lr']
            new_lr = current_lr * 0.9
            param_group['lr'] = new_lr
            print(f"LR updated: {current_lr:.8f} → {new_lr:.8f}")
    # scheduler = StepLR(optimizer, step_size=10, gamma=gamma)
    scheduler = ReduceLROnPlateau(optimizer, 'min', factor=gamma, patience=3, threshold=0.0001, threshold_mode='abs', verbose=True)

    device = "cuda" if torch.cuda.is_available() else "cpu"

    epochs = 50
    use_amp = True

    if args.load_model:
        start_epoch = checkpoint["epoch"] + 1
    else:
        start_epoch = 0


    print(len(All_Searchable_Folders))

    current_time = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())

    print(f'training started at: {current_time}')
    start_time = time.time()

    for epoch in range(start_epoch, epochs):
        total_epoch_loss = 0
        total_epoch_val_loss = 0
        total_epoch_accuracy1 = 0
        total_epoch_accuracy2 = 0
        total_epoch_val_accuracy1 = 0
        total_epoch_val_accuracy2 = 0
        temp_search = All_Searchable_Folders.copy()
        train_len = 0
        val_len = 0
        batch = 0
        straight_count = 0
        turning_count = 0

        while len(temp_search) != 0:
            epoch_loss = 0
            epoch_accuracy1 = 0
            epoch_accuracy2 = 0

            while (len(Front_lidar_all) < 30000) and len(temp_search) != 0:
                current_folder = temp_search.pop()

                load_latest_data(current_folder)
            
                # print(len(Images_All))
            # print(len(temp_search))
            # print(len(All_Searchable_Folders))
            # print(len(Images_All))
            print((len(temp_search)/len(All_Searchable_Folders))*100)

            Split_a = train_test_split(Front_lidar_all, Rear_lidar_all, Speeds_All, Steering_Angles_All, test_size=0.1, shuffle=True)
            (Front_clouds, Front_clouds_Test, Rear_clouds, Rear_clouds_Test, Speeds, Speed_Test, Steering_Angles, Steering_Angle_Test) = Split_a   
            Split_b = train_test_split(Front_clouds, Rear_clouds, Speeds, Steering_Angles, test_size=0.2, shuffle=True)
            (Front_clouds_Train, Front_clouds_Valid, Rear_clouds_Train, Rear_clouds_Valid, Speed_Train, Speed_Valid, Steering_Angle_Train, Steering_Angle_Valid) = Split_b

            train_data = dataset(Front_clouds_Train, Rear_clouds_Train, Speed_Train, Steering_Angle_Train, transform=tensor_transform)
            test_data = dataset(Front_clouds_Test, Rear_clouds_Test, Speed_Test, Steering_Angle_Test, transform=tensor_transform)
            val_data = dataset(Front_clouds_Valid, Rear_clouds_Valid, Speed_Valid, Steering_Angle_Valid, transform=tensor_transform)

            train_loader = torch.utils.data.DataLoader(
                dataset=train_data, batch_size=batch_size, shuffle=True, drop_last=True, collate_fn=collate_fn
            )
            test_loader = torch.utils.data.DataLoader(
                dataset=test_data, batch_size=batch_size, shuffle=True, collate_fn=collate_fn
            )
            val_loader = torch.utils.data.DataLoader(
                dataset=val_data, batch_size=batch_size, shuffle=True, collate_fn=collate_fn
            )

            train_len += len(train_loader.dataset)
            val_len += len(val_loader.dataset)

        # print("length of data trainer is ")
        # print(train_loader)

        # for data1, data2, label1, label2 in train_loader:
            for data1, data2, label1, label2 in train_loader:

                data1 = data1.to(device="cuda")
                data2 = data2.to(device="cuda")
                # label1.to(device)
                # label2.to(device)
                
                # print(len(front_lidar))
                # print("The data given is")
                # data1 = torch.Tensor(data1)
                # print(len(data1[1]))
                # data1 = torch.stack(data1)
                # print(data1[0].size(1))
                # # print(data1.shape)
                # print(data1.shape)
                # print(data2.shape)
                # print("The labels are")
                # print(label1)
                # print(label2)

                # print("now processing the data")

                # front_lidar = tensor_transform(front_lidar).to("cuda")
                if data1.size(1) < points_all:
                        points_all = data1.size(1)

                # front_lidar = torch.squeeze(front_lidar)
                # front_lidar = front_lidar[:, :, :3].contiguous()

                

                if data1.dtype != torch.float32:
                    data1 = data1.float()

                # print(f"points all is: {points_all}")
                # print(f"data1 is {data1}")

                fps_idx = pointnet2_utils.furthest_point_sample(data1, points_all)
                # print(fps_idx.shape)
                fps_idx = fps_idx[:, np.random.choice(points_all, npoints, False)]
                # print(fps_idx.shape)
                data1 = pointnet2_utils.gather_operation(data1.transpose(1, 2).contiguous(), fps_idx).transpose(1, 2).contiguous()
                # print(data1.shape)
                # front_lidar = transform(data1)

                # rear_lidar = tensor_transform(rear_lidar).to("cuda")
                # if len(rear_lidar) < points_all:
                #         points_all = len(rear_lidar)

                # rear_lidar = rear_lidar[:, :, :3].contiguous()
                if data2.dtype != torch.float32:
                    data2 = data2.float()

                fps_idx = pointnet2_utils.furthest_point_sample(data2, points_all)
                fps_idx = fps_idx[:, np.random.choice(points_all, npoints, False)]
                data2 = pointnet2_utils.gather_operation(data2.transpose(1, 2).contiguous(), fps_idx).transpose(1, 2).contiguous()
            # for i in range (0, len(Image_Train)):
                # data = Image_Train[i]
                # speed = Speed_Train[i]
                # angle = Steering_Angle_Train[i]
                data1 = data1.to(device)
                data2 = data2.to(device)

                # if data1.size(1) < points_all:
                #     points_all = data1.size(1)

                # fps_idx = pointnet2_utils.furthest_point_sample(data1, points_all)
                # fps_idx = fps_idx[:, np.random.choice(points_all, npoints, False)]
                # data1 = pointnet2_utils.gather_operation(data1.transpose(1, 2).contiguous(), fps_idx).transpose(1, 2).contiguous()
                # data1 = transform(data1)
                # print(data1.shape)
                # print(label1)
                # label1 = torch.stack(label1)
                # label2 = torch.stack(label2)
                label1 = torch.FloatTensor(label1)
                label2 = torch.FloatTensor(label2)
                label1 = label1.to(device)
                label2 = label2.to(device)
                # print(data.shape)

                output1, output2 = model(data1, data2)
                # print(output1.shape)
                # print(label1.shape)
                loss1 = criterion(output1, label1)
                loss2 = criterion(output2, label2)

                loss = loss1 + loss2

                total_epoch_loss += loss.item()

                # writer.add_scalar("Loss/Train", loss, epoch)

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                acc1 = (abs(output1 - label1) < (0.27 / 5.4)).float().sum()
                acc2 = (abs(output2 - label2) < (0.015 / 0.3)).float().sum()
                epoch_accuracy1 += acc1
                epoch_accuracy2 += acc2
                epoch_loss += loss.item()

            total_epoch_accuracy1 += epoch_accuracy1
            total_epoch_accuracy2 += epoch_accuracy2
            epoch_accuracy1 = epoch_accuracy1 / len(train_loader.dataset)
            epoch_accuracy2 = epoch_accuracy2 / len(train_loader.dataset)
            epoch_loss = epoch_loss / len(train_loader.dataset)

            with torch.no_grad():
                epoch_val_accuracy1 = 0
                epoch_val_accuracy2 = 0
                epoch_val_loss = 0
                # for i in range(0, len(Image_Valid)): 
                for data1, data2, label1, label2 in val_loader:
                    # data = Image_Valid[i]
                    # speed = Speed_Valid[i]
                    # angle = Steering_Angle_Valid[i]
                    data1 = data1.to(device)
                    data2 = data2.to(device)
                    label1 = torch.FloatTensor(label1)
                    label2 = torch.FloatTensor(label2)
                    label1 = label1.to(device)
                    label2 = label2.to(device)

                    val_output1, val_output2 = model(data1, data2)
                    val_loss1 = criterion(val_output1, label1)
                    val_loss2 = criterion(val_output2, label2)

                    val_loss = val_loss1 + val_loss2
                    total_epoch_val_loss += val_loss.item()

                    acc1 = (abs(val_output1 - label1) < (0.54 / 5.4)).float().sum()
                    acc2 = (abs(val_output2 - label2) < (0.03 / 0.3)).float().sum()
                    epoch_val_accuracy1 += acc1
                    epoch_val_accuracy2 += acc2
                    epoch_val_loss += val_loss.item()

                total_epoch_val_accuracy1 += epoch_val_accuracy1
                total_epoch_val_accuracy2 += epoch_val_accuracy2
                epoch_val_accuracy1 = epoch_val_accuracy1 / len(val_loader.dataset)
                epoch_val_accuracy2 = epoch_val_accuracy2 / len(val_loader.dataset)
                epoch_val_loss = epoch_val_loss / len(val_loader.dataset)


            batch += 1
            Front_lidar_all = []
            Rear_lidar_all = []
            Speeds_All = []
            Steering_Angles_All = []
            del train_data, train_loader, val_data, val_loader, test_data, test_loader

        total_epoch_accuracy1 = total_epoch_accuracy1 / train_len
        total_epoch_accuracy2 = total_epoch_accuracy2 / train_len
        total_epoch_loss = total_epoch_loss / train_len
        total_epoch_val_accuracy1 = total_epoch_val_accuracy1 / val_len
        total_epoch_val_accuracy2 = total_epoch_val_accuracy2 / val_len
        total_epoch_val_loss = total_epoch_val_loss / val_len
        writer.add_scalar("Loss/Train", total_epoch_loss, epoch)
        writer.add_scalar("Loss/Validation", total_epoch_val_loss, epoch)
        writer.add_scalar("accuracy1/Train", total_epoch_accuracy1, epoch)
        writer.add_scalar("accuracy2/Train", total_epoch_accuracy2, epoch)
        writer.add_scalar("accuracy1/Validation", total_epoch_val_accuracy1, epoch)
        writer.add_scalar("accuracy2/Validation", total_epoch_val_accuracy2, epoch)

        print(
            "Total Epoch : {} values, accuracy1 : {}, accuracy2 : {}, loss : {}".format(
                epoch + 1, total_epoch_accuracy1, total_epoch_accuracy2, total_epoch_loss
            )
        )
        print(
            "Total Epoch : {} values, val_accuracy1 : {}, val_accuracy2 : {}, val_loss : {}".format(
                epoch + 1, total_epoch_val_accuracy1, total_epoch_val_accuracy2, total_epoch_val_loss
            )
        )

        if best_loss > total_epoch_loss:
            best_loss = total_epoch_loss

            save_name = f"pointMamba_shuttle_{model_name}_{epoch+1}_{total_epoch_loss:.4f}_{total_epoch_accuracy1:.4f}_{total_epoch_accuracy2:.4f}.pth"

            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'loss': total_epoch_loss
            }, save_name)

        scheduler.step(total_epoch_val_loss)

        for i, param_group in enumerate(optimizer.param_groups):
            print(f"[Epoch {epoch}] LR group {i}: {param_group['lr']:.8f}")

        elapsed_time = time.time() - start_time
        start_time = time.time()

        print(f'Time elapsed: {elapsed_time}')

        # print(f"straight count: {straight_count}, turning count: {turning_count}")

    end_time = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())

    print(f'training finished at: {end_time}')

    torch.save(model.state_dict(), f'pointMamba_shuttle_{model_name}.pth')
    writer.flush()
    writer.close()