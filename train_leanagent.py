import os
import sys
import json
import traceback
import torch
import pytorch_lightning as pl
from pytorch_lightning import seed_everything
from pytorch_lightning.callbacks import EarlyStopping, LearningRateMonitor, ModelCheckpoint
from pytorch_lightning.strategies import DDPStrategy
from datetime import timedelta
from loguru import logger

# Import from existing leanagent modules
from filenames import RAID_DIR, DATA_DIR, CHECKPOINT_DIR, DB_FILE_NAME
from dynamic_database import DynamicDatabase
from retrieval.datamodule import RetrievalDataModule
from retrieval.model import PremiseRetriever
import generate_benchmark_lean4

def initialize_database(dynamic_database_json_path: str) -> DynamicDatabase:
    """Initializes or loads the dynamic database."""
    if not os.path.exists(dynamic_database_json_path):
        raise FileNotFoundError(f"Database file not found at {dynamic_database_json_path}. Please run build_merged_dataset.py first.")
    
    logger.info(f"Loading database from {dynamic_database_json_path}")
    db = DynamicDatabase.from_json(dynamic_database_json_path)
    logger.info(f"Loaded database with {len(db.repositories)} repositories")
    return db

def main():
    """
    Simplified training script for LeanAgent.
    """
    try:
        # Configuration
        BATCH_SIZE = 4
        current_epoch = 0
        epochs_per_repo = 1 # We treat the merged dataset as one "repo" for epoch counting
        lambda_value = 0.1 # For progressive training
        
        # Paths
        if not RAID_DIR:
            raise ValueError("RAID_DIR environment variable is not set.")
            
        dynamic_database_json_path = os.path.join(RAID_DIR, DB_FILE_NAME)
        # We use the merged dataset we created
        # Note: build_merged_dataset.py created it at RAID_DIR/data/merged_paper_subset
        new_data_path = os.path.join(DATA_DIR, "merged_paper_subset")
        
        if not os.path.exists(new_data_path):
             raise FileNotFoundError(f"Merged dataset not found at {new_data_path}")

        # Setup
        logger.info("Configuring LeanDojo...")
        generate_benchmark_lean4.configure_leandojo()
        logger.info("LeanDojo configured")

        db = initialize_database(dynamic_database_json_path)
        
        # Training Setup
        logger.info("Starting Training Loop")
        
        # Find latest checkpoint or use default
        model_checkpoint_path = None
        try:
            # Simple logic to find latest checkpoint
            all_checkpoints = [os.path.join(CHECKPOINT_DIR, f) for f in os.listdir(CHECKPOINT_DIR) if f.endswith(".ckpt")]
            if all_checkpoints:
                model_checkpoint_path = max(all_checkpoints, key=os.path.getmtime)
                logger.info(f"Found latest checkpoint: {model_checkpoint_path}")
        except Exception as e:
            logger.warning(f"Could not find existing checkpoints: {e}")

        if not model_checkpoint_path:
             # Fallback to a base checkpoint if available, or let the model initialize from scratch/huggingface
             # The original script defaults to a specific mathlib checkpoint. 
             # We will try to use that if it exists, otherwise None (which might fail if PremiseRetriever expects it)
             default_ckpt = f"{RAID_DIR}/checkpoints/mathlib4_29dcec074de168ac2bf835a77ef68bbe069194c5.ckpt"
             if os.path.exists(default_ckpt):
                 model_checkpoint_path = default_ckpt
                 logger.info(f"Using default mathlib checkpoint: {model_checkpoint_path}")
             else:
                 logger.warning("No checkpoint found. Training might start from scratch or fail if a base model is required.")

        seed_everything(3407)
        
        if not torch.cuda.is_available():
            logger.warning("CUDA is not available. Training will be extremely slow on CPU.")
            device = torch.device("cpu")
        else:
            device = torch.device("cuda")

        config = {
            "model_name": "kaiyuy/leandojo-lean4-retriever-byt5-small",
            "lr": 1e-3,
            "warmup_steps": 1000,
            "max_seq_len": 512,
            "num_retrieved": 100,
        }

        # Load Model
        if model_checkpoint_path:
             model = PremiseRetriever.load(model_checkpoint_path, device, freeze=False, config=config)
             logger.info(f"Loaded premise retriever from {model_checkpoint_path}")
        else:
             # If no checkpoint, initialize fresh model from HuggingFace
             logger.info("Initializing new model from HuggingFace config...")
             model = PremiseRetriever(
                 model_name=config["model_name"],
                 lr=config["lr"],
                 warmup_steps=config["warmup_steps"],
                 max_seq_len=config["max_seq_len"],
                 num_retrieved=config["num_retrieved"]
             )

        model.train()
        model.set_lambda(lambda_value)

        # Callbacks
        dir_name = "merged_paper_subset"
        filename_suffix = f"_lambda_{lambda_value}"
        
        checkpoint_callback = ModelCheckpoint(
            dirpath=CHECKPOINT_DIR,
            filename=dir_name + filename_suffix + "_{epoch}-{Recall@10_val:.2f}",
            verbose=True,
            save_top_k=-1,
            every_n_epochs=1,
            monitor="Recall@10_val",
            mode="max",
        )

        early_stop_callback = EarlyStopping(
            monitor="Recall@10_val", patience=5, mode="max", verbose=True
        )

        lr_monitor = LearningRateMonitor(logging_interval="step")

        # Environment for DDP
        VERY_LONG_TIMEOUT = 7 * 24 * 60 * 60  # 1 week
        os.environ["TORCH_NCCL_ASYNC_ERROR_HANDLING"] = "1"
        os.environ["NCCL_TIMEOUT"] = str(VERY_LONG_TIMEOUT * 1000)

        custom_log_dir = os.path.join(RAID_DIR, "lightning_logs", f"{dir_name}_lambda_{lambda_value}")
        os.makedirs(custom_log_dir, exist_ok=True)

        # Trainer
        # Adjust devices based on availability
        num_gpus = torch.cuda.device_count()
        devices = num_gpus if num_gpus > 0 else 1
        accelerator = "gpu" if num_gpus > 0 else "cpu"
        strategy = DDPStrategy(timeout=timedelta(seconds=VERY_LONG_TIMEOUT)) if num_gpus > 1 else "auto"

        trainer = pl.Trainer(
            accelerator=accelerator,
            gradient_clip_val=1.0,
            precision="bf16-mixed" if num_gpus > 0 else 32, # bf16 might not work on CPU
            strategy=strategy,
            devices=devices,
            accumulate_grad_batches=4,
            callbacks=[lr_monitor, checkpoint_callback, early_stop_callback],
            max_epochs=current_epoch + 5, # Train for 5 epochs for now
            log_every_n_steps=1,
            num_sanity_val_steps=0,
            default_root_dir=custom_log_dir,
        )

        # Data Module
        corpus_path = os.path.join(new_data_path, "corpus.jsonl")
        data_path_random = os.path.join(new_data_path, "random")
        
        logger.info(f"Loading data from {data_path_random}")
        data_module = RetrievalDataModule(
            data_path=data_path_random,
            corpus_path=corpus_path,
            num_negatives=3,
            num_in_file_negatives=1,
            model_name="google/byt5-small",
            batch_size=BATCH_SIZE,
            eval_batch_size=64,
            max_seq_len=1024,
            num_workers=4,
        )
        data_module.setup(stage="fit")

        logger.info(f"Training dataset size: {len(data_module.ds_train)}")
        logger.info(f"Validation dataset size: {len(data_module.ds_val)}")

        # Train
        logger.info("Starting trainer.fit...")
        trainer.fit(model, datamodule=data_module, ckpt_path=model_checkpoint_path)
        logger.info("Training finished!")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
