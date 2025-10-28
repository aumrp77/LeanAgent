import argparse, json, os, sys
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, help="Path to repo root (has .lake/)")
    ap.add_argument("--url", required=True, help="Repo URL (e.g. https://github.com/owner/name)")
    ap.add_argument("--commit", default="", help="Commit SHA (defaults to git rev-parse HEAD)")
    ap.add_argument("--out_root", required=True, help="Datasets root (e.g. RAID/data)")
    ap.add_argument("--zip", action="store_true", help="Also create a zip bundle with IR + corpus.jsonl")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    if not repo.exists():
        print(f"[ERR] Repo not found: {repo}", file=sys.stderr)
        sys.exit(2)

    # detect commit if not given
    commit = args.commit.strip()
    if not commit:
        import subprocess
        try:
            commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(repo)).decode().strip()
        except Exception as e:
            print(f"[ERR] Could not detect commit via git: {e}", file=sys.stderr)
            sys.exit(2)

    ir_root = repo / ".lake" / "build" / "ir"
    if not ir_root.is_dir():
        print(f"[ERR] IR dir not found: {ir_root}\nRun `lake build` first.", file=sys.stderr)
        sys.exit(2)

    asts = sorted(ir_root.rglob("*.ast.json"))
    if not asts:
        print(f"[ERR] No *.ast.json files under {ir_root}", file=sys.stderr)
        sys.exit(2)

    # dataset folder name: owner_repo_commit
    owner_repo = "/".join(args.url.rstrip("/").split("/")[-2:])
    owner_repo_flat = owner_repo.replace("/", "_")
    out_dir = Path(args.out_root) / f"{owner_repo_flat}_{commit}"
    out_dir.mkdir(parents=True, exist_ok=True)

    corpus_path = out_dir / "corpus.jsonl"
    with corpus_path.open("w") as f:
        for p in asts:
            rec = {
                "repo_url": args.url,
                "commit": commit,
                "ast_path": str(p.relative_to(repo)),
            }
            f.write(json.dumps(rec) + "\n")

    print(f"[OK] Wrote {corpus_path}  records: {len(asts)}")

    if args.zip:
        # bundle: corpus.jsonl + IR tree
        exports = Path(os.environ.get("RAID_DIR", repo.parent.parent)) / "exports"
        exports.mkdir(parents=True, exist_ok=True)
        zip_name = f"{owner_repo_flat}_{commit}_bundle.zip"
        zip_path = exports / zip_name

        # use system zip via subprocess to preserve paths
        import subprocess
        cmd = [
            "zip","-r", str(zip_path),
            str(corpus_path),
            str(ir_root),
            "-x","*.DS_Store"
        ]
        print("[ZIP] ", " ".join(cmd))
        subprocess.check_call(cmd, cwd=str(Path(os.environ.get("RAID_DIR", repo.parent.parent))))
        print(f"[OK] Bundle ready: {zip_path}")

if __name__ == "__main__":
    main()
