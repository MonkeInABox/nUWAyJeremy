import torch
from torch import nn
from functools import partial

from torchvision import datasets, models, transforms
from PIL import Image

from einops import rearrange, repeat
from einops.layers.torch import Rearrange
from shuttlebusTrainAugmentation import drivePointMamba

from torch.utils.tensorboard import SummaryWriter

import numpy as np

import cv2
import os
import sys
from os.path import join, exists, dirname, abspath
import matplotlib.cm as cm

from pointnet2_ops import pointnet2_utils

# from sklearn.model_selection import train_test_split

# import torch.optim as optim
# from torch.optim.lr_scheduler import StepLR
import argparse
# from torchsummary import summary
import time

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import random
import data_transforms

tensor_transform = transforms.Compose(
    [
        transforms.ToTensor(),
    ]
)

transform = transforms.Compose(
    [
        # data_transforms.PointcloudScaleAndTranslate(),
    ]
)

saliency_transform = transforms.Compose([
    # transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5], std=[0.5])
])

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
padding = 4300
npoints = 3072
points_all = 4300

if __name__ == "__main__":
    #load image
    parser = argparse.ArgumentParser("Load model from checkpoint")
    parser.add_argument("--load_model", action="store_true")
    parser.add_argument("model_name", default="pointMamba_shuttle_lane_following_50_0.0009_0.7666_0.8309.pth", type=str, nargs='?')
    # parser.add_argument("model_fine_name", default="VMamba_shuttle_lane_following_13_0.0003_0.9026_0.8934.pth", type=str, nargs='?')
    # parser.add_argument("model_pullin_name", default="SwinTransformer_shuttle_pullin_50_0.0005_0.9154_0.8539.pth", type=str, nargs='?')
    # parser.add_argument("model_reverse_name", default="SwinTransformer_shuttle_reverse_50_0.0003_0.9359_0.9977.pth", type=str, nargs='?')
    parser.add_argument("model_type", default="lane_following", type=str, nargs='?')

    args = parser.parse_args()

    print(args.model_name)
    print(args.model_type)

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

    model.load_state_dict(torch.load(args.model_name, weights_only=True)['model_state_dict'])

    model.eval()
    model.to(device)

    model_name = args.model_type


    Image_Paths = []
    All_Searchable_Folders = []

    # All_Searchable_Folders = [dirname("/home/quirky/Documents/eglinton_datasorting_dual/sorted_eglinton_data/CIL_Dual_Cam_Stage1/bad_gps_manual_sorting_needed/")]
    # All_Searchable_Folders = [dirname("/home/quirky/Documents/eglinton_datasorting_dual/sorted_eglinton_data/CIL_Dual_Cam_Stage2_B/pullout/")]

    All_Searchable_Folders = [dirname("/home/quirky/Documents/nUWAyModels/lidarModels/pointMamba/output/")]
    # All_Searchable_Folders = [dirname("/media/quirky/EglintonData/lidar_data_sorting/LiDAR_Dual_Stage2/lane_following/")]
    current_file = 47000
    current_model = 0
    # print(All_Searchable_Folders)
    
    random_bag = random.randint(0, len(os.listdir(All_Searchable_Folders[0]))-1)
    # print(os.listdir(All_Searchable_Folders[0]))
    # print(os.listdir(category_file))

    while True:
        # try:
        
        image_path = os.listdir(All_Searchable_Folders[0])[random_bag]
        # print(image_path)
        # print(join(All_Searchable_Folders[0],image_path))
        # image_path = All_Searchable_Folders
        # print(sorted(os.listdir(image_path)))
        # print(len(os.listdir(image_path[0])))
        # print(current_file)
        selected_bag = join(All_Searchable_Folders[0],image_path)
        # print(All_Searchable_Folders[0])
        # selected_bag = All_Searchable_Folders[0]
        # print(sorted(os.listdir(selected_bag), key=lambda x: int(x.split("_")[1])))
        file = sorted(os.listdir(selected_bag), key=lambda x: int(x.split("_")[1]))[current_file]
        # print(f"file is: {file}")
        previous_file = sorted(os.listdir(selected_bag), key=lambda x: int(x.split("_")[1]))[current_file-6]
        # file = os.listdir(selected_bag)[0]
        # print(file)
        image_path = join(selected_bag, file)
        previous_data_path = join(selected_bag, previous_file)
        # print(image_path)
        # file = sorted(os.listdir(image_path), key=lambda x: int(x.split("_")[1]))[current_file]
        # print(file)

    # try:
        data = np.load(image_path, allow_pickle=True)
        previous_data = np.load(previous_data_path, allow_pickle=True)
        # print(data)
        # print(len(data))

        img = data[4]


        Speed = data[2][0]
        # print(f"speed value is: {Speed}")
        Steering_Angle = data[3][0]
        # print(f"Steering_Angle value is: {Steering_Angle}")
        # print(len(data[0]))
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

        if len(front_cropped_points) > padding:
            # Random sampling
            indices = np.random.choice(len(front_cropped_points), padding, replace=False)
            front_cropped_points = front_cropped_points[indices]

        if len(rear_cropped_points) > padding:
            # Random sampling
            indices = np.random.choice(len(rear_cropped_points), padding, replace=False)
            rear_cropped_points = rear_cropped_points[indices]

        front_lidar = tensor_transform(front_cropped_points)
        # front_lidar = front_lidar.to(device="cuda")
        # front_lidar = transform(front_lidar)
        # print(front_lidar.shape)
        filler = torch.zeros(1,(padding - front_lidar.size(1)), 3)
        # filler = filler.to(device="cuda")
        front_lidar = torch.cat((front_lidar, filler), 1)
        front_lidar = torch.squeeze(front_lidar)

        rear_lidar = tensor_transform(rear_cropped_points)
        # rear_lidar = rear_lidar.to(device="cuda")
        # rear_lidar = transform(rear_lidar)
        filler = torch.zeros(1,(padding - rear_lidar.size(1)), 3)
        # filler = filler.to(device="cuda")
        rear_lidar = torch.cat((rear_lidar, filler), 1)
        rear_lidar = torch.squeeze(rear_lidar)
        # print(rear_lidar.shape)
        # rear_lidar = torch.squeeze(rear_lidar)
        front_lidar = front_lidar.unsqueeze(0)
        rear_lidar = rear_lidar.unsqueeze(0)

        # print(front_lidar.shape)
        front_lidar = front_lidar.to(device="cuda")
        rear_lidar = rear_lidar.to(device="cuda")

        if front_lidar.size(1) < points_all:
            points_all = front_lidar.size(1)

        # print(points_all)
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

        # front_lidar = front_lidar.to(device)
        # rear_lidar = rear_lidar.to(device)

        start_time = time.time()

        cropped_img = img[60:, 40:440]
        cropped_img = Image.fromarray(np.uint8(cropped_img), mode='L')

        saliency_img = cropped_img.copy()

        cropped_img = tensor_transform(cropped_img)
        cropped_img = rearrange(cropped_img, "c h w -> 1 c h w")
        cropped_img = cropped_img.to(device)

        # print(Speed)
        # print(Steering_Angle)

        target = None

        with torch.inference_mode(), torch.autocast('cuda', enabled=False):

            # torch.save(cropped_img, "input.pt")

            #pass image to model
            if current_model == 0:
                output1, output2 = model(front_lidar, rear_lidar)

            # elif current_model == 1:
            #     output1, output2 = model_fine(cropped_img)
    

        output1 = output1 * 5.4
        output2 = output2 * 0.3
        output1 = output1.detach().cpu().numpy()[0]
        output2 = output2.detach().cpu().numpy()[0]
        elapse_time = time.time() - start_time
        print(f"elapsed time is: {elapse_time}")
        # print(Steering_Angle)

        # Speed = Speed * 5.4
        # Steering_Angle = Steering_Angle * 0.3
        Speed = Speed
        Steering_Angle = Steering_Angle
        

        print(output1)
        print(output2)
        print(Speed)
        print(Steering_Angle)
        # print(f"current driving mode is: {data[4]}")

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
            # elif current_model == 1:
            #     saliency_output1, saliency_output2 = model_fine(input_tensor)
            #     target = saliency_output1[0, 0] if saliency_output1.dim() == 2 else saliency_output1.squeeze()

            #     # Backward pass: compute gradients of output w.r.t. input image
            #     model_fine.zero_grad()
            #     target.backward()
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
            # elif current_model == 1:
            #     saliency_output1, saliency_output2 = model_fine(input_tensor2)
            #     target2 = saliency_output2[0, 0] if saliency_output2.dim() == 2 else saliency_output2.squeeze()

            #     # Backward pass: compute gradients of output w.r.t. input image
            #     model_fine.zero_grad()
            #     target2.backward()
           
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


            # plt.figure(figsize=(6, 6))
            # plt.imshow(overlay)
            # plt.axis("off")
            # plt.title("Saliency Map Overlay")
            # # plt.ion()
            # # plt.show()
            # plt.pause(0.001)
            k = cv2.waitKey(0)

        if k == 113:
            cv2.destroyAllWindows()
            break
        elif k == 83:
            current_file += 1
            if current_file > (len(os.listdir(selected_bag))-1):
                current_file = (len(os.listdir(selected_bag))-1)
            continue
        elif k == 81:
            current_file -= 1
            if current_file < 10:
                current_file = 10
            continue
        elif k == 82:
            current_file += 20
            if current_file > (len(os.listdir(selected_bag))-1):
                current_file = (len(os.listdir(selected_bag))-1)
            continue
        elif k == 84:
            current_file -= 20
            if current_file < 10:
                current_file = 10
            continue
        elif k == 114:
            current_model = 3
            continue
        # elif k == 102:
        #     current_model = 1
            continue
        elif k == 112:
            current_model = 2
            continue
        elif k == 108:
            current_model = 0
            continue
        elif k == 99:
            # random_category = random.randint(0, len(All_Searchable_Folders)-1)
            # category_file = join(All_Searchable_Folders, All_Searchable_Folders[random_category])
            # random_bag = random.randint(0, len(os.listdir(category_file))-1)
            random_bag = random.randint(0, len(os.listdir(All_Searchable_Folders[0])))
            current_file = 0
            continue
        
        # elif k == :
        #     random_bag = random.randint(0, len(All_Searchable_Folders))
        #     current_file = 0
        #     continue
        else:
            continue