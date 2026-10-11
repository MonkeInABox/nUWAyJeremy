# Import
import matplotlib.pyplot as plt
from matplotlib import cm, colors
#import torchsparse
import numpy as np
# Load Point Cloud
import torch
import cv2
path = "/media/ubuntu22/RAID1/jeremy/output/newbag_0_fixed/Pcl_14_4.000_-0.000_.npy"

x_max = 15
x_min = -15
y_min = -3.0
y_max = 3.0
y_limit = 4.0
z_limit = 0.5

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

# Merge clouds
def merge_point_clouds(front_point_cloud, front_feats, rear_point_cloud, rear_feats):  
    print(front_point_cloud.shape)
    front_ones = np.ones((front_point_cloud.shape[0], 1))
    front_point_cloud_h = np.hstack([front_point_cloud, front_ones])  # Shape: (N, 4)
    rear_ones = np.ones((rear_point_cloud.shape[0], 1))
    rear_point_cloud_h = np.hstack([rear_point_cloud, rear_ones])  # Shape: (N, 4)

    front_transformed_h = (front_LiDAR_transformation_matrix @ front_point_cloud_h.T).T  # Shape: (N, 4)
    rear_transformed_h = (rear_LiDAR_transformation_matrix @ rear_point_cloud_h.T).T    # Shape: (N, 4)

    # merged_point_clouds = np.vstack([front_transformed_h[:, 0:3], rear_transformed_h[:, 0:3]], dtype=np.float32)
    # merged_feats = np.vstack([front_feats, rear_feats], dtype=np.float32)

    # return merged_point_clouds, merged_feats
    f_x, f_y, f_z = front_transformed_h[:, 0], front_transformed_h[:, 1], front_transformed_h[:, 2]
    r_x, r_y, r_z = rear_transformed_h[:, 0], rear_transformed_h[:, 1], rear_transformed_h[:, 2]

    front_mask = (f_x > x_min) & (f_x < x_max) & (np.abs(f_y) < y_limit) & (f_z < z_limit)
    rear_mask = (r_x > x_min) & (r_x < x_max) & (np.abs(r_y) < y_limit) & (r_z < z_limit)

    front_cropped_points = front_transformed_h[front_mask, :3]  # Shape: (M, 3)
    print(front_cropped_points.shape)
    front_cropped_feats = front_feats[front_mask]
    rear_cropped_points = rear_transformed_h[rear_mask, :3]    # Shape: (M, 3)
    print(rear_cropped_points.shape)
    rear_cropped_feats = rear_feats[rear_mask]

    cropped_points = np.vstack([front_cropped_points, rear_cropped_points], dtype=np.float32)
    print(cropped_points.shape)
    cropped_feats = np.vstack([front_cropped_feats, rear_cropped_feats], dtype=np.float32)

    return cropped_points, cropped_feats

# Plot clouds
def plot_point_cloud(point_cloud, block=True):
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
                        marker='.',          # point marker
                        s=5)                # marker size
        
        # Adding color bar to show intensity scale
        cb = plt.colorbar(sc, ax=ax, pad=0.1)
        cb.set_label('Intensity')
        
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.view_init(elev=35, azim=45)  # Adjust perspective # for xy-plane: elev=90, azim=-90 # side-view: elev=30, azim=45
        #ax.set_axis_off()
        # Label axes
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')

        #fig.patch.set_facecolor('black')  # Set background
        #ax.set_facecolor('black')
        plt.savefig('point_cloud_comp_vox.png', dpi=300, bbox_inches='tight') #format='svg', 
        
        # Set plot title
        #ax.set_title('3D Point Cloud with Intensity Visualization')
        
        plt.show(block=block)

# Voxelize point cloud
def voxelize_point_cloud_with_intensity(point_cloud, feats, voxel_size=0.2):
    """
    Convert a point cloud to a voxel grid with aggregated intensity values.
    
    Parameters:
    point_cloud (numpy.ndarray): Nx4 array of [x, y, z, intensity].
    voxel_size (float): Size of each voxel (default: 0.2).
    
    Returns:
    intensity_grid (numpy.ndarray): 3D array with aggregated intensities.
    """
    # Get min and max coordinates
    min_coords = np.min(point_cloud[:, :3], axis=0)
    max_coords = np.max(point_cloud[:, :3], axis=0)
    
    # Calculate grid shape based on voxel size
    ranges = max_coords - min_coords
    grid_shape = np.ceil(ranges / voxel_size).astype(int)
    
    # Initialize grids for intensity sum and point count
    intensity_sum = np.zeros(grid_shape)
    point_count = np.zeros(grid_shape)
    
    # Normalize coordinates to voxel indices
    coords_normalized = (point_cloud[:, :3] - min_coords) / voxel_size
    coords_normalized = np.floor(coords_normalized).astype(int)
    coords_normalized = np.clip(coords_normalized, 0, grid_shape - 1)
    
    # Aggregate intensities
    for i in range(point_cloud.shape[0]):
        x, y, z = coords_normalized[i]
        intensity = feats[i]#coords_normalized[i][2]
        intensity_sum[x, y, z] += intensity
        point_count[x, y, z] += 1
    
    # Compute average intensity per voxel
    with np.errstate(divide='ignore', invalid='ignore'):
        intensity_grid = intensity_sum / point_count
        intensity_grid[point_count == 0] = 0  # Set to 0 where no points
    
    return intensity_grid

def plot_voxel_grid_with_intensity(intensity_grid):
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')
    
    # Occupied voxels
    occupied = intensity_grid > 0
    print("occupied shape:", occupied.shape)
    
    # Normalize intensities
    min_intensity = np.min(intensity_grid[occupied]) if np.any(occupied) else 0
    max_intensity = np.max(intensity_grid[occupied]) if np.any(occupied) else 1
    #norm_intensity = (intensity_grid - min_intensity) / (max_intensity - min_intensity + 1e-6)
    norm = colors.Normalize(vmin=min_intensity, vmax=max_intensity)

    # Create colors_4d
    cmap = cm.get_cmap('viridis')
    #cmap = plt.get_cmap('viridis')
    colors_4d = np.zeros((*occupied.shape, 4), dtype=float)
    colors_4d[occupied] = cmap(norm(intensity_grid[occupied]))
    
    # Verify shapes
    print("colors_4d shape:", colors_4d.shape)
    
    # Plot voxels
    ax.voxels(occupied,
                    facecolors=colors_4d,
                    edgecolor=None,
                    alpha=0.8)
    
    # === Force cubes ===
    # This makes the x,y,z axes have equal scale so voxels appear cubic
    #ax.set_box_aspect((1, 1, 1))


    # === Force cubic voxels by equalizing axis limits ===
    # Calculate the shape of the grid:
    nx, ny, nz = intensity_grid.shape
    max_dim = max(nx, ny, nz)
    # Compute centers
    cx, cy, cz = nx/2, ny/2, nz/2
    # Set each axis to run from center-half_max to center+half_max
    half = max_dim / 2
    ax.set_xlim(cx - half, cx + half)
    ax.set_ylim(cy - half, cy + half)
    ax.set_zlim(cz - half, cz + half)

    # === Colorbar ===
    mappable = cm.ScalarMappable(norm=norm, cmap=cmap)
    mappable.set_array(intensity_grid)  
    cbar = fig.colorbar(mappable, ax=ax, shrink=0.6, pad=0.1)
    cbar.set_label('Intensity')

    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    #ax.set_axis_off()
    # ax.set_xlim(284, 484)
    # ax.set_ylim(82, 232)
    # ax.set_xlim(344, 424)
    # ax.set_ylim(137, 187)
    ax.set_xlim(0, 150)
    ax.set_ylim(0, 150)
    ax.set_zlim(-20, 50)
    ax.view_init(elev=35, azim=45)  # Adjust perspective # for xy-plane: elev=90, azim=-90

    # fig.patch.set_facecolor('black')  # Set background
    # ax.set_facecolor('black')
    plt.savefig('voxel_plot_test.png', dpi=300, bbox_inches='tight') #format='svg', 
    plt.show()

def augment_front_rear_lidar_visible(front_points, front_int, rear_points, rear_int,
                                     delta_y_front=0.3, delta_y_rear=-0.3,
                                     n_rings=16, n_cols=1800):
    """
    Augment front and rear LiDAR clouds with a visible lateral shift and z-buffer simulation.

    Returns coordinates and intensities separately.
    """

    def augment_single_cloud(points, intensities, delta_y):
        # Step 1: visible lateral translation
        points_shifted = points + np.array([0.0, delta_y, 0.0], dtype=np.float32)
        
        # Step 2: compute relative vectors from shifted LiDAR origin
        origin = np.array([0.0, delta_y, 0.0], dtype=np.float32)
        rel = points_shifted - origin
        r = np.linalg.norm(rel, axis=1)
        az = np.arctan2(rel[:,1], rel[:,0])
        el = np.arcsin(rel[:,2] / np.clip(r, 1e-6, None))
        
        # Step 3: quantize to LiDAR pattern
        el_min, el_max = -15*np.pi/180, 15*np.pi/180  # typical VLP-16 FoV
        ring = np.floor((el - el_min) / (el_max - el_min) * n_rings).astype(int)
        col = np.floor((az + np.pi) / (2*np.pi) * n_cols).astype(int)
        
        # Keep valid bins
        valid = (ring >=0) & (ring < n_rings) & (col >=0) & (col < n_cols)
        r, az, el, intensities = r[valid], az[valid], el[valid], intensities[valid]
        ring, col = ring[valid], col[valid]
        
        # Step 4: z-buffer - keep nearest per (ring, col)
        key = ring * n_cols + col
        order = np.lexsort((r, key))
        unique_keys, first_idx = np.unique(key[order], return_index=True)
        keep = order[first_idx]
        r, az, el, intensities = r[keep], az[keep], el[keep], intensities[keep]
        
        # Step 5: back-project into world coordinates
        x = r * np.cos(el) * np.cos(az) + origin[0]
        y = r * np.cos(el) * np.sin(az) + origin[1]
        z = r * np.sin(el) + origin[2]
        points_aug = np.stack([x, y, z], axis=1)
        
        return points_aug, intensities

    # Augment front and rear
    front_aug, front_int_aug = augment_single_cloud(front_points, front_int, delta_y_front)
    rear_aug, rear_int_aug = augment_single_cloud(rear_points, rear_int, delta_y_rear)
    
    # Merge clouds
    # all_points = np.vstack([front_aug, rear_aug])
    # all_intensities = np.hstack([front_int_aug, rear_int_aug])
    
    # return all_points, all_intensities
    
    return front_aug, front_int_aug, rear_aug, rear_int_aug


# Point Cloud Plot
data = np.load(path, allow_pickle=True)
print((data))
front_point_cloud, rear_point_cloud = data[0], data[1]
# img = data[2]
# img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
# cv2.imshow('ground truth comparison', img)
# k = cv2.waitKey(0)
front_coords, rear_coords = front_point_cloud[:, :3], rear_point_cloud[:, :3]
front_feats, rear_feats = np.expand_dims(front_point_cloud[:, 3], axis=-1), np.expand_dims(rear_point_cloud[:, 3], axis=-1)
delta_y = (torch.rand(1).item() * 2 - 1) * 0.3
delta_y = -1
t = torch.tensor([0.0, -delta_y, 0.0]).numpy()
R = torch.eye(3).numpy()

# front_lidar = front_coords @ R.T + t
# rear_lidar = rear_coords @ R.T - t


front_lidar, front_feats_aug, rear_lidar, rear_feats_aug = augment_front_rear_lidar_visible(
    front_coords, front_feats,
    rear_coords, rear_feats,
    delta_y_front=delta_y, delta_y_rear=-delta_y
)

print("Original:", front_coords.shape, "Augmented:", front_lidar.shape)
print("Original:", rear_coords.shape, "Augmented:", rear_lidar.shape)

transformed_coords, feats = merge_point_clouds(front_coords, front_feats, rear_coords, rear_feats)
shifted_coords, shifted_feats = merge_point_clouds(front_lidar, front_feats_aug, rear_lidar, rear_feats_aug)
print("Original:", transformed_coords.shape, "Augmented:", shifted_coords.shape)
tmp = np.hstack([transformed_coords, feats])
shifted_coords = shifted_coords @ R.T + t
tmp2 = np.hstack([shifted_coords, shifted_feats])
plot_point_cloud(tmp, False)
plot_point_cloud(tmp2)
# Voxelize with voxel size 0.2
#intensity_grid = voxelize_point_cloud_with_intensity(transformed_coords, feats, voxel_size=0.2)    
# Plot the voxel grid with intensity
#plot_voxel_grid_with_intensity(intensity_grid)