"""
Policy-value neural network for chess.

Residual CNN architecture similar to AlphaZero.
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from typing import Tuple, Optional
import numpy as np


def residual_block(x: tf.Tensor, filters: int, kernel_size: int = 3) -> tf.Tensor:
    """Create a residual block with batch normalization and ReLU."""
    shortcut = x
    
    # First convolution
    x = layers.Conv2D(filters, kernel_size, padding='same')(x)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU()(x)
    
    # Second convolution
    x = layers.Conv2D(filters, kernel_size, padding='same')(x)
    x = layers.BatchNormalization()(x)
    
    # Add shortcut connection
    if shortcut.shape[-1] != filters:
        shortcut = layers.Conv2D(filters, 1, padding='same')(shortcut)
    
    x = layers.Add()([x, shortcut])
    x = layers.ReLU()(x)
    
    return x


def build_model(board_channels: int = 119, move_space: int = 4096, 
                width: int = 256, depth: int = 2, lr: float = 0.001,
                mixed_precision: bool = True) -> keras.Model:
    """
    Build the policy-value network.
    
    Args:
        board_channels: Number of input channels
        move_space: Size of move action space
        width: Network width (number of filters)
        depth: Number of residual blocks
        lr: Learning rate
        mixed_precision: Enable mixed precision training
        
    Returns:
        Compiled Keras model
    """
    if mixed_precision:
        policy = keras.mixed_precision.Policy('mixed_float16')
        keras.mixed_precision.set_global_policy(policy)
    
    # Input layer
    inputs = layers.Input(shape=(8, 8, board_channels), name='board')
    
    # Initial convolution
    x = layers.Conv2D(width, 3, padding='same')(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU()(x)
    
    # Residual blocks
    for _ in range(depth):
        x = residual_block(x, width)
    
    # Policy head
    policy_conv = layers.Conv2D(2, 1, padding='same')(x)
    policy_conv = layers.BatchNormalization()(policy_conv)
    policy_conv = layers.ReLU()(policy_conv)
    
    policy_flat = layers.Flatten()(policy_conv)
    policy_output = layers.Dense(move_space, name='policy', dtype='float32')(policy_flat)
    
    # Value head
    value_conv = layers.Conv2D(1, 1, padding='same')(x)
    value_conv = layers.BatchNormalization()(value_conv)
    value_conv = layers.ReLU()(value_conv)
    
    value_flat = layers.Flatten()(value_conv)
    value_hidden = layers.Dense(width, activation='relu')(value_flat)
    value_hidden = layers.Dropout(0.3)(value_hidden)
    value_output = layers.Dense(1, activation='tanh', name='value', dtype='float32')(value_hidden)
    
    # Create model
    model = keras.Model(inputs=inputs, outputs=[policy_output, value_output])
    
    # Compile with mixed precision
    if mixed_precision:
        optimizer = keras.optimizers.AdamW(learning_rate=lr, weight_decay=0.0001)
    else:
        optimizer = keras.optimizers.Adam(learning_rate=lr)
    
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
    
    return model


class PolicyValueNetwork:
    """Wrapper for policy-value network with prediction interface."""
    
    def __init__(self, model: keras.Model):
        """
        Initialize network wrapper.
        
        Args:
            model: Trained Keras model
        """
        self.model = model
    
    def predict_policy_value(self, board) -> Tuple[np.ndarray, float]:
        """
        Predict policy and value for a chess position.
        
        Args:
            board: Chess board position
            
        Returns:
            Tuple of (policy_vector, value)
        """
        # TODO: Convert board to feature planes
        # For now, return dummy predictions
        move_space = 4096  # Default move space size
        policy = np.random.random(move_space)
        value = np.random.uniform(-1, 1)
        
        return policy, value
    
    def predict_batch(self, boards) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict policy and value for a batch of positions.
        
        Args:
            boards: Batch of chess positions
            
        Returns:
            Tuple of (policy_batch, value_batch)
        """
        # TODO: Implement batch prediction
        batch_size = len(boards)
        move_space = 4096
        
        policy_batch = np.random.random((batch_size, move_space))
        value_batch = np.random.uniform(-1, 1, (batch_size, 1))
        
        return policy_batch, value_batch


def load_model(model_path: str) -> PolicyValueNetwork:
    """
    Load a trained model from file.
    
    Args:
        model_path: Path to saved model
        
    Returns:
        Loaded network wrapper
    """
    try:
        model = keras.models.load_model(model_path)
        return PolicyValueNetwork(model)
    except Exception as e:
        print(f"Failed to load model from {model_path}: {e}")
        # Return dummy network
        return PolicyValueNetwork(None)


def create_model_summary(board_channels: int = 119, move_space: int = 4096,
                         width: int = 256, depth: int = 2) -> str:
    """
    Create a summary of the model architecture.
    
    Args:
        board_channels: Number of input channels
        move_space: Size of move action space
        width: Network width
        depth: Number of residual blocks
        
    Returns:
        Model summary string
    """
    model = build_model(board_channels, move_space, width, depth)
    
    summary_lines = []
    model.summary(print_fn=lambda x: summary_lines.append(x))
    
    return '\n'.join(summary_lines)