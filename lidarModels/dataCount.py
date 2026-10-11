import os

def count_files_by_threshold(main_folder, threshold=0.02):
    above_count = 0
    below_count = 0

    # Walk through all subfolders
    for root, _, files in os.walk(main_folder):
        for filename in files:
            if filename.endswith(".npy") and filename.startswith("Pcl_"):
                parts = filename.rstrip(".npy").split("_")
                if len(parts) >= 5:
                    try:
                        value = float(parts[3])  # 4th element
                        if value > threshold and value < (threshold + 0.03):
                            above_count += 1
                        else:
                            below_count += 1
                    except ValueError:
                        continue  # Skip invalid filenames

    return above_count, below_count


if __name__ == "__main__":
    main_folder = "/media/quirky/EglintonData/lidar_data_sorting/LiDAR_Dual_Stage2/lane_following/"  # change this to your folder containing subfolders
    above, below = count_files_by_threshold(main_folder)
    print(f"Files with value > 0.03: {above}")
    print(f"Files with value <= 0.03: {below}")