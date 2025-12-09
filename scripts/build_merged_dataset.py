#!/usr/bin/env python3
"""
Build a merged dataset from already-traced repos.

This script:
  - Loads/creates the dynamic database at RAID/db_file.txt
  - For each non-empty corpus under RAID/data/<name>_<sha>/corpus.jsonl,
    it infers (repo_url, commit) from the first line and adds the repo to the DB
    using git_utils.add_repo_to_database (reuses LeanDojo caches if present).
  - Exports a merged dataset to RAID/data/merged_paper_subset.

Run from repo root:
  export RAID_DIR="$PWD/RAID"
  export REPO_DIR="$RAID_DIR/repos"
  python LeanAgent/scripts/build_merged_dataset.py
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from loguru import logger
import sys

# Ensure repo modules are importable when running as a script
HERE = Path(__file__).resolve()
REPO_ROOT = HERE.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from lean_dojo import LeanGitRepo  # noqa: E402
from dynamic_database import DynamicDatabase  # noqa: E402
from filenames import RAID_DIR, DB_FILE_NAME  # noqa: E402
from git_utils import add_repo_to_database  # noqa: E402
from scripts.trace_paper_repos import PAPER_REPOS  # noqa: E402


def iter_nonempty_corpora(data_root: Path):
    for d in sorted(data_root.iterdir()):
        cj = d / "corpus.jsonl"
        if not cj.exists() or cj.stat().st_size == 0:
            continue
        yield d, cj


_SLUG_TO_URL = {
    item["name"]: f"https://github.com/{item['owner']}/{item['name']}"
    for item in PAPER_REPOS
}
# Add alternative names for repos with different directory names
_SLUG_TO_URL["formal_book"] = "https://github.com/mo271/FormalBook"
_SLUG_TO_URL["hairy-ball-theorem-lean"] = "https://github.com/leanprover-community/hairy-ball-theorem"


def _infer_repo_from_dir(dir_path: Path) -> tuple[str, str]:
    name = dir_path.name
    if "_" not in name:
        raise ValueError(f"Directory name {name} does not contain commit suffix")
    slug, commit = name.rsplit("_", 1)
    if len(commit) != 40:
        raise ValueError(f"Directory {name} missing 40-char commit suffix")
    url = _SLUG_TO_URL.get(slug)
    if not url:
        raise ValueError(f"Unknown repo slug '{slug}'. Please add it to PAPER_REPOS.")
    return url, commit


def load_repo_from_corpus(corpus_path: Path) -> tuple[str, str]:
    with corpus_path.open() as f:
        first = f.readline()
    url = commit = ""
    if first:
        try:
            meta = json.loads(first)
            url = meta.get("repo_url") or ""
            commit = meta.get("commit") or ""
        except Exception:
            pass
    if url and commit:
        return url, commit
    return _infer_repo_from_dir(corpus_path.parent)


def main() -> None:
    raid_dir = Path(RAID_DIR)
    db_path = raid_dir / DB_FILE_NAME

    db: DynamicDatabase
    if not db_path.exists() or db_path.stat().st_size == 0:
        logger.info(f"Initializing new database at {db_path}")
        db = DynamicDatabase()
        db.to_json(str(db_path))
    else:
        logger.info(f"Loading database from {db_path}")
        db = DynamicDatabase.from_json(str(db_path))

    # Add repos discovered from existing corpora
    data_root = raid_dir / "data"
    if not data_root.exists():
        logger.warning(f"{data_root} does not exist. Checking {raid_dir} directly...")
        data_root = raid_dir

    targets = []
    for d, cj in iter_nonempty_corpora(data_root):
        try:
            # We don't strictly need url/commit here if we trust metadata.json, 
            # but it's good for logging.
            url, commit = load_repo_from_corpus(cj)
            targets.append((d, cj, url, commit))
        except Exception as e:
            logger.warning(f"Skipping {d} due to: {e}")

    logger.info(f"Found {len(targets)} repos with non-empty corpora to ingest")

    from dynamic_database import Repository
    import requests
    import re

    def get_lean_version_from_github(url, commit):
        """Fetch lean-toolchain from GitHub and parse version."""
        try:
            raw_url = url.replace("github.com", "raw.githubusercontent.com")
            config_url = f"{raw_url}/{commit}/lean-toolchain"
            response = requests.get(config_url, timeout=10)
            if response.status_code == 200:
                content = response.text.strip()
                # Parse version like "leanprover/lean4:v4.8.0" -> "v4.8.0"
                match = re.search(r"leanprover/lean4:(.+)", content)
                if match:
                    return match.group(1)
                return content # Fallback to full string if regex fails
        except Exception as e:
            logger.warning(f"Failed to fetch lean-toolchain for {url}@{commit}: {e}")
        return "v4.0.0" # Ultimate fallback

    for d, cj, url, commit in targets:
        logger.info(f"Ingesting {url}@{commit} from {d}")
        
        # 1. Read metadata.json
        meta_path = d / "metadata.json"
        meta = {}
        if meta_path.exists():
            try:
                with open(meta_path, "r") as f:
                    meta = json.load(f)
            except Exception as e:
                logger.error(f"Failed to read metadata for {d}: {e}")

        # 2. Construct Repository data
        from_repo = meta.get("from_repo", {})
        repo_url = from_repo.get("url", url)
        repo_commit = from_repo.get("commit", commit)
        
        date_processed = meta.get("date_processed")
        if not date_processed:
             date_processed = meta.get("creation_time", "2024-01-01T00:00:00.000000")

        lean_dojo_ver = meta.get("lean_dojo_version") or meta.get("leandojo_version", "0.0.1")
        
        # Fetch REAL Lean version if missing
        lean_ver = meta.get("lean_version")
        if not lean_ver:
            logger.info(f"Fetching real Lean version for {repo_url}...")
            lean_ver = get_lean_version_from_github(repo_url, repo_commit)
            logger.info(f"Got version: {lean_ver}")

        # Create dummy theorems folder if missing
        theorems_dir = d / "random"
        if not theorems_dir.exists():
            theorems_dir.mkdir(parents=True, exist_ok=True)

        repo_data = {
            "url": repo_url,
            "name": repo_url.split("/")[-1] if repo_url else d.name.split("_")[0],
            "commit": repo_commit,
            "lean_version": lean_ver,
            "lean_dojo_version": lean_dojo_ver,
            "metadata": {
                "date_processed": date_processed
            },
            "theorems_folder": str(theorems_dir),
            "premise_files_corpus": str(cj),
            "files_traced": str(d / "traced_files.jsonl")
        }

        # 3. Add to DB
        try:
            repo = Repository.from_dict(repo_data)
            db.add_repository(repo)
            logger.info(f"Successfully added {repo_url} to DB")
        except Exception as e:
            logger.error(f"Failed to add repo {repo_url} to DB: {e}")

    # Save updated database
    logger.info(f"Saving database with {len(db.repositories)} repositories to {db_path}")
    db.to_json(str(db_path))

    # Export merged dataset
    out_dir = raid_dir / "data" / "merged_paper_subset"
    logger.info(f"Generating merged dataset at {out_dir}")
    db.generate_merged_dataset(out_dir)
    logger.info("DONE.")


if __name__ == "__main__":
    if not os.environ.get("RAID_DIR"):
        raise SystemExit("Please set RAID_DIR and REPO_DIR before running.")
    main()
