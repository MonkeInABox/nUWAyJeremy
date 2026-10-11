import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np


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

x_max = 15
x_min = -15
y_min = -15
y_max = 15
y_limit = 15
z_limit = 30

lidar = np.load("/media/ubuntu22/RAID1/jeremy/output/newbag_0_fixed/Pcl_14_4.000_-0.000_.npy", allow_pickle=True)
# Example front_lidar: list of [x, y, z, intensity]
front_lidar = lidar[0][:, :3]
rear_lidar = lidar[1][:, :3]

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
rear_cropped_points = rear_lidar[rear_mask, :3]    # Shape: (M, 3)


# print(len(front_lidar))
print(front_lidar)

full_lidar = np.vstack([front_cropped_points, rear_cropped_points], dtype=np.float32)

# Convert to numpy array for easier indexing
# front_lidar = np.array(front_lidar)

# Split columns
x, y, z = full_lidar[:, 0], full_lidar[:, 1], full_lidar[:, 2]

# === Load or generate saliency ===
# Replace with your real saliency source
# saliency = np.load("saliency.npy")  # Must match shape: (full_lidar.shape[0],)
saliency = np.random.rand(full_lidar.shape[0])  # Example placeholder

# Normalize saliency for color mapping
saliency_normalized = (saliency - np.min(saliency)) / (np.max(saliency) - np.min(saliency) + 1e-6)

# Create 3D plot
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')

# Scatter plot with intensity as color
sc = ax.scatter(x, y, z, c=saliency_normalized, cmap='plasma', s=5)

# Add colorbar
cbar = plt.colorbar(sc, ax=ax, label='Saliency')

# Axis labels
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('3D Scatter Plot with Saliency')

plt.tight_layout()
plt.show()