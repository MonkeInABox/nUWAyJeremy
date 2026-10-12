# Jeremy Butson, adapting (https://github.com/szacho/pointcam) to the University of Western Australia REV Project nUWAy shuttle driving

import subprocess
import sys

MAMBA_PYTHON = "/home/ubuntu22/miniconda3/envs/pointmamba/bin/python"  
CAM_PYTHON = "/home/ubuntu22/miniconda3/envs/pointcam/bin/python"     


MAMBA_SCRIPT = "sweepmamba.py"
CAM_SCRIPT = "sweep2.py"  

print("Starting PointMamba inference in Environment 1..")
mamba_process = subprocess.run([MAMBA_PYTHON, MAMBA_SCRIPT], capture_output=True, text=True)
if mamba_process.returncode != 0:
    print(f"Error running Mamba:\n{mamba_process.stderr}")
    sys.exit(1)
print("PointMamba finished and saved mamba_preds.npy")

print("Starting PointCAM inference in Environment 2...")
cam_process = subprocess.run([CAM_PYTHON, CAM_SCRIPT], capture_output=True, text=True)
if cam_process.returncode != 0:
    print(f"Error running CAM:\n{cam_process.stderr}")
    sys.exit(1)
print("PointCAM finished and saved cam_preds.npy")

print("Both models completed successfully. Proceeding to ensemble validation.")