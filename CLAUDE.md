# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Environment Setup
```bash
# Create and activate conda environment
conda create -n "LeanAgent" python=3.10
conda activate LeanAgent
pip install -r requirements.txt
```

### Running Tests
```bash
# Run the test suite
conda activate LeanAgent
python -m pytest tests/
```

### Running LeanAgent
```bash
# Main training/proving pipeline
bash run_leanagent.sh
```

### Fisher Information Matrix Computation (for EWC ablations)
```bash
# Compute Fisher Information Matrix
bash run_compute_fisher.sh
```

### Environment Configuration Required
Before running, update the following in shell scripts:
- `RAID_DIR`: Path to storage directory
- `PATH_TO_CONDA_ENV`: Path to conda installation  
- `GITHUB_ACCESS_TOKEN`: GitHub personal access token

## Architecture Overview

LeanAgent is a lifelong learning framework for formal theorem proving that continuously learns from expanding mathematical repositories without forgetting previous knowledge.

### Core Components

1. **Dynamic Database (`dynamic_database.py`)**: Central JSON-based storage system that manages mathematical knowledge across repositories. Tracks theorems (proven, sorry-but-now-proven, unproven), premise files, and repository metadata with deduplication capabilities.

2. **Repository Processing Pipeline**: 
   - Discovers and clones Lean repositories from GitHub
   - Uses LeanDojo to trace/extract theorems, proofs, and premises
   - Checks Lean version compatibility (4.3.0-rc2 to 4.8.0-rc1)
   - Builds dependency graphs and exports structured datasets

3. **Progressive Retriever Training (`retrieval/`)**:
   - Trains ByT5-based retriever incrementally on new repositories
   - Uses PyTorch Lightning with DDP for distributed training
   - Saves checkpoints based on R@10 validation performance
   - Measures both plasticity (new learning) and stability (retention)

4. **Theorem Proving (`prover/`)**:
   - Best-first tree search for sorry theorem proving
   - Uses trained retriever to find relevant premises
   - Generates tactic candidates with beam search
   - 10-minute timeout per theorem, processes in batches of 12

5. **Curriculum Learning**: Exponential complexity scoring (e^S where S = proof steps) with Easy/Medium/Hard categorization based on 33rd/67th percentiles.

### Key Configuration Points

The main configuration happens in `leanagent.py` where you must set:
- `repo_dir`: Repository path
- `DATA_DIR`: Data storage directory  
- `CHECKPOINT_DIR`: Model checkpoint directory
- `EVAL_RESULTS_FILE_PATH`: Evaluation results path
- `DB_FILE_NAME`: Database filename
- `PROOF_LOG_FILE_NAME`: Proof logging filename
- `ENCOUNTERED_THEOREMS_FILE`: Theorem tracking file
- `FISHER_DIR`: Fisher Information Matrix directory (optional)

### Distributed Computing
- Uses Ray for distributed repository processing
- PyTorch Lightning DDP for multi-GPU training (typically 4 A100s)
- Custom timeout settings for lengthy operations
- Resource cleanup between phases to prevent memory leaks

### Repository Integration
When theorems are successfully proven, LeanAgent can:
- Create temporary branches
- Replace `sorry` with generated proofs
- Submit pull requests to original repositories
- Use standardized commit messages and PR templates