

import csv
import itertools
import os
import subprocess
import sys
import time
from datetime import datetime



TRAIN_SCRIPT = "shuttlebusTrainCAMMulti.py"   
MODEL_TYPE = "lane_following"            

RESULTS_CSV = "sweep_results_bay.csv"        
LOG_DIR = "sweep_logs_bay"                 
FAILURES_CSV = "sweep_failures_bay.csv"    

EPOCHS_PER_RUN = 10


RUN_TIMEOUT_SEC = None

BASELINE = {
    "n_patches": 64,
    "points_per_patch": 32,
    "freeze_encoder": False,
    "drop_path_rate": 0.1,
    "lr": 1e-4,
    "weight_decay": 0.05,
    "gamma": 0.8,
    "batch_size": 70,
}

SWEEP_LIST = [
    {**BASELINE, "run_label": "baseline"},
    {**BASELINE, "run_label": "baseline"},
    {**BASELINE, "run_label": "baseline"},
    {**BASELINE, "run_label": "baseline"},
    {**BASELINE, "run_label": "baseline"},

    # --- encoder / patching -----------------------------------------------
    {**BASELINE, "run_label": "freeze_encoder", "freeze_encoder": True},
    {**BASELINE, "run_label": "freeze_encoder", "freeze_encoder": True},
    {**BASELINE, "run_label": "freeze_encoder", "freeze_encoder": True},
    {**BASELINE, "run_label": "freeze_encoder", "freeze_encoder": True},
    {**BASELINE, "run_label": "freeze_encoder", "freeze_encoder": True},
    {**BASELINE, "run_label": "patches_undersampled", "n_patches": 32, "points_per_patch": 32},   # 1024 pts covered
    {**BASELINE, "run_label": "patches_undersampled", "n_patches": 32, "points_per_patch": 32},   # 1024 pts covered
    {**BASELINE, "run_label": "patches_undersampled", "n_patches": 32, "points_per_patch": 32},   # 1024 pts covered
    {**BASELINE, "run_label": "patches_undersampled", "n_patches": 32, "points_per_patch": 32},   # 1024 pts covered
    {**BASELINE, "run_label": "patches_undersampled", "n_patches": 32, "points_per_patch": 32},   # 1024 pts covered
    {**BASELINE, "run_label": "patches_oversampled", "n_patches": 128, "points_per_patch": 32},   # 4096 pts covered
    {**BASELINE, "run_label": "patches_oversampled", "n_patches": 128, "points_per_patch": 32},   # 4096 pts covered
    {**BASELINE, "run_label": "patches_oversampled", "n_patches": 128, "points_per_patch": 32},   # 4096 pts covered
    {**BASELINE, "run_label": "patches_oversampled", "n_patches": 128, "points_per_patch": 32},   # 4096 pts covered
    {**BASELINE, "run_label": "patches_oversampled", "n_patches": 128, "points_per_patch": 32},   # 4096 pts covered
    {**BASELINE, "run_label": "patches_fewer_larger", "n_patches": 32, "points_per_patch": 64},   # same 2048 coverage, different granularity
    {**BASELINE, "run_label": "patches_fewer_larger", "n_patches": 32, "points_per_patch": 64},   # same 2048 coverage, different granularity
    {**BASELINE, "run_label": "patches_fewer_larger", "n_patches": 32, "points_per_patch": 64},   # same 2048 coverage, different granularity
    {**BASELINE, "run_label": "patches_fewer_larger", "n_patches": 32, "points_per_patch": 64},   # same 2048 coverage, different granularity
    {**BASELINE, "run_label": "patches_fewer_larger", "n_patches": 32, "points_per_patch": 64},   # same 2048 coverage, different granularity
    {**BASELINE, "run_label": "patches_fewer_larger", "n_patches": 32, "points_per_patch": 64},   # same 2048 coverage, different granularity

    # --- regularization ------------------------------------------------------
    {**BASELINE, "run_label": "drop_path_0.0", "drop_path_rate": 0.0},
    {**BASELINE, "run_label": "drop_path_0.0", "drop_path_rate": 0.0},
    {**BASELINE, "run_label": "drop_path_0.0", "drop_path_rate": 0.0},
    {**BASELINE, "run_label": "drop_path_0.0", "drop_path_rate": 0.0},
    {**BASELINE, "run_label": "drop_path_0.0", "drop_path_rate": 0.0},
    {**BASELINE, "run_label": "drop_path_0.3", "drop_path_rate": 0.3},
    {**BASELINE, "run_label": "drop_path_0.3", "drop_path_rate": 0.3},
    {**BASELINE, "run_label": "drop_path_0.3", "drop_path_rate": 0.3},
    {**BASELINE, "run_label": "drop_path_0.3", "drop_path_rate": 0.3},
    {**BASELINE, "run_label": "drop_path_0.3", "drop_path_rate": 0.3},
    {**BASELINE, "run_label": "weight_decay_0.0", "weight_decay": 0.0},
    {**BASELINE, "run_label": "weight_decay_0.0", "weight_decay": 0.0},
    {**BASELINE, "run_label": "weight_decay_0.0", "weight_decay": 0.0},
    {**BASELINE, "run_label": "weight_decay_0.0", "weight_decay": 0.0},
    {**BASELINE, "run_label": "weight_decay_0.0", "weight_decay": 0.0},
    {**BASELINE, "run_label": "weight_decay_0.2", "weight_decay": 0.2},
    {**BASELINE, "run_label": "weight_decay_0.2", "weight_decay": 0.2},
    {**BASELINE, "run_label": "weight_decay_0.2", "weight_decay": 0.2},
    {**BASELINE, "run_label": "weight_decay_0.2", "weight_decay": 0.2},
    {**BASELINE, "run_label": "weight_decay_0.2", "weight_decay": 0.2},


    {**BASELINE, "run_label": "lr_1e-3", "lr": 1e-3},
    {**BASELINE, "run_label": "lr_1e-3", "lr": 1e-3},
    {**BASELINE, "run_label": "lr_1e-3", "lr": 1e-3},
    {**BASELINE, "run_label": "lr_1e-3", "lr": 1e-3},
    {**BASELINE, "run_label": "lr_1e-3", "lr": 1e-3},
    {**BASELINE, "run_label": "lr_1e-5", "lr": 1e-5},
    {**BASELINE, "run_label": "lr_1e-5", "lr": 1e-5},
    {**BASELINE, "run_label": "lr_1e-5", "lr": 1e-5},
    {**BASELINE, "run_label": "lr_1e-5", "lr": 1e-5},
    {**BASELINE, "run_label": "lr_1e-5", "lr": 1e-5},



    {**BASELINE, "run_label": "gamma_0.3_very_aggressive", "gamma": 0.3},
    {**BASELINE, "run_label": "gamma_0.3_very_aggressive", "gamma": 0.3},
    {**BASELINE, "run_label": "gamma_0.3_very_aggressive", "gamma": 0.3},
    {**BASELINE, "run_label": "gamma_0.3_very_aggressive", "gamma": 0.3},
    {**BASELINE, "run_label": "gamma_0.3_very_aggressive", "gamma": 0.3},
    {**BASELINE, "run_label": "gamma_0.5_aggressive", "gamma": 0.5},
    {**BASELINE, "run_label": "gamma_0.5_aggressive", "gamma": 0.5},
    {**BASELINE, "run_label": "gamma_0.5_aggressive", "gamma": 0.5},
    {**BASELINE, "run_label": "gamma_0.5_aggressive", "gamma": 0.5},
    {**BASELINE, "run_label": "gamma_0.5_aggressive", "gamma": 0.5},
    {**BASELINE, "run_label": "gamma_0.6", "gamma": 0.6},
    {**BASELINE, "run_label": "gamma_0.6", "gamma": 0.6},
    {**BASELINE, "run_label": "gamma_0.6", "gamma": 0.6},
    {**BASELINE, "run_label": "gamma_0.6", "gamma": 0.6},
    {**BASELINE, "run_label": "gamma_0.6", "gamma": 0.6},
    {**BASELINE, "run_label": "gamma_0.7", "gamma": 0.7},
    {**BASELINE, "run_label": "gamma_0.7", "gamma": 0.7},
    {**BASELINE, "run_label": "gamma_0.7", "gamma": 0.7},
    {**BASELINE, "run_label": "gamma_0.7", "gamma": 0.7},
    {**BASELINE, "run_label": "gamma_0.7", "gamma": 0.7},

    {**BASELINE, "run_label": "gamma_0.9", "gamma": 0.9},
    {**BASELINE, "run_label": "gamma_0.9", "gamma": 0.9},
    {**BASELINE, "run_label": "gamma_0.9", "gamma": 0.9},
    {**BASELINE, "run_label": "gamma_0.9", "gamma": 0.9},
    {**BASELINE, "run_label": "gamma_0.9", "gamma": 0.9},
    {**BASELINE, "run_label": "gamma_0.95_gentle", "gamma": 0.95},
    {**BASELINE, "run_label": "gamma_0.95_gentle", "gamma": 0.95},
    {**BASELINE, "run_label": "gamma_0.95_gentle", "gamma": 0.95},
    {**BASELINE, "run_label": "gamma_0.95_gentle", "gamma": 0.95},
    {**BASELINE, "run_label": "gamma_0.95_gentle", "gamma": 0.95},
    {**BASELINE, "run_label": "gamma_0.99_very_gentle", "gamma": 0.99},
    {**BASELINE, "run_label": "gamma_0.99_very_gentle", "gamma": 0.99},
    {**BASELINE, "run_label": "gamma_0.99_very_gentle", "gamma": 0.99},
    {**BASELINE, "run_label": "gamma_0.99_very_gentle", "gamma": 0.99},
    {**BASELINE, "run_label": "gamma_0.99_very_gentle", "gamma": 0.99},

    {**BASELINE, "run_label": "batch_size_32", "batch_size": 32},
    {**BASELINE, "run_label": "batch_size_32", "batch_size": 32},
    {**BASELINE, "run_label": "batch_size_32", "batch_size": 32},
    {**BASELINE, "run_label": "batch_size_32", "batch_size": 32},
    {**BASELINE, "run_label": "batch_size_32", "batch_size": 32},
    {**BASELINE, "run_label": "batch_size_128", "batch_size": 128},
    {**BASELINE, "run_label": "batch_size_128", "batch_size": 128},
    {**BASELINE, "run_label": "batch_size_128", "batch_size": 128},
    {**BASELINE, "run_label": "batch_size_128", "batch_size": 128},
    {**BASELINE, "run_label": "batch_size_128", "batch_size": 128},


    {**BASELINE, "run_label": "combined_guess"},
    {**BASELINE, "run_label": "combined_guess"},
    {**BASELINE, "run_label": "combined_guess"},
    {**BASELINE, "run_label": "combined_guess"},
    {**BASELINE, "run_label": "combined_guess"},
]

SWEEP_GRID = {
    "n_patches": [32, 64, 128],
    "points_per_patch": [16, 32, 64],
    "drop_path_rate": [0.0, 0.1, 0.2],
    "lr": [1e-4, 5e-5],
    "freeze_encoder": [False, True],
}




def build_configs():
    if SWEEP_LIST is not None:
        return list(SWEEP_LIST)
    keys = list(SWEEP_GRID.keys())
    combos = itertools.product(*(SWEEP_GRID[k] for k in keys))
    return [dict(zip(keys, combo)) for combo in combos]


def config_to_argv(config, run_name):
    config = {k: v for k, v in config.items() if k != "run_label"}
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
                argv.append(flag)  # store_true flags: only pass when True
        else:
            argv.extend([flag, str(value)])
    return argv


def log_failure(run_name, config, returncode, log_path):
    config = {k: v for k, v in config.items() if k != "run_label"}
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
        label = config.get("run_label", f"config{i}")
        run_name = f"run{i:03d}_{label}"
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
