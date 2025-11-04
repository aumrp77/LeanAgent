from lean_dojo import LeanGitRepo
from dynamic_database import DynamicDatabase
from git_utils import add_repo_to_database
from filenames import RAID_DIR, DB_FILE_NAME
from pathlib import Path

SEED_REPOS = [
    ("https://github.com/ImperialCollegeLondon/FLT", "b208a302cdcbfadce33d8165f0b054bfa17e2147"),
    ("https://github.com/HEPLean/PhysLean", "60f1ebc3eb015f78a3719ee4085344a600d0af50"),
    ("https://github.com/verse-lab/veil", "a9fe7205c57f7b6ee8b350bfc87b9b4b28c57781"),
]

db_path = Path(RAID_DIR) / DB_FILE_NAME
if db_path.exists():
    db = DynamicDatabase.from_json(db_path)
else:
    db = DynamicDatabase()

for url, commit in SEED_REPOS:
    repo = LeanGitRepo(url, commit)
    print(f"Tracing {url}@{commit}")
    add_repo_to_database(str(db_path), repo, db)
