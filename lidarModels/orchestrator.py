# orchestrator.py
import subprocess
import sys

# Define the paths to the Python executables for each environment
MAMBA_PYTHON = "/home/ubuntu22/miniconda3/envs/pointmamba/bin/python"  # e.g., an env with mamba-ssm
CAM_PYTHON = "/home/ubuntu22/miniconda3/envs/pointcam/bin/python"      # e.g., an env with xformers

# Define the scripts to run
MAMBA_SCRIPT = "sweepmamba.py"
CAM_SCRIPT = "sweep2.py"  # Or your PointCAM sweep script

# print("Starting PointMamba inference in Environment 1...")
# mamba_process = subprocess.run([MAMBA_PYTHON, MAMBA_SCRIPT], capture_output=True, text=True)
# if mamba_process.returncode != 0:
#     print(f"Error running Mamba:\n{mamba_process.stderr}")
#     sys.exit(1)
# print("PointMamba finished and saved mamba_preds.npy")

print("Starting PointCAM inference in Environment 2...")
cam_process = subprocess.run([CAM_PYTHON, CAM_SCRIPT], capture_output=True, text=True)
if cam_process.returncode != 0:
    print(f"Error running CAM:\n{cam_process.stderr}")
    sys.exit(1)
print("PointCAM finished and saved cam_preds.npy")

print("Both models completed successfully. Proceeding to ensemble validation.")