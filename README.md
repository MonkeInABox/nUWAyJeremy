# All My Working Files for Honours 2026 - nUWAy Shuttle Bus LiDAR Model Dev

- Thank you to Kieran Quirke-Brown et al. for the basis for a lot of these files

Running the docker file:
```bash
cd docker/
docker build -t pointcam-inference:latest .
./run_pointcam_inference.sh /checkpoint.pth /cmd_vel
```
