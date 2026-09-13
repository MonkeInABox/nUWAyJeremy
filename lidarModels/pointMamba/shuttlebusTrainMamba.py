import torch
from torch import nn
import torch.nn.functional as F
from functools import partial

from torchvision import datasets, models, transforms
from PIL import Image

from einops import rearrange, repeat
from einops.layers.torch import Rearrange
from driveModelMamba import drivePointMamba

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
import csv
from datetime import datetime

import data_transforms

from pytorch3d.ops import sample_farthest_points


def fps_downsample(points, n_fps, n_sample):
    """
    Farthest-point-sample `points` (B, N, C>=3) down to `n_fps` points, then
    randomly keep `n_sample` of those FPS-selected points.

    Uses pytorch3d instead of the original pointnet2_ops pipeline
    (furthest_point_sample + gather_operation) -- deliberately kept
    IDENTICAL to the PointCAM version's data pipeline, so any difference
    between the two models' results is attributable to the model, not to
    incidental differences in how point clouds get downsampled before
    reaching it.
    """
    _, fps_idx = sample_farthest_points(
        points[..., :3], K=n_fps, random_start_point=True
    )
    fps_idx = fps_idx[:, np.random.choice(n_fps, n_sample, replace=False)]
    return torch.gather(points, 1, fps_idx.unsqueeze(-1).expand(-1, -1, points.shape[-1]))

writer = SummaryWriter()

Point_All = []
Speeds_All = []
Steering_Angles_All = []

def pair(t):

    return t if isinstance(t, tuple) else (t,t)


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
    parser = argparse.ArgumentParser("Train the shuttle bus driving model")
    parser.add_argument("--load_model", action="store_true")
    parser.add_argument("--fine_tune_model", action="store_true")
    parser.add_argument("model_type", default="lane_following", type=str, nargs='?')

    # --- Hyperparameters exposed for sweeping --------------------------------
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--weight_decay", type=float, default=0.05)
    parser.add_argument("--gamma", type=float, default=0.8, help="ReduceLROnPlateau decay factor")
    parser.add_argument("--batch_size", type=int, default=70)
    parser.add_argument("--epochs", type=int, default=50)
    # PointMamba architecture params -- num_group/group_size are the direct
    # analogs of PointCAM's n_patches/points_per_patch (FPS centers + KNN
    # grouping), included under those original names for a fair comparison.
    parser.add_argument("--trans_dim", type=int, default=512)
    parser.add_argument("--depth", type=int, default=12)
    parser.add_argument("--cls_dim", type=int, default=1000, help="Pooled feature size fed into the speed/steering heads")
    parser.add_argument("--num_group", type=int, default=64, help="Number of FPS-selected groups (PointMamba's analog of n_patches)")
    parser.add_argument("--group_size", type=int, default=32, help="Points per group via KNN (PointMamba's analog of points_per_patch)")
    parser.add_argument("--encoder_dims", type=int, default=512)
    parser.add_argument("--rms_norm", action="store_true")
    parser.add_argument("--drop_path", type=float, default=0.1)
    parser.add_argument("--drop_out", type=float, default=0.1)
    parser.add_argument("--drop_out_block", type=float, default=0.1)
    parser.add_argument("--use_cls_token", action="store_true")
    parser.add_argument("--freeze_encoder", action="store_true", help="Freeze the PointMamba encoder weights")

    # --- Sweep bookkeeping -----------------------------------------------------
    parser.add_argument(
        "--results_csv", type=str, default="sweep_results.csv",
        help="CSV file this run's final metrics + hyperparameters get appended to",
    )
    parser.add_argument(
        "--run_name", type=str, default=None,
        help="Optional label for this run (first column in results_csv). Defaults to model_name.",
    )
    parser.add_argument(
        "--config_label", type=str, default=None,
        help="Sweep config identifier shared by all repeats of the same hyperparameter combo "
             "(e.g. 'lr_1e-3'). Written as its own results_csv column so repeats can be "
             "grouped/averaged without parsing run_name strings.",
    )
    parser.add_argument(
        "--repeat", type=int, default=1,
        help="Which repeat of config_label this run is (1, 2, 3, ...). Written as its own column.",
    )

    args = parser.parse_args()

    lr = args.lr
    weight_decay = args.weight_decay
    gamma = args.gamma
    batch_size = args.batch_size
    npoints = 3072
    points_all = 4300
    best_loss = 100000
    best_val_loss = 100000
    best_val_epoch = None

    model_path_name = "pointMamba_shuttle_lane_following_48_0.0009_0.7621_0.8276.pth"
    checkpoint = None

    model = drivePointMamba(
        trans_dim=args.trans_dim,
        depth=args.depth,
        cls_dim=args.cls_dim,
        group_size=args.group_size,
        num_group=args.num_group,
        encoder_dims=args.encoder_dims,
        rms_norm=args.rms_norm,
        drop_path=args.drop_path,
        drop_out=args.drop_out,
        drop_out_block=args.drop_out_block,
        use_cls_token=args.use_cls_token,
        freeze_encoder=args.freeze_encoder,
    )

    # img = torch.randn(1, 3, 200, 66)

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

    # CHECK THIS PATH -- it must point at wherever your converted LiDAR data
    # (the .npy output of convertLidarDataNew.py) currently lives. I've seen
    # this repo reference at least two different paths across our
    # conversation (output1008 and output2) -- confirm this matches whatever
    # your shuttlebusTrain.py (PointCAM) script is currently pointed at,
    # since that's the value that was actually working most recently.
    Base_Path = "/media/ubuntu22/RAID1/jeremy/baylissALLDATA"

    for bag_output_folder in os.listdir(Base_Path):
        Search_Folder = join(Base_Path, bag_output_folder)
        if os.path.isdir(Search_Folder):
            for file in os.listdir(Search_Folder):
                if file.endswith(".npy"):
                    All_Searchable_Folders.append(join(Search_Folder, file))

    # If your data is nested more than one folder deep under Base_Path
    # (e.g. Base_Path/session/sub_session/bag_output/*.npy rather than
    # Base_Path/bag_output/*.npy), the one-level search above finds
    # nothing even when the files genuinely exist. Fall back to a
    # recursive search at any depth before giving up.
    if len(All_Searchable_Folders) == 0:
        from pathlib import Path
        All_Searchable_Folders = [str(p) for p in Path(Base_Path).rglob("*.npy")]
        if All_Searchable_Folders:
            print(
                f"Note: found {len(All_Searchable_Folders)} .npy files via a recursive "
                f"search -- your data is nested deeper than one folder level under "
                f"Base_Path. Consider updating Base_Path or this search logic to "
                f"reflect that directly, this fallback is just here so training doesn't "
                f"crash."
            )

    if len(All_Searchable_Folders) == 0:
        raise RuntimeError(
            f"No .npy files found under Base_Path={Base_Path!r}. "
            f"Check that this path exists and actually contains "
            f"convertLidarDataNew.py's output (one subfolder per bag, "
            f"each full of .npy frames) -- training would otherwise silently "
            f"proceed with zero data and crash later with a confusing "
            f"ZeroDivisionError instead of failing clearly here."
        )

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

    epochs = args.epochs
    use_amp = True

    if args.load_model:
        start_epoch = checkpoint["epoch"] + 1
    else:
        start_epoch = 0


    print(len(All_Searchable_Folders))

    current_time = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())

    print(f'training started at: {current_time}')
    start_time = time.time()
    sweep_start_time = time.time()  # tracks total wall-clock time for this run, for results_csv

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

                data1 = fps_downsample(data1, points_all, npoints)
                # print(data1.shape)
                # front_lidar = transform(data1)

                # rear_lidar = tensor_transform(rear_lidar).to("cuda")
                # if len(rear_lidar) < points_all:
                #         points_all = len(rear_lidar)

                # rear_lidar = rear_lidar[:, :, :3].contiguous()
                if data2.dtype != torch.float32:
                    data2 = data2.float()

                data2 = fps_downsample(data2, points_all, npoints)
            # for i in range (0, len(Image_Train)):
                # data = Image_Train[i]
                # speed = Speed_Train[i]
                # angle = Steering_Angle_Train[i]
                data1 = data1.to(device)
                data2 = data2.to(device)

                # if data1.size(1) < points_all:
                #     points_all = data1.size(1)

                # data1 = fps_downsample(data1, points_all, npoints)
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

        # .item() here converts these from CUDA tensors to plain Python
        # floats -- without it, the results_csv row ends up with literal
        # strings like "tensor(0.9113, device='cuda:0')" instead of numbers,
        # which breaks pandas/any downstream numeric analysis of the CSV.
        total_epoch_accuracy1 = (total_epoch_accuracy1 / train_len).item()
        total_epoch_accuracy2 = (total_epoch_accuracy2 / train_len).item()
        total_epoch_loss = total_epoch_loss / train_len
        total_epoch_val_accuracy1 = (total_epoch_val_accuracy1 / val_len).item()
        total_epoch_val_accuracy2 = (total_epoch_val_accuracy2 / val_len).item()
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

        # Separately track the best VALIDATION epoch, not just best train
        # epoch. For long runs these can diverge (the model can keep
        # improving on train while val gets worse -- classic overfitting),
        # and without this you'd have no checkpoint of the actually-best
        # model, and no way to tell from results_csv alone whether "final"
        # epoch numbers reflect the best point in training or an
        # already-overfit one.
        if best_val_loss > total_epoch_val_loss:
            best_val_loss = total_epoch_val_loss
            best_val_epoch = epoch

            best_val_save_name = f"pointMamba_shuttle_{model_name}_bestval_{epoch+1}_{total_epoch_val_loss:.4f}_{total_epoch_val_accuracy1:.4f}_{total_epoch_val_accuracy2:.4f}.pth"

            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_loss': total_epoch_val_loss
            }, best_val_save_name)

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

    # --- Append this run's results to the sweep CSV -----------------------------
    total_training_time = time.time() - sweep_start_time

    results_row = {
        "run_name": args.run_name or model_name,
        "config_label": args.config_label or "",
        "repeat": args.repeat,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "model_type": args.model_type,
        "trans_dim": args.trans_dim,
        "depth": args.depth,
        "cls_dim": args.cls_dim,
        "num_group": args.num_group,
        "group_size": args.group_size,
        "encoder_dims": args.encoder_dims,
        "rms_norm": args.rms_norm,
        "drop_path": args.drop_path,
        "drop_out": args.drop_out,
        "drop_out_block": args.drop_out_block,
        "use_cls_token": args.use_cls_token,
        "freeze_encoder": args.freeze_encoder,
        "lr": args.lr,
        "weight_decay": args.weight_decay,
        "gamma": args.gamma,
        "batch_size": args.batch_size,
        "epochs_requested": args.epochs,
        "epochs_completed": epoch + 1,
        "best_train_loss": best_loss,
        "best_val_loss": best_val_loss,
        "best_val_epoch": (best_val_epoch + 1) if best_val_epoch is not None else "",
        "final_train_loss": total_epoch_loss,
        "final_train_accuracy1": total_epoch_accuracy1,
        "final_train_accuracy2": total_epoch_accuracy2,
        "final_val_loss": total_epoch_val_loss,
        "final_val_accuracy1": total_epoch_val_accuracy1,
        "final_val_accuracy2": total_epoch_val_accuracy2,
        "total_training_time_sec": round(total_training_time, 1),
        "checkpoint_saved": f"pointMamba_shuttle_{model_name}.pth",
    }

    file_exists = os.path.exists(args.results_csv)
    with open(args.results_csv, "a", newline="") as f:
        csv_writer = csv.DictWriter(f, fieldnames=list(results_row.keys()))
        if not file_exists:
            csv_writer.writeheader()
        csv_writer.writerow(results_row)

    print(f"Appended results to {args.results_csv}")