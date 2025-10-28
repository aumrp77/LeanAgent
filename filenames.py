import os

RAID_DIR = os.environ.get("RAID_DIR")
ray_tmp = "/tmp/ray"
os.makedirs(ray_tmp, exist_ok=True)
os.environ["RAY_TMPDIR"] = ray_tmp
REPO_DIR = os.path.join(RAID_DIR, "repos")
DATA_DIR = os.path.join(RAID_DIR, "data")
CHECKPOINT_DIR = os.path.join(RAID_DIR, "checkpoints")
EVAL_RESULTS_FILE_PATH = os.path.join(RAID_DIR, "eval_results.txt")
DB_FILE_NAME = "db_file.txt"
PROOF_LOG_FILE_NAME = os.path.join(RAID_DIR, "proof_log.txt")
ENCOUNTERED_THEOREMS_FILE = os.path.join(RAID_DIR, "encountered_theorems.pkl")
FISHER_DIR = os.path.join(RAID_DIR, "fisher")  # Optional
