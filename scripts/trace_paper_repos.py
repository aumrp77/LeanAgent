#!/usr/bin/env python3
"""
Trace the fixed set of paper repos and materialize corpus.jsonl
next to RAID/data/<name>_<commit>/, mirroring the manual veil flow.

Run from repo root:
    export RAID_DIR="$PWD/RAID"
    export REPO_DIR="$RAID_DIR/repos"
    python scripts/trace_paper_repos.py
"""

import json
import os
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve()
REPO_ROOT = HERE.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from lean_dojo import LeanGitRepo  # noqa: E402
from lean_dojo.data_extraction.trace import get_traced_repo_path  # noqa: E402


# hardcoded list reconstructed from the paper / convo
# ==== Already traced / paper list ====
PAPER_REPOS = [
    # {"owner": "teorth", "name": "pfr", "sha": "fa398a5b853c7e94e3294c45e50c6aee013a2687"},  # ALREADY TRACED
    # {"owner": "leanprover-community", "name": "hairy-ball-theorem", "sha": "a778826d19c8a7ddf1d26beeea628c45450612e6"},           # not found
    # {"owner": "leanprover-community", "name": "coxeter", "sha": "96af8aee7943ca8685ed1b00cc83a559ea389a97"},            # not found
    # {"owner": "avigad", "name": "mathematics_in_lean_source", "sha": "5297e0fb051367c48c0a084411853a576389ecf5"},  # ALREADY TRACED
    {"owner": "mo271", "name": "FormalBook", "sha": "6fbe8c2985008c0bfb30050750a71b90388ad3a3"},  # searched commit hashes; original table SHA/owner invalid
    # {"owner": "yangky11", "name": "miniF2F-lean4", "sha": "9e445f5435407f014b88b44a98436d50dd7abd00"},  # ALREADY TRACED
    # {"owner": "lecopivo", "name": "SciLean", "sha": "22d53b2f4e3db2a172e71da6eb9c916e62655744"},  # ALREADY TRACED
    {"owner": "fpvandoorn", "name": "carleson", "sha": "bec7808b907190882fa1fa54ce749af297c6cf37"},  # searched commit hashes; original table SHA/owner invalid
    {"owner": "m4lvin", "name": "lean4-pdl", "sha": "c7f649fe3c4891cf1a01c120e82ebc5f6199856e"},  # searched commit hashes; original table SHA/owner invalid
    # {"owner": "AlexKontorovich", "name": "PrimeNumberTheoremAnd", "sha": "29baddd685660b5fedd7bd67f9916ae24253d566"},  # ALREADY TRACED
    # {"owner": "dwrensha", "name": "compfiles", "sha": "f99bf6f2928d47dd1a445b414b3a723c2665f091"},  # ALREADY TRACED
    # {"owner": "ImperialCollegeLondon", "name": "FLT", "sha": "b208a302cdcbfadce33d8165f0b054bfa17e2147"},  # ALREADY TRACED
    # {"owner": "Bachmann", "name": "debate", "sha": "7fb39251b705797ee54e08c96177fabd29a5b5a3"},   # not found
    # {"owner": "digama0", "name": "lean4lean", "sha": "05b1f4a68c5facea96a5ee51c6a56fef21276e0f"},  # ALREADY TRACED
    # {"owner": "eric-wieser", "name": "lean-matrix-cookbook", "sha": "f15a149d321ac99ff9b9c024b58e7882f564669f"},  # ALREADY TRACED
    # {"owner": "yuma-mizuno", "name": "lean-math-workshop", "sha": "5acd4b933d47fd6c1032798a6046c1baf261445d"},  # ALREADY TRACED
    # {"owner": "loganrjmurphy", "name": "LeanEuclid", "sha": "f1912c3090eb82820575758efc31e40b9db86bb8"},                      SMT ERROR
    # {"owner": "FormalizedFormalLogic", "name": "Foundation", "sha": "d5fe5d057a90a0703a745cdc318a1b6621490c21"},                      SMT ERROR
    # {"owner": "leanprover-community", "name": "con-nf", "sha": "00bdc85ba7d486a9e544a0806a1018dd06fa3856"},  # ALREADY TRACED
    # {"owner": "siddhartha-gadgil", "name": "Saturn", "sha": "3811a9dd46cdfd5fa0c0c1896720c28d2ec4a42a"},    # ALREADY TRACED
    # {"owner": "ahhwuhu", "name": "zeta_3_irrational", "sha": "914712200e463cfc97fe37e929d518dd58806a38"},  # ALREADY TRACED
    # {"owner": "EmilGedda", "name": "Formalization-of-Constructable-Numbers", "sha": "01ef1f22a04f2ba8081c5fb29413f515a0e52878"},  # not found
    {"owner": "YaelDillies", "name": "LeanAPAP", "sha": "951c660a8d7ba8e39f906fdf657674a984effa8b"},  # searched commit hashes; original table SHA/owner invalid
]


PINNED_DEPS = {
    "loganrjmurphy/LeanEuclid": [
        {
            "url": "https://github.com/leanprover-community/mathlib4",
            "type": "git",
            "subDir": None,
            "rev": "b2c9f64fbc8dfe4c1b15b2bc6ab5a6f472fc047e",
            "name": "mathlib",
            "manifestFile": "lake-manifest.json",
            "inputRev": "b2c9f64fbc8dfe4c1b15b2bc6ab5a6f472fc047e",
            "inherited": False,
            "configFile": "lakefile.lean",
        },
        {
            "url": "https://github.com/yangky11/lean-smt.git",
            "type": "git",
            "subDir": None,
            "rev": "a3c0e8ab1e07d74b8fd745e7b3c4b83c6d859bbb",
            "name": "smt",
            "manifestFile": "lake-manifest.json",
            "inputRev": "a3c0e8ab1e07d74b8fd745e7b3c4b83c6d859bbb",
            "inherited": False,
            "configFile": "lakefile.lean",
        },
    ]
}


def apply_dependency_pins(repo_root: pathlib.Path, owner: str, name: str) -> None:
    repo_key = f"{owner}/{name}"
    targets = PINNED_DEPS.get(repo_key)
    if not targets:
        return

    manifest_path = repo_root / "lake-manifest.json"
    if manifest_path.exists():
        try:
            manifest = json.load(manifest_path.open())
        except json.JSONDecodeError:
            manifest = {}
    else:
        manifest = {}

    manifest.setdefault("packagesDir", ".lake/packages")
    packages = manifest.setdefault("packages", [])
    changed = False

    for target in targets:
        for pkg in packages:
            if pkg.get("name") == target["name"]:
                if pkg != target:
                    pkg.update(target)
                    changed = True
                break
        else:
            packages.append(dict(target))
            changed = True

    if changed:
        manifest_path.write_text(json.dumps(manifest, indent=2))
        print(f"  pinned lake-manifest.json for {repo_key}")

    lake_dir = repo_root / ".lake"
    if lake_dir.exists():
        shutil.rmtree(lake_dir)
        print(f"  removed stale .lake directory for {repo_key}")


def make_corpus_from_repo(source_root: pathlib.Path, out_dir: pathlib.Path, url: str, commit: str) -> int:
    """Scan .lake/build/ir for *.ast.json and write corpus.jsonl."""
    ir_root = source_root / ".lake" / "build" / "ir"
    if not ir_root.exists():
        print(f"  !! no .lake/build/ir in {source_root}, skipping corpus.jsonl")
        return 0

    recs = []
    for p in ir_root.rglob("*.ast.json"):
        recs.append(
            {
                "repo_url": url,
                "commit": commit,
                "ast_path": str(p.relative_to(source_root)),
            }
        )

    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "corpus.jsonl"
    with out_file.open("w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    print(f"  wrote {len(recs)} records to {out_file}")
    return len(recs)


def main() -> None:
    raid_dir = os.environ.get("RAID_DIR")
    repo_dir = os.environ.get("REPO_DIR")

    if not raid_dir or not repo_dir:
        raise SystemExit("Please set RAID_DIR and REPO_DIR before running.")

    raid_dir = pathlib.Path(raid_dir)
    repo_dir = pathlib.Path(repo_dir)

    for item in PAPER_REPOS:
        url = f"https://github.com/{item['owner']}/{item['name']}"
        commit = item["sha"]

        # repo as checked out by the earlier crawl
        repo_root = repo_dir / item["owner"] / item["name"]
        out_dir = raid_dir / "data" / f"{item['name']}_{commit}"

        if repo_root.exists():
            apply_dependency_pins(repo_root, item["owner"], item["name"])
        else:
            print(f"  !! repo root {repo_root} not found — was it cloned under RAID/repos/?")

        print(f"\n=== tracing {url}@{commit} ===")
        try:
            repo = LeanGitRepo(url, commit)
            traced_path = get_traced_repo_path(repo, build_deps=True)
            traced_path = pathlib.Path(traced_path)
            print(f"  lean_dojo traced into cache: {traced_path}")
        except Exception as e:
            print(f"  !! lean_dojo failed for {url}@{commit}: {e}")
            continue

        sources = [traced_path]
        if repo_root.exists():
            sources.append(repo_root)

        exported = 0
        for src in sources:
            exported = make_corpus_from_repo(src, out_dir, url, commit)
            if exported > 0:
                break

        if exported > 0:
            print(f"  ✅ exported corpus for {item['name']} ({exported} files)")
        else:
            print(f"  ⚠ traced but no IR — likely a build/env issue for this repo")

    print("\nDONE.")


if __name__ == "__main__":
    main()
