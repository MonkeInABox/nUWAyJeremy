

import csv
import itertools
import os
import subprocess
import sys
import time
from datetime import datetime

# Config value (change them!)

TRAIN_SCRIPT = "shuttleBusTrainCAM.py"   # training script
MODEL_TYPE = "lane_following"            

RESULTS_CSV = "sweep_results.csv"        # output csv
LOG_DIR = "sweep_logs"                   # log dir
FAILURES_CSV = "sweep_failures.csv"      # failure womp woomp csv

EPOCHS_PER_RUN = 5

RUN_TIMEOUT_SEC = None

SWEEP_GRID = {
    "n_patches": [32, 64, 128],
    "points_per_patch": [16, 32, 64],
    "drop_path_rate": [0.0, 0.1, 0.2],
    "lr": [1e-4, 5e-5],
    "freeze_encoder": [False, True],
}

SWEEP_LIST = None


def build_configs():
    if SWEEP_LIST is not None:
        return list(SWEEP_LIST)
    keys = list(SWEEP_GRID.keys())
    combos = itertools.product(*(SWEEP_GRID[k] for k in keys))
    return [dict(zip(keys, combo)) for combo in combos]


def config_to_argv(config, run_name):
    argv = [
        sys.executable, TRAIN_SCRIPT, MODEL_TYPE,
        "--epochs", str(EPOCHS_PER_RUN),
        "--results_csv", RESULTS_CSV,
        "--run_name", run_name,
    ]
    for key, value in config.items():
        flag = f"--{key}"
        if isinstance(value, bool):
            if value:
                argv.append(flag)  
        else:
            argv.extend([flag, str(value)])
    return argv


def log_failure(run_name, config, returncode, log_path):
    file_exists = os.path.exists(FAILURES_CSV)
    row = {
        "run_name": run_name,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "returncode": returncode,
        "log_file": log_path,
        **config,
    }
    with open(FAILURES_CSV, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(row.keys()))
        if not file_exists:
            w.writeheader()
        w.writerow(row)


def main():
    os.makedirs(LOG_DIR, exist_ok=True)
    configs = build_configs()

    print(f"Sweep: {len(configs)} run(s) planned, {EPOCHS_PER_RUN} epoch(s) each")
    print(f"Results -> {RESULTS_CSV}   Failures -> {FAILURES_CSV}   Logs -> {LOG_DIR}/")

    for i, config in enumerate(configs, start=1):
        run_name = f"run{i:03d}_" + "_".join(f"{k}={v}" for k, v in config.items())
        run_name = run_name.replace(" ", "")
        log_path = os.path.join(LOG_DIR, f"{run_name}.log")

        argv = config_to_argv(config, run_name)

        print(f"\n[{i}/{len(configs)}] {run_name}")
        print(f"  command: {' '.join(argv)}")

        start = time.time()
        with open(log_path, "w") as log_file:
            try:
                result = subprocess.run(
                    argv,
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    timeout=RUN_TIMEOUT_SEC,
                )
                returncode = result.returncode
            except subprocess.TimeoutExpired:
                print(f"  TIMED OUT after {RUN_TIMEOUT_SEC}s -- logged as failure")
                log_failure(run_name, config, returncode="timeout", log_path=log_path)
                continue

        elapsed = time.time() - start

        if returncode == 0:
            print(f"  done in {elapsed:.1f}s")
        else:
            print(f"  FAILED (exit code {returncode}) -- see {log_path}")
            log_failure(run_name, config, returncode, log_path)

    print("\nSweep complete.")
    if os.path.exists(RESULTS_CSV):
        print(f"Results: {RESULTS_CSV}")
    if os.path.exists(FAILURES_CSV):
        print(f"Some runs failed -- see {FAILURES_CSV} and {LOG_DIR}/ for details")


if __name__ == "__main__":
    main()
