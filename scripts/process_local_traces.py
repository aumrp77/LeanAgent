import json
import pathlib
import os
import shutil
import sys

# Add the parent directory (LeanAgent root) to sys.path to allow imports
current_dir = pathlib.Path(__file__).parent.resolve()
lean_agent_root = current_dir.parent
sys.path.insert(0, str(lean_agent_root))

from lean_dojo.data_extraction.traced_data import TracedRepo
from generate_benchmark_lean4 import export_premises, export_proofs, split_data, export_metadata

def process_repo(source_root: pathlib.Path, out_dir: pathlib.Path, url: str, commit: str) -> bool:
    """
    Load a traced Lean repository from source_root,
    export premises to corpus.jsonl, and export theorems to random/.
    """
    print(f"  Loading TracedRepo from {source_root}...")
    try:
        traced_repo = TracedRepo.from_traced_files(source_root, build_deps=True)
    except Exception as e:
        print(f"  !! Failed to load TracedRepo: {e}")
        return False
        
    print(f"  Exporting to {out_dir}...")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Export premises to corpus.jsonl
    try:
        export_premises(traced_repo, out_dir)
        print(f"    ✓ Exported premises → {out_dir / 'corpus.jsonl'}")
    except Exception as e:
        print(f"  !! Failed to export premises: {e}")
        return False

    # Step 2: Export theorems (THE FIX - this was missing!)
    try:
        print(f"    Extracting theorems...")
        splits = split_data(traced_repo, num_val_pct=0.02, num_test_pct=0.02)
        total_theorems = export_proofs(splits, out_dir, traced_repo)
        export_metadata(traced_repo, out_dir)  # Fixed: removed splits argument
        print(f"    ✓ Exported {total_theorems} theorems → {out_dir / 'random/'}")
    except Exception as e:
        print(f"  !! Failed to export theorems: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

# VM repo paths - comment out repos you want to skip
VM_REPOS = [
    {"name": "FLT", "owner": "ImperialCollegeLondon", "commit": "b208a302cdcbfadce33d8165f0b054bfa17e2147", "local_path": "/home/aum/repos_cache/FLT/ImperialCollegeLondon-FLT-b208a302cdcbfadce33d8165f0b054bfa17e2147/FLT"},
    {"name": "formal_book", "owner": "mo271", "commit": "6fbe8c2985008c0bfb30050750a71b90388ad3a3", "local_path": "/home/aum/repos_cache/FormalBook/mo271-formal_book-6fbe8c2985008c0bfb30050750a71b90388ad3a3/formal_book"},
    {"name": "Formalisation-of-constructable-numbers", "owner": "Louis", "commit": "01ef1f22a04f2ba8081c5fb29413f515a0e52878", "local_path": "/home/aum/repos_cache/Formalization-of-Constructable-Numbers/Louis-Le-Grand-Formalisation-of-constructable-numbers-01ef1f22a04f2ba8081c5fb29413f515a0e52878/Formalisation-of-constructable-numbers"},
    {"name": "Foundation", "owner": "FormalizedFormalLogic", "commit": "d5fe5d057a90a0703a745cdc318a1b6621490c21", "local_path": "/home/aum/repos_cache/Foundation/FormalizedFormalLogic-Foundation-d5fe5d057a90a0703a745cdc318a1b6621490c21/Foundation"},
    {"name": "LeanAPAP", "owner": "YaelDillies", "commit": "951c660a8d7ba8e39f906fdf657674a984effa8b", "local_path": "/home/aum/repos_cache/LeanAPAP/YaelDillies-LeanAPAP-951c660a8d7ba8e39f906fdf657674a984effa8b/LeanAPAP"},
    {"name": "LeanEuclid", "owner": "loganrjmurphy", "commit": "f1912c3090eb82820575758efc31e40b9db86bb8", "local_path": "/home/aum/repos_cache/LeanEuclid/loganrjmurphy-LeanEuclid-f1912c3090eb82820575758efc31e40b9db86bb8/LeanEuclid"},
    {"name": "PrimeNumberTheoremAnd", "owner": "AlexKontorovich", "commit": "29baddd685660b5fedd7bd67f9916ae24253d566", "local_path": "/home/aum/repos_cache/PrimeNumberTheoremAnd/AlexKontorovich-PrimeNumberTheoremAnd-29baddd685660b5fedd7bd67f9916ae24253d566/PrimeNumberTheoremAnd"},
    {"name": "Saturn", "owner": "siddhartha", "commit": "3811a9dd46cdfd5fa0c0c1896720c28d2ec4a42a", "local_path": "/home/aum/repos_cache/Saturn/siddhartha-gadgil-Saturn-3811a9dd46cdfd5fa0c0c1896720c28d2ec4a42a/Saturn"},
    {"name": "SciLean", "owner": "lecopivo", "commit": "22d53b2f4e3db2a172e71da6eb9c916e62655744", "local_path": "/home/aum/repos_cache/SciLean/lecopivo-SciLean-22d53b2f4e3db2a172e71da6eb9c916e62655744/SciLean"},
    {"name": "carleson", "owner": "fpvandoorn", "commit": "bec7808b907190882fa1fa54ce749af297c6cf37", "local_path": "/home/aum/repos_cache/carleson/fpvandoorn-carleson-bec7808b907190882fa1fa54ce749af297c6cf37/carleson"},
    {"name": "compfiles", "owner": "dwrensha", "commit": "f99bf6f2928d47dd1a445b414b3a723c2665f091", "local_path": "/home/aum/repos_cache/compfiles/dwrensha-compfiles-f99bf6f2928d47dd1a445b414b3a723c2665f091/compfiles"},
    {"name": "con-nf", "owner": "leanprover", "commit": "00bdc85ba7d486a9e544a0806a1018dd06fa3856", "local_path": "/home/aum/repos_cache/con-nf/leanprover-community-con-nf-00bdc85ba7d486a9e544a0806a1018dd06fa3856/con-nf"},
    {"name": "coxeter", "owner": "NUS", "commit": "96af8aee7943ca8685ed1b00cc83a559ea389a97", "local_path": "/home/aum/repos_cache/coxeter/NUS-Math-Formalization-coxeter-96af8aee7943ca8685ed1b00cc83a559ea389a97/coxeter"},
    {"name": "hairy-ball-theorem-lean", "owner": "corent1234", "commit": "a778826d19c8a7ddf1d26beeea628c45450612e6", "local_path": "/home/aum/repos_cache/hairy-ball-theorem/corent1234-hairy-ball-theorem-lean-a778826d19c8a7ddf1d26beeea628c45450612e6/hairy-ball-theorem-lean"},
    {"name": "lean-math-workshop", "owner": "yuma", "commit": "5acd4b933d47fd6c1032798a6046c1baf261445d", "local_path": "/home/aum/repos_cache/lean-math-workshop/yuma-mizuno-lean-math-workshop-5acd4b933d47fd6c1032798a6046c1baf261445d/lean-math-workshop"},
    {"name": "lean-matrix-cookbook", "owner": "eric", "commit": "f15a149d321ac99ff9b9c024b58e7882f564669f", "local_path": "/home/aum/repos_cache/lean-matrix-cookbook/eric-wieser-lean-matrix-cookbook-f15a149d321ac99ff9b9c024b58e7882f564669f/lean-matrix-cookbook"},
    {"name": "lean4-pdl", "owner": "m4lvin", "commit": "c7f649fe3c4891cf1a01c120e82ebc5f6199856e", "local_path": "/home/aum/repos_cache/lean4-pdl/m4lvin-lean4-pdl-c7f649fe3c4891cf1a01c120e82ebc5f6199856e/lean4-pdl"},
    {"name": "lean4lean", "owner": "digama0", "commit": "05b1f4a68c5facea96a5ee51c6a56fef21276e0f", "local_path": "/home/aum/repos_cache/lean4lean/digama0-lean4lean-05b1f4a68c5facea96a5ee51c6a56fef21276e0f/lean4lean"},
    {"name": "mathematics_in_lean_source", "owner": "avigad", "commit": "5297e0fb051367c48c0a084411853a576389ecf5", "local_path": "/home/aum/repos_cache/mathematics_in_lean_source/avigad-mathematics_in_lean_source-5297e0fb051367c48c0a084411853a576389ecf5/mathematics_in_lean_source"},
    {"name": "miniF2F-lean4", "owner": "yangky11", "commit": "9e445f5435407f014b88b44a98436d50dd7abd00", "local_path": "/home/aum/repos_cache/miniF2F-lean4/yangky11-miniF2F-lean4-9e445f5435407f014b88b44a98436d50dd7abd00/miniF2F-lean4"},
    {"name": "pfr", "owner": "teorth", "commit": "fa398a5b853c7e94e3294c45e50c6aee013a2687", "local_path": "/home/aum/repos_cache/pfr/teorth-pfr-fa398a5b853c7e94e3294c45e50c6aee013a2687/pfr"},
    {"name": "zeta_3_irrational", "owner": "ahhwuhu", "commit": "914712200e463cfc97fe37e929d518dd58806a38", "local_path": "/home/aum/repos_cache/zeta_3_irrational/ahhwuhu-zeta_3_irrational-914712200e463cfc97fe37e929d518dd58806a38/zeta_3_irrational"},
]

def main():
    # Configuration for VM
    raid_dir = pathlib.Path.home() / "LeanAgent" / "RAID"
    
    print("="*80)
    print("VM BATCH EXTRACTION - Processing Local Traces (Sequential)")
    print("="*80)
    print(f"Found {len(VM_REPOS)} repos to process")
    print("="*80)
    
    successful = []
    failed = []

    for i, repo in enumerate(VM_REPOS, 1):
        print(f"\n[{i}/{len(VM_REPOS)}] Processing {repo['name']}...")
        source_root = pathlib.Path(repo["local_path"])
        
        if not source_root.exists():
            print(f"  !! Source path does not exist: {source_root}")
            failed.append(repo['name'])
            continue

        out_dir = raid_dir / "data" / f"{repo['name']}_{repo['commit']}"
        url = f"https://github.com/{repo['owner']}/{repo['name']}"
        
        success = process_repo(source_root, out_dir, url, repo["commit"])
        
        if success:
            print(f"  ✓ Successfully processed {repo['name']}.")
            successful.append(repo['name'])
        else:
            print(f"  ✗ Failed to process {repo['name']}.")
            failed.append(repo['name'])
    
    # Summary
    print("\n" + "="*80)
    print("EXTRACTION SUMMARY")
    print("="*80)
    print(f"\n✓ Successful: {len(successful)}/{len(VM_REPOS)}")
    for name in successful:
        print(f"  - {name}")
    
    if failed:
        print(f"\n✗ Failed: {len(failed)}/{len(VM_REPOS)}")
        for name in failed:
            print(f"  - {name}")
    
    print(f"\nResults saved to: {raid_dir / 'data'}")
    print("="*80)

if __name__ == "__main__":
    main()
