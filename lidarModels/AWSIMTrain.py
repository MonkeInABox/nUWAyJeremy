# 


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

import cv2
import os
import sys
from os.path import join, exists, dirname, abspath

from sklearn.model_selection import train_test_split

import torch.optim as optim
from torch.optim.lr_scheduler import StepLR, ReduceLROnPlateau #, CosLR

import data_transforms

from pointnet2_ops import pointnet2_utils

from torchsummary import summary
import time
import argparse

writer = SummaryWriter()

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

        # self.pool = pool
        # self.to_latent = nn.Identity()

        self.mlp_head1 = nn.Sequential(
                nn.Linear(cls_dim, int(cls_dim / 2)),
                nn.LayerNorm(int(cls_dim/2)),
                nn.ELU(),
                nn.Linear(int(cls_dim / 2),  int(cls_dim / 4)),
                nn.LayerNorm(int(cls_dim / 4)),
                nn.ELU(),
                nn.Linear(int(cls_dim / 4), 1)).to(device=self.device)
        
        self.mlp_head2 = nn.Sequential(
                nn.Linear(cls_dim, int(cls_dim / 2)),
                nn.LayerNorm(int(cls_dim/2)),
                nn.ELU(),
                nn.Linear(int(cls_dim / 2),  int(cls_dim / 4)),
                nn.LayerNorm(int(cls_dim / 4)),
                nn.ELU(),
                nn.Linear(int(cls_dim / 4), 1)).to(device=self.device)

    def forward(self, front_cloud):
        # front_cloud = front_cloud[0]
        # front_cloud = torch.unsqueeze(front_cloud, 0)
        # print(front_cloud.shape)
        x = self.vision_model(front_cloud)
        b, n = x.shape

        speed = self.mlp_head1(x)
        angle = self.mlp_head2(x)
        # print(x.shape)
        return speed[:,0], angle[:,0]
        # return x

padding = 1000

tensor_transform = transforms.Compose(
    [
        transforms.ToTensor(),
    ]
)

transform = transforms.Compose(
    [
        
        # transforms.RandomResizedCrop(224),
        # transforms.RandomHorizontalFlip(),
        # transforms.ToTensor(),
        # transforms.Pad(padding=padding),
        # transforms.Resize((5000, 4)),
        data_transforms.PointcloudScaleAndTranslate(),
        # transforms.ToTensor(),
    ]
)

class dataset(torch.utils.data.Dataset):
    def __init__(self, file_list1, label_list1, label_list2, transform=None):
        self.file_list1 = file_list1
        # self.file_list2 = file_list2
        self.label_list1 = label_list1
        self.label_list2 = label_list2
        self.transform = transform

    def __len__(self):
        self.filelength = len(self.file_list1)
        return self.filelength

    def __getitem__(self, idx):
        merged_lidar = self.file_list1[idx]
        # rear_lidar = self.file_list2[idx]
        label1 = self.label_list1[idx]
        label2 = self.label_list2[idx]
        # img = Image.open(img_path).convert("RGB")
        # img_transformed = self.transform(img)
        

        merged_lidar = self.transform(merged_lidar)
        # print(merged_lidar.shape)
        filler = torch.zeros(1,(padding - merged_lidar.size(1)), 3)
        # print(filler.shape)
        merged_lidar = torch.cat((merged_lidar, filler), 1)
        merged_lidar = torch.squeeze(merged_lidar)
        # print(merged_lidar.shape)
        # F.pad(front_lidar, (5000 - front_lidar.size(1)), "constant", torch.empty(4))
        # print(front_lidar.shape)
        # rear_lidar = self.transform(rear_lidar)
        # filler = torch.zeros(1,(padding - rear_lidar.size(1)), 3)
        # rear_lidar = torch.cat((rear_lidar, filler), 1)
        # rear_lidar = torch.squeeze(rear_lidar)
        return merged_lidar, label1, label2
    
def collate_fn(batch):
    # print("batch data looks like ")
    # print(batch[0])
    # print(len(batch))
    data1 = torch.stack([item[0] for item in batch])
    # data1 = tensor_transform(data1)
    # data2 = torch.stack([item[1] for item in batch])
    # data2 = tensor_transform(data2)
    label1 = [item[1] for item in batch]
    label2 = [item[2] for item in batch]
    return data1, label1, label2

if __name__ == "__main__":
    lr = 1e-4
    weight_decay = 0.05
    gamma = 0.1
    batch_size = 96
    npoints = 2048
    points_all = 2400
    Speed_scale = 5.4
    Steering_Angle_scale = 0.3
    best_loss = 100000
    use_amp = True

    model_path_name = "VMamba_shuttle_pullin_18_0.0002_0.9459_0.8891.pth"
    checkpoint = None

    
    # with open('config.yaml', 'r') as file:
    #     config_yaml = yaml.safe_load(file)

    parser = argparse.ArgumentParser("Load model from checkpoint")
    parser.add_argument("--load_model", action="store_true")
    parser.add_argument("--fine_tune_model", action="store_true")
    parser.add_argument("model_type", default="lane_following", type=str, nargs='?')


    model = drivePointMamba(
        trans_dim=384,
        depth=12,
        cls_dim= 40,
        group_size= 32,
        num_group= 64,
        encoder_dims= 384,
        rms_norm= False,
        drop_path= 0.3,
        drop_out= 0.1,
        drop_out_block= 0.1,
        use_cls_token=False,
    )

    args = parser.parse_args()

    if args.load_model:
        print("loading model")
        checkpoint = torch.load(model_path_name, weights_only=True)
        
        model.load_state_dict(checkpoint['model_state_dict'])
    elif args.fine_tune_model:
        print("fine tuning model")
        checkpoint = torch.load(model_path_name, weights_only=True)
        model.load_state_dict(checkpoint['model_state_dict'])


    # summary(model, (20000, 3))

    # img = torch.randn(1, 3, 200, 66)
    for name, layer in model.named_children():
        print(name)

    # Front_lidar_all = []
    # Rear_lidar_all = []
    lidar_all = []
    # Image_all = []
    Speeds_All = []
    Steering_Angles_All = []

    if args.fine_tune_model:
        model_name = args.model_type + '_finetune'
    else:
        model_name = args.model_type
    print(model_name)

    # Script_Path = dirname(abspath(join((__file__), '..')))
    # print(Script_Path)
    Script_Path = abspath(join('..', 'AWSIM'))
    Image_Path = join(join(Script_Path, 'sorted_data'), 'extracted_vel_0_5_merged')
    print(Image_Path)    
    if exists(Image_Path):
        for Folders in os.listdir(Image_Path):
            Search_Folder = join(Image_Path, Folders)
            # i=0
            # print(Search_Folder)
            for Files in os.listdir(Search_Folder):
                # print(i)
                # print(Files)
                try:
                    data = np.load(join(Search_Folder, Files), allow_pickle=True)
                except EOFError:
                    continue

                #front lidar, rear lidar, image, speed, steering
                # print("start of data")
                # print(data)
                Speed = data[1]
                Speed = Speed / Speed_scale
                # print(Speed)
                Steering_Angle = data[2]
                Steering_Angle = Steering_Angle / Steering_Angle_scale
                merged_lidar = np.delete(data[0], -1, axis=1)
                # print(np.delete(data[0], -1, axis=1))
                # bleh
                # rear_lidar = np.delete(data[1], -1, axis=1)
                # merged_lidar = data[0][:2]
                # print(merged_lidar)
                # print(len(merged_lidar))
                # image = data[2]
                # merged_lidar = tensor_transform(merged_lidar).to("cuda")
                # print(merged_lidar.shape)
                # print(front_lidar)
                # print(len(front_lidar))
                
                # rear_lidar = tensor_transform(rear_lidar).to("cuda")
                if len(merged_lidar) > padding:
                    padding = len(merged_lidar)
                # if len(front_lidar) > padding:
                #     padding = len(front_lidar)
                # if len(rear_lidar) > padding:
                #     padding = len(rear_lidar)
                # Speed=int(Files.split("_")[3])
                # Steering_Angle=int(Files.split("_")[4])
                # img=Image.open(join(Search_Folder, Files)).convert("RGB")
                # print(Image.shape)
                # Front_lidar_all.append(front_lidar)
                # Rear_lidar_all.append(rear_lidar)
                lidar_all.append(merged_lidar)
                # Image_all.append(image)
                Speeds_All.append(Speed)
                Steering_Angles_All.append(Steering_Angle)
                # i = i + 1
    else:
        print('[Error!] Check Image Directory is Correct!')
        sys.exit()

    print(len(lidar_all))
    print(len(Speeds_All))
    print(len(Steering_Angles_All))

    # for i in range(0, 1):
    # print(Front_lidar_all[0])
    Split_a = train_test_split(lidar_all, Speeds_All, Steering_Angles_All, test_size=0.1, shuffle=True)
    (merged_clouds, merged_clouds_Test, Speeds, Speed_Test, Steering_Angles, Steering_Angle_Test) = Split_a   
    Split_b = train_test_split(merged_clouds, Speeds, Steering_Angles, test_size=0.2, shuffle=True)
    (merge_clouds_Train, merge_clouds_Valid, Speed_Train, Speed_Valid, Steering_Angle_Train, Steering_Angle_Valid) = Split_b

    train_data = dataset(merge_clouds_Train, Speed_Train, Steering_Angle_Train, transform=tensor_transform)
    test_data = dataset(merged_clouds_Test, Speed_Test, Steering_Angle_Test, transform=tensor_transform)
    val_data = dataset(merge_clouds_Valid, Speed_Valid, Steering_Angle_Valid, transform=tensor_transform)

    train_loader = torch.utils.data.DataLoader(
        dataset=train_data, batch_size=batch_size, shuffle=True, drop_last=True, collate_fn=collate_fn
    )
    test_loader = torch.utils.data.DataLoader(
        dataset=test_data, batch_size=batch_size, shuffle=True, collate_fn=collate_fn
    )
    val_loader = torch.utils.data.DataLoader(
        dataset=val_data, batch_size=batch_size, shuffle=True, collate_fn=collate_fn
    )

    criterion = nn.L1Loss()
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    if args.load_model:
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    # scheduler = StepLR(optimizer, step_size=10, gamma=gamma)
    scheduler = ReduceLROnPlateau(optimizer, 'min', factor=gamma, patience=5)


    epochs = 50

    if args.load_model:
        start_epoch = checkpoint["epoch"] + 1
    else:
        start_epoch = 0

    device = "cuda" if torch.cuda.is_available() else "cpu"

    current_time = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())

    print(f'training started at: {current_time}')
    start_time = time.time()

    for epoch in range(start_epoch, epochs):
        epoch_loss = 0
        epoch_accuracy1 = 0
        epoch_accuracy2 = 0
        total_loss1 = 0
        total_loss2 = 0

        # print("length of data trainer is ")
        # print(train_loader)

        # for data1, data2, label1, label2 in train_loader:
        for data1, label1, label2 in train_loader:

            data1 = data1.to(device="cuda")
            # data2 = data2.to(device="cuda")
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

            # print(points_all)
            # print(data1)

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

            # fps_idx = pointnet2_utils.furthest_point_sample(data2, points_all)
            # fps_idx = fps_idx[:, np.random.choice(points_all, npoints, False)]
            # data2 = pointnet2_utils.gather_operation(data2.transpose(1, 2).contiguous(), fps_idx).transpose(1, 2).contiguous()
        # for i in range (0, len(Image_Train)):
            # data = Image_Train[i]
            # speed = Speed_Train[i]
            # angle = Steering_Angle_Train[i]
            data1 = data1.to(device)
            # data2 = data2.to(device)

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

            # with torch.amp.autocast(device_type="cuda", dtype=torch.float16, enabled=use_amp):
            output1, output2 = model(data1)
            loss1 = criterion(output1, label1)
            loss2 = criterion(output2, label2)

            loss = loss1 + loss2
            total_loss1 += loss1.item()
            total_loss2 += loss2.item()
            # print(output1.shape)
            # print(label1.shape)
            # loss1 = criterion(output1, label1)
            # loss2 = criterion(output2, label2)

            # loss = loss1 + loss2
            

            # writer.add_scalar("Loss/Train", loss, epoch)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            acc1 = (abs(output1 - label1) < (0.27 / Speed_scale)).float().sum()
            acc2 = (abs(output2 - label2) < (0.015 / Steering_Angle_scale)).float().sum()
            epoch_accuracy1 += acc1
            epoch_accuracy2 += acc2
            epoch_loss += loss.item()

        epoch_accuracy1 = epoch_accuracy1 / len(train_loader.dataset)
        epoch_accuracy2 = epoch_accuracy2 / len(train_loader.dataset)
        epoch_loss = epoch_loss / len(train_loader.dataset)

        
        
        print(
            "Epoch : {}, train accuracy1 : {}, train accuracy2 : {}, train loss : {}".format(
                epoch + 1, epoch_accuracy1, epoch_accuracy2, epoch_loss
            )
        )

        print(
            "Loss contributions from 1: {}, and 2 : {}".format(
                total_loss1, total_loss2
            )
        )

        with torch.no_grad():
            epoch_val_accuracy1 = 0
            epoch_val_accuracy2 = 0
            epoch_val_loss = 0
            # for i in range(0, len(Image_Valid)): 
            for data1, label1, label2 in val_loader:
                # data = Image_Valid[i]
                # speed = Speed_Valid[i]
                # angle = Steering_Angle_Valid[i]
                data1 = data1.to(device)
                # data2 = data2.to(device)
                label1 = torch.FloatTensor(label1)
                label2 = torch.FloatTensor(label2)
                label1 = label1.to(device)
                label2 = label2.to(device)

                val_output1, val_output2 = model(data1)
                val_loss1 = criterion(val_output1, label1)
                val_loss2 = criterion(val_output2, label2)

                val_loss = val_loss1 + val_loss2

                acc1 = (abs(val_output1 - label1) < (0.54 / Speed_scale)).float().sum()
                acc2 = (abs(val_output2 - label2) < (0.03 / Steering_Angle_scale)).float().sum()
                epoch_val_accuracy1 += acc1
                epoch_val_accuracy2 += acc2
                epoch_val_loss += val_loss.item()

            epoch_val_accuracy1 = epoch_val_accuracy1 / len(val_loader.dataset)
            epoch_val_accuracy2 = epoch_val_accuracy2 / len(val_loader.dataset)
            epoch_val_loss = epoch_val_loss / len(val_loader.dataset)
            
            print(
                "Epoch : {}, val_accuracy : {}, val_accuracy : {}, val_loss : {}".format(
                    epoch + 1, epoch_val_accuracy1, epoch_val_accuracy2, epoch_val_loss
                )
            )

        train_len = len(train_loader.dataset)
        val_len = len(val_loader.dataset)

        total_epoch_accuracy1 = epoch_accuracy1 #/ train_len
        total_epoch_accuracy2 = epoch_accuracy2 #/ train_len
        total_epoch_loss = epoch_loss #/ train_len
        total_epoch_val_accuracy1 = epoch_val_accuracy1 #/ val_len
        total_epoch_val_accuracy2 = epoch_val_accuracy2 #/ val_len
        total_epoch_val_loss = epoch_val_loss #/ val_len
        writer.add_scalar("Loss/Train", total_epoch_loss, epoch)
        writer.add_scalar("Loss/Validation", total_epoch_val_loss, epoch)
        writer.add_scalar("accuracy1/Train", total_epoch_accuracy1, epoch)
        writer.add_scalar("accuracy2/Train", total_epoch_accuracy2, epoch)
        writer.add_scalar("accuracy1/Validation", total_epoch_val_accuracy1, epoch)
        writer.add_scalar("accuracy2/Validation", total_epoch_val_accuracy2, epoch)

        if best_loss > epoch_loss:
            best_loss = epoch_loss

            save_name = f"pointMamba_awsim_{model_name}_{epoch+1}_{epoch_loss:.4f}_{epoch_accuracy1:.4f}_{epoch_accuracy2:.4f}.pth"

            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'loss': epoch_loss
            }, save_name)

        scheduler.step(epoch_val_loss)

        elapsed_time = time.time() - start_time
        start_time = time.time()

        print(f'Time elapsed: {elapsed_time}')

        # print(f"straight count: {straight_count}, turning count: {turning_count}")

    end_time = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())

    print(f'training finished at: {end_time}')

    torch.save(model.state_dict(), f'pointMamba_awsim_{model_name}.pth')
    writer.flush()
    writer.close()

