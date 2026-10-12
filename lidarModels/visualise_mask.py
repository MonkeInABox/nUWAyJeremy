# Jeremy Butson, adapting (https://github.com/szacho/pointcam) to the University of Western Australia REV Project nUWAy shuttle driving


import numpy as np
import torch
import matplotlib.pyplot as plt
from pathlib import Path
from model import PointCAMBackbone

def visualize_patches():
    data_path = "/media/ubuntu22/RAID1/jeremy/baylissALLDATA"
    npy_files = list(Path(data_path).rglob("*.npy"))
    if not npy_files:
        print("No .npy files found.")
        return
    
    sample_file = str(npy_files[0])
    print(f"Loading sample: {sample_file}")
    
    data = np.load(sample_file, allow_pickle=True)
    front_lidar = np.delete(data[0], -1, axis=1)
    points = torch.tensor(front_lidar[:3072, :3], dtype=torch.float32).unsqueeze(0)

    backbone = PointCAMBackbone(n_patches=64, points_per_patch=32)
    backbone.eval()

    with torch.no_grad():
        patched_output = backbone.patch_finder(points)
        
        if hasattr(patched_output, 'centers'):
            centers = patched_output.centers
        elif hasattr(patched_output, 'patch_centers'):
            centers = patched_output.patch_centers
        else:
            centers = patched_output.xyz
            
        centers_np = centers.detach().cpu().numpy()
        while centers_np.ndim > 2 and centers_np.shape[0] == 1:
            centers_np = centers_np[0]
            
        num_patches = centers_np.shape[0]

        mask = None
        
        if hasattr(backbone, 'mask_generator'):
            try:
                mask = backbone.mask_generator(centers)
            except Exception as e:
                print(f"mask_generator execution note: {e}")
                
        if mask is None and hasattr(backbone, 'forward_enc'):
            try:
                _, _, mask = backbone.forward_enc(points)
            except Exception as e:
                print(f"forward_enc execution note: {e}")

        if mask is not None:
            mask_np = mask.detach().cpu().numpy()
            while mask_np.ndim > 1:
                mask_np = mask_np[0]
            mask_np = mask_np.astype(bool)
        else:
            ratio = getattr(backbone, 'mask_ratio', 0.6)
            n_masked = int(num_patches * ratio)
            perm = np.random.permutation(num_patches)
            masked_indices = perm[:n_masked]
            
            mask_np = np.ones(num_patches, dtype=bool)
            mask_np[masked_indices] = False

        visible_centers = centers_np[mask_np]
        masked_centers = centers_np[~mask_np]
        
        print(f"Simulated PointCAM Mask -> Visible Patches: {len(visible_centers)} | Hidden Patches: {len(masked_centers)}")

        pts_np = points[0].numpy()

        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(projection='3d')
        
        ax.scatter(pts_np[:, 0], pts_np[:, 1], pts_np[:, 2], c='lightgray', s=0.5, alpha=0.3, label='Raw Points', zorder=1)
        
        if len(visible_centers) > 0:
            ax.scatter(visible_centers[:, 0], visible_centers[:, 1], visible_centers[:, 2], 
                       c='blue', s=30, label='Visible Patches', zorder=3)
            
        if len(masked_centers) > 0:
            ax.scatter(masked_centers[:, 0], masked_centers[:, 1], masked_centers[:, 2], 
                       c='red', s=30, label='Hidden Patches (Masked)', zorder=3)

        ax.set_title(f"Simulated PointCAM Mask")
        
        ax.set_xlim([0.0, 50.0])
        ax.set_ylim([0.0, 50.0])
        ax.set_zlim([0.0, 50.0])
        ax.view_init(elev=30, azim=-120)
        ax.set_box_aspect([1, 1, 0.5])
        ax.set_xlabel("X (Forward)")
        ax.set_ylabel("Y (Lateral)")
        ax.set_zlabel("Z (Height)")
        ax.legend()
        plt.savefig("visible_vs_masked_patches.png", dpi=1000)
        print("Saved visualization to visible_vs_masked_patches.png")

if __name__ == "__main__":
    visualize_patches()