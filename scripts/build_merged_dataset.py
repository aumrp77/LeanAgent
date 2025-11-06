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
    targets = []
    for d, cj in iter_nonempty_corpora(data_root):
        try:
            url, commit = load_repo_from_corpus(cj)
            targets.append((url, commit))
        except Exception as e:
            logger.warning(f"Skipping {d} due to: {e}")

    logger.info(f"Found {len(targets)} repos with non-empty corpora to ingest")

    for url, commit in targets:
        repo = LeanGitRepo(url, commit)
        logger.info(f"Ingesting {url}@{commit}")
        status = add_repo_to_database(str(db_path), repo, db)
        logger.info(f"Status for {url}: {status}")

    # Export merged dataset
    out_dir = raid_dir / "data" / "merged_paper_subset"
    logger.info(f"Generating merged dataset at {out_dir}")
    db.generate_merged_dataset(out_dir)
    logger.info("DONE.")


if __name__ == "__main__":
    if not os.environ.get("RAID_DIR"):
        raise SystemExit("Please set RAID_DIR and REPO_DIR before running.")
    main()
