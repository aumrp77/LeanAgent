#!/usr/bin/env python3
"""
Trace the fixed set of paper repos and materialize corpus.jsonl
next to RAID/data/<name>_<commit>/, mirroring the manual veil flow.

Run from repo root:
    export RAID_DIR="$PWD/RAID"
    export REPO_DIR="$RAID_DIR/repos"
    python scripts/trace_paper_repos.py
"""

import os
import json
import pathlib

from lean_dojo import LeanGitRepo
from lean_dojo.data_extraction.trace import get_traced_repo_path


# hardcoded list reconstructed from the paper / convo
PAPER_REPOS = [
    # 1. teorth/pfr
    # {
    #     "owner": "teorth",
    #     "name": "pfr",
    #     "sha": "fa398a5b853c7e94e3294c45e50c6aee013a2687",
    # },
    # 2. avigad/mathematics_in_lean_source
    {
        "owner": "avigad",
        "name": "mathematics_in_lean_source",
        "sha": "5297e0fb051367c48c0a084411853a576389ecf5",
    },
    {
        "owner": "verse-lab",
        "name": "veil",
        "sha": "a9fe7205c57f7b6ee8b350bfc87b9b4b28c57781",
    },
    # 3. miniF2F
    {
        "owner": "yangky11",
        "name": "miniF2F-lean4",
        "sha": "9e445f5435407f014b88b44a98436d50dd7abd00",
    },
    # 4. SciLean (in paper → we must make it work eventually)
    # {
    #     "owner": "lecopivo",
    #     "name": "SciLean",
    #     "sha": "22d53b2f4e3db2a172e71da6eb9c916e62655744",
    # },
    # 5. teorth/lean4-pdl
    {
        "owner": "teorth",
        "name": "lean4-pdl",
        "sha": "c7f649fe3c4891cf1a01c120e82ebc5f6199856e",
    },
    # 6. prime number theorem notes
    {
        "owner": "AlexKontorovich",
        "name": "PrimeNumberTheoremAnd",
        "sha": "29baddd685660b5fedd7bd67f9916ae24253d566",
    },
    # 7. compfiles
    {
        "owner": "dwrensha",
        "name": "compfiles",
        "sha": "f99bf6f2928d47dd1a445b414b3a723c2665f091",
    },
    # 8. FLT
    {
        "owner": "ImperialCollegeLondon",
        "name": "FLT",
        "sha": "b208a302cdcbfadce33d8165f0b054bfa17e2147",
    },
    {
        "owner": "verse-lab",
        "name": "veil",
        "sha": "a9fe7205c57f7b6ee8b350bfc87b9b4b28c57781",
    },
    # 9. lean4-cli (paper mentions tooling repos; we saw this in your crawl)
    {
        "owner": "leanprover-community",
        "name": "lean4-cli",
        "sha": "05b1f4a68c5facea96a5ee51c6a56fef21276e0f",
    },
    # 10. matrix cookbook
    {
        "owner": "eric-wieser",
        "name": "lean-matrix-cookbook",
        "sha": "f15a149d321ac99ff9b9c024b58e7882f564669f",
    },
    # 11. LeanEuclid
    {
        "owner": "loganrjmurphy",
        "name": "LeanEuclid",
        "sha": "f1912c3090eb82820575758efc31e40b9db86bb8",
    },
    # 12. formalized logic foundation
    {
        "owner": "FormalizedFormalLogic",
        "name": "Foundation",
        "sha": "d5fe5d057a90a0703a745cdc318a1b6621490c21",
    },
    # 13. con-nf
    {
        "owner": "pengbaolin",
        "name": "con-nf",
        "sha": "00bdc85ba7d486a9e544a0806a1018dd06fa3856",
    },
    # 14. zeta_3_irrational
    {
        "owner": "ahhwuhu",
        "name": "zeta_3_irrational",
        "sha": "914712200e463cfc97fe37e929d518dd58806a38",
    },
    # 15. LeanAPAP
    {
        "owner": "judicael-pvt",
        "name": "LeanAPAP",
        "sha": "951c660a8d7ba8e39f906fdf657674a984effa8b",
    },
    # paper had a few that we couldn't map to GH — keep extensible
]


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

        print(f"\n=== tracing {url}@{commit} ===")
        try:
            repo = LeanGitRepo(url, commit)
            traced_path = get_traced_repo_path(repo, build_deps=False)
            traced_path = pathlib.Path(traced_path)
            print(f"  lean_dojo traced into cache: {traced_path}")
        except Exception as e:
            print(f"  !! lean_dojo failed for {url}@{commit}: {e}")
            continue

        # repo as checked out by the earlier crawl
        repo_root = repo_dir / item["owner"] / item["name"]
        out_dir = raid_dir / "data" / f"{item['name']}_{commit}"

        if not repo_root.exists():
            print(f"  !! repo root {repo_root} not found — was it cloned under RAID/repos/?")

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
