# Jeremy Butson, adapting (https://github.com/szacho/pointcam) to the University of Western Australia REV Project nUWAy shuttle driving and PointMamba

import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error

def main():
    try:
        mamba_preds = np.load("mamba_preds.npy")
        cam_preds = np.load("cam_preds.npy")
        targets = np.load("targets.npy")
    except FileNotFoundError as e:
        print(f"Error loading files. Ensure the orchestrator ran successfully: {e}")
        return

    print(f"Loaded shapes -> mamba_preds: {mamba_preds.shape}, cam_preds: {cam_preds.shape}, targets: {targets.shape}")

    if mamba_preds.shape != cam_preds.shape:
        print("Warning: Shape mismatch detected between model predictions!")
        min_len = min(mamba_preds.shape[0], cam_preds.shape[0], targets.shape[0])
        print(f"Truncating all arrays to common length: {min_len}")
        
        mamba_preds = mamba_preds[:min_len]
        cam_preds = cam_preds[:min_len]
        targets = targets[:min_len]

    if mamba_preds.ndim > 1 and mamba_preds.shape[-1] == 1:
        mamba_preds = mamba_preds.squeeze(-1)
    if cam_preds.ndim > 1 and cam_preds.shape[-1] == 1:
        cam_preds = cam_preds.squeeze(-1)
    if targets.ndim > 1 and targets.shape[-1] == 1:
        targets = targets.squeeze(-1)

    assert mamba_preds.shape == cam_preds.shape, f"Still unequal shapes: {mamba_preds.shape} vs {cam_preds.shape}"

    ensemble_preds = (mamba_preds + cam_preds) / 2.0
    is_multi_output = (ensemble_preds.ndim == 2 and ensemble_preds.shape[1] >= 2)


    chunk_size = 50 
    num_chunks = int(np.ceil(len(ensemble_preds) / chunk_size))

    print("\n=== Per-Epoch / Chunk Ensemble Validation Results ===")
    print(f"{'Epoch/Chunk':<12} | {'Speed MAE':<12} | {'Speed MSE':<12} | {'Steer MAE':<12} | {'Steer MSE':<12}")
    print("-" * 68)

    for i in range(num_chunks):
        start_idx = i * chunk_size
        end_idx = min((i + 1) * chunk_size, len(ensemble_preds))
        
        chunk_preds = ensemble_preds[start_idx:end_idx]
        chunk_targets = targets[start_idx:end_idx]
        
        if len(chunk_preds) == 0:
            continue

        if is_multi_output:
            s_preds = chunk_preds[:, 0]
            s_targs = chunk_targets[:, 0]
            st_preds = chunk_preds[:, 1]
            st_targs = chunk_targets[:, 1]
            
            s_mae = mean_absolute_error(s_targs, s_preds)
            s_mse = mean_squared_error(s_targs, s_preds)
            st_mae = mean_absolute_error(st_targs, st_preds)
            st_mse = mean_squared_error(st_targs, st_preds)
            
            print(f"{i+1:<12} | {s_mae:<12.4f} | {s_mse:<12.4f} | {st_mae:<12.4f} | {st_mse:<12.4f}")
        else:
            mae = mean_absolute_error(chunk_targets, chunk_preds)
            mse = mean_squared_error(chunk_targets, chunk_preds)
            print(f"{i+1:<12} | {mae:<12.4f} | {mse:<12.4f} | {'N/A':<12} | {'N/A':<12}")

    if is_multi_output:
        speed_preds_flat = ensemble_preds[:, 0]
        speed_targets_flat = targets[:, 0]
        steer_preds_flat = ensemble_preds[:, 1]
        steer_targets_flat = targets[:, 1]
        
        print("\n=== Overall Ensemble Summary ===")
        print(f"Speed    -> MSE: {mean_squared_error(speed_targets_flat, speed_preds_flat):.4f} | MAE: {mean_absolute_error(speed_targets_flat, speed_preds_flat):.4f}")
        print(f"Steering -> MSE: {mean_squared_error(steer_targets_flat, steer_preds_flat):.4f} | MAE: {mean_absolute_error(steer_targets_flat, steer_preds_flat):.4f}")
    else:
        print("\n=== Overall Ensemble Summary ===")
        print(f"Overall  -> MSE: {mean_squared_error(targets, ensemble_preds):.4f} | MAE: {mean_absolute_error(targets, ensemble_preds):.4f}")
    print("==========================================")

if __name__ == "__main__":
    main()