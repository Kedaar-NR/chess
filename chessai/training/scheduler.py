"""
Learning rate scheduler for chess training.

Cosine schedule with warmup for stable training.
"""

import tensorflow as tf
from tensorflow import keras
from typing import Optional, Dict, Any
import math


class CosineWarmupScheduler(keras.callbacks.Callback):
    """Cosine learning rate schedule with warmup."""
    
    def __init__(self, warmup_steps: int, total_steps: int, 
                 base_lr: float = 1e-3, min_lr: float = 1e-6):
        """
        Initialize cosine warmup scheduler.
        
        Args:
            warmup_steps: Number of warmup steps
            total_steps: Total training steps
            base_lr: Base learning rate
            min_lr: Minimum learning rate
        """
        super().__init__()
        self.warmup_steps = warmup_steps
        self.total_steps = total_steps
        self.base_lr = base_lr
        self.min_lr = min_lr
    
    def on_train_batch_begin(self, batch: int, logs: Optional[Dict[str, Any]] = None) -> None:
        """Update learning rate at the beginning of each batch."""
        if hasattr(self.model, 'optimizer'):
            lr = self._get_lr(batch)
            tf.keras.backend.set_value(self.model.optimizer.learning_rate, lr)
    
    def _get_lr(self, step: int) -> float:
        """Get learning rate for current step."""
        if step < self.warmup_steps:
            # Warmup phase
            return self.base_lr * (step / self.warmup_steps)
        else:
            # Cosine decay phase
            progress = (step - self.warmup_steps) / (self.total_steps - self.warmup_steps)
            progress = min(progress, 1.0)
            cosine_decay = 0.5 * (1 + math.cos(math.pi * progress))
            return self.min_lr + (self.base_lr - self.min_lr) * cosine_decay


def create_lr_schedule(warmup_steps: int, total_steps: int, 
                       base_lr: float = 1e-3, min_lr: float = 1e-6) -> tf.keras.optimizers.schedules.LearningRateSchedule:
    """
    Create a learning rate schedule function.
    
    Args:
        warmup_steps: Number of warmup steps
        total_steps: Total training steps
        base_lr: Base learning rate
        min_lr: Minimum learning rate
        
    Returns:
        Learning rate schedule
    """
    def lr_schedule(step):
        if step < warmup_steps:
            return base_lr * (step / warmup_steps)
        else:
            progress = (step - warmup_steps) / (total_steps - warmup_steps)
            progress = min(progress, 1.0)
            cosine_decay = 0.5 * (1 + math.cos(math.pi * progress))
            return min_lr + (base_lr - min_lr) * cosine_decay
    
    return lr_schedule


class StepDecayScheduler(keras.callbacks.Callback):
    """Step decay learning rate scheduler."""
    
    def __init__(self, decay_steps: int, decay_rate: float = 0.1, 
                 base_lr: float = 1e-3, min_lr: float = 1e-6):
        """
        Initialize step decay scheduler.
        
        Args:
            decay_steps: Steps between decay
            decay_rate: Decay rate
            base_lr: Base learning rate
            min_lr: Minimum learning rate
        """
        super().__init__()
        self.decay_steps = decay_steps
        self.decay_rate = decay_rate
        self.base_lr = base_lr
        self.min_lr = min_lr
    
    def on_train_batch_begin(self, batch: int, logs: Optional[Dict[str, Any]] = None) -> None:
        """Update learning rate at the beginning of each batch."""
        if hasattr(self.model, 'optimizer'):
            lr = self._get_lr(batch)
            tf.keras.backend.set_value(self.model.optimizer.learning_rate, lr)
    
    def _get_lr(self, step: int) -> float:
        """Get learning rate for current step."""
        decay_count = step // self.decay_steps
        lr = self.base_lr * (self.decay_rate ** decay_count)
        return max(lr, self.min_lr)


def create_optimizer(optimizer_type: str = 'adamw', lr: float = 1e-3, 
                     weight_decay: float = 1e-4, **kwargs) -> keras.optimizers.Optimizer:
    """
    Create optimizer for training.
    
    Args:
        optimizer_type: Type of optimizer
        lr: Learning rate
        weight_decay: Weight decay
        **kwargs: Additional optimizer arguments
        
    Returns:
        Keras optimizer
    """
    if optimizer_type.lower() == 'adamw':
        return keras.optimizers.AdamW(
            learning_rate=lr,
            weight_decay=weight_decay,
            **kwargs
        )
    elif optimizer_type.lower() == 'adam':
        return keras.optimizers.Adam(
            learning_rate=lr,
            **kwargs
        )
    elif optimizer_type.lower() == 'sgd':
        return keras.optimizers.SGD(
            learning_rate=lr,
            momentum=0.9,
            **kwargs
        )
    else:
        raise ValueError(f"Unknown optimizer type: {optimizer_type}")


def create_callbacks(log_dir: str, save_dir: str, 
                     save_freq: int = 1000) -> list:
    """
    Create training callbacks.
    
    Args:
        log_dir: Directory for TensorBoard logs
        save_dir: Directory for model checkpoints
        save_freq: Save frequency in steps
        
    Returns:
        List of callbacks
    """
    callbacks = [
        # TensorBoard logging
        keras.callbacks.TensorBoard(
            log_dir=log_dir,
            histogram_freq=1,
            write_graph=True,
            update_freq='batch'
        ),
        
        # Model checkpointing
        keras.callbacks.ModelCheckpoint(
            filepath=os.path.join(save_dir, 'checkpoint-{epoch:02d}-{loss:.4f}.h5'),
            save_best_only=True,
            monitor='val_loss',
            mode='min',
            save_freq=save_freq
        ),
        
        # Early stopping
        keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        ),
        
        # Reduce learning rate on plateau
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-6
        )
    ]
    
    return callbacks