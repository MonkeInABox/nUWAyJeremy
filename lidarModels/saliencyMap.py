import torch
from torch import nn
import torch.nn.functional as F
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


import torch.optim as optim
import time

import data_transforms

from pointnet2_ops import pointnet2_utils

model_path_name = "VMamba_shuttle_lane_following_finetune_7_0.0003_0.9266_0.8902.pth"
checkpoint = None

device = "cuda" if torch.cuda.is_available() else "cpu"

model = drivePointMamba(
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
    )

print("loading model")
checkpoint = torch.load(model_path_name, weights_only=True)

model.load_state_dict(checkpoint['model_state_dict'])
model.eval()

data = np.load("Img_1065_0.677_0.011_.npy", allow_pickle=True)




#load data

input_tensor.requires_grad_()

# Forward pass
output1, output2 = model(input_tensor)  # shape: (1, num_classes)
target = output1[0, 0] if output1.dim() == 2 else output1.squeeze()

# Backward pass: compute gradients of output w.r.t. input image
model.zero_grad()
target.backward()


# Compute saliency as the norm of the gradient at each point
saliency = input_tensor.grad.data.norm(dim=1).squeeze().cpu().numpy()  # (N,)

# Normalize for visualization
saliency = (saliency - saliency.min()) / (saliency.max() - saliency.min())

# Visualize: 3D scatter with saliency as color
import open3d as o3d

def visualize_saliency(points, saliency):
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    colors = plt.cm.jet(saliency)[:, :3]  # Colormap for saliency
    pcd.colors = o3d.utility.Vector3dVector(colors)
    o3d.visualization.draw_geometries([pcd])

visualize_saliency(points, saliency)