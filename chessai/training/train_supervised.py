"""
Supervised training script for chess AI.

Trains policy-value network on expert games.
"""

import os
import sys
import argparse
import yaml
import tensorflow as tf
from tensorflow import keras
import numpy as np
from typing import Dict, Any, Optional

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from chessai.models.policy_value import build_model
from chessai.training.dataset import load_dataset_splits
from chessai.training.losses import ChessLoss, create_loss_metrics
from chessai.training.scheduler import CosineWarmupScheduler, create_optimizer, create_callbacks
from chessai.utils.config import load_config
from chessai.utils.logging import setup_logging


def train_supervised(config_path: str, model_path: Optional[str] = None) -> None:
    """
    Train the supervised model.
    
    Args:
        config_path: Path to configuration file
        model_path: Path to pretrained model (optional)
    """
    # Load configuration
    config = load_config(config_path)
    
    # Setup logging
    logger = setup_logging(config.get('logging', {}))
    
    # Load datasets
    logger.info("Loading datasets...")
    datasets = load_dataset_splits(
        config['data']['tfrecords_dir'],
        batch_size=config['training']['batch_size']
    )
    
    if datasets['train'] is None:
        logger.error("No training data found!")
        return
    
    # Build model
    logger.info("Building model...")
    model = build_model(
        board_channels=config['model']['board_channels'],
        move_space=config['model']['move_space'],
        width=config['model']['width'],
        depth=config['model']['depth'],
        lr=config['training']['learning_rate'],
        mixed_precision=config['training'].get('mixed_precision', True)
    )
    
    # Load pretrained model if specified
    if model_path and os.path.exists(model_path):
        logger.info(f"Loading pretrained model from {model_path}")
        model.load_weights(model_path)
    
    # Create optimizer
    optimizer = create_optimizer(
        optimizer_type=config['training']['optimizer'],
        lr=config['training']['learning_rate'],
        weight_decay=config['training'].get('weight_decay', 1e-4)
    )
    
    # Compile model
    model.compile(
        optimizer=optimizer,
        loss={
            'policy': 'sparse_categorical_crossentropy',
            'value': 'mse'
        },
        loss_weights={
            'policy': 1.0,
            'value': 1.0
        },
        metrics={
            'policy': 'sparse_categorical_accuracy',
            'value': 'mae'
        }
    )
    
    # Create callbacks
    log_dir = os.path.join(config['training']['output_dir'], 'logs')
    save_dir = os.path.join(config['training']['output_dir'], 'checkpoints')
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(save_dir, exist_ok=True)
    
    callbacks = create_callbacks(log_dir, save_dir)
    
    # Add learning rate scheduler
    total_steps = config['training']['epochs'] * len(datasets['train'])
    warmup_steps = config['training'].get('warmup_steps', total_steps // 10)
    
    lr_scheduler = CosineWarmupScheduler(
        warmup_steps=warmup_steps,
        total_steps=total_steps,
        base_lr=config['training']['learning_rate']
    )
    callbacks.append(lr_scheduler)
    
    # Train model
    logger.info("Starting training...")
    history = model.fit(
        datasets['train'],
        validation_data=datasets['val'],
        epochs=config['training']['epochs'],
        callbacks=callbacks,
        verbose=1
    )
    
    # Save final model
    final_model_path = os.path.join(config['training']['output_dir'], 'final_model.h5')
    model.save(final_model_path)
    logger.info(f"Saved final model to {final_model_path}")
    
    # Save best model
    best_model_path = os.path.join(config['training']['output_dir'], 'best_model.h5')
    model.save(best_model_path)
    logger.info(f"Saved best model to {best_model_path}")
    
    logger.info("Training completed!")


def main():
    """Main training function."""
    parser = argparse.ArgumentParser(description='Train supervised chess model')
    parser.add_argument('--config', type=str, required=True,
                       help='Path to configuration file')
    parser.add_argument('--model', type=str, default=None,
                       help='Path to pretrained model')
    
    args = parser.parse_args()
    
    try:
        train_supervised(args.config, args.model)
    except Exception as e:
        print(f"Training failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()