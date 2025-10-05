"""
Loss functions for chess training.

Combined policy and value losses with regularization.
"""

import tensorflow as tf
from tensorflow import keras
from typing import Dict, Any


def policy_loss(y_true: tf.Tensor, y_pred: tf.Tensor, 
                legal_mask: tf.Tensor, label_smoothing: float = 0.1) -> tf.Tensor:
    """
    Policy loss with legal move masking and label smoothing.
    
    Args:
        y_true: True policy indices
        y_pred: Predicted policy logits
        legal_mask: Legal move mask
        label_smoothing: Label smoothing factor
        
    Returns:
        Policy loss
    """
    # Apply legal move mask
    masked_logits = tf.where(legal_mask, y_pred, tf.fill(tf.shape(y_pred), -1e9))
    
    # Apply label smoothing
    if label_smoothing > 0:
        num_classes = tf.shape(y_pred)[-1]
        smooth_labels = tf.one_hot(y_true, num_classes, dtype=tf.float32)
        smooth_labels = smooth_labels * (1 - label_smoothing) + label_smoothing / num_classes
        loss = tf.keras.losses.categorical_crossentropy(smooth_labels, masked_logits, from_logits=True)
    else:
        loss = tf.keras.losses.sparse_categorical_crossentropy(y_true, masked_logits, from_logits=True)
    
    return tf.reduce_mean(loss)


def value_loss(y_true: tf.Tensor, y_pred: tf.Tensor) -> tf.Tensor:
    """
    Value loss using mean squared error.
    
    Args:
        y_true: True values
        y_pred: Predicted values
        
    Returns:
        Value loss
    """
    return tf.keras.losses.mean_squared_error(y_true, y_pred)


def l2_regularization(model: keras.Model, l2_lambda: float = 1e-4) -> tf.Tensor:
    """
    L2 regularization loss.
    
    Args:
        model: Keras model
        l2_lambda: L2 regularization factor
        
    Returns:
        L2 regularization loss
    """
    l2_loss = 0
    for layer in model.layers:
        if hasattr(layer, 'kernel') and layer.kernel is not None:
            l2_loss += tf.nn.l2_loss(layer.kernel)
        if hasattr(layer, 'bias') and layer.bias is not None:
            l2_loss += tf.nn.l2_loss(layer.bias)
    
    return l2_lambda * l2_loss


def combined_loss(y_true: Dict[str, tf.Tensor], y_pred: Dict[str, tf.Tensor], 
                  model: keras.Model, policy_weight: float = 1.0, 
                  value_weight: float = 1.0, l2_lambda: float = 1e-4) -> tf.Tensor:
    """
    Combined loss function for policy and value.
    
    Args:
        y_true: True targets
        y_pred: Predictions
        model: Keras model
        policy_weight: Weight for policy loss
        value_weight: Weight for value loss
        l2_lambda: L2 regularization factor
        
    Returns:
        Combined loss
    """
    # Policy loss
    policy_loss = policy_loss(
        y_true['policy'], 
        y_pred['policy'], 
        y_true.get('legal_mask', None)
    )
    
    # Value loss
    value_loss_val = value_loss(y_true['value'], y_pred['value'])
    
    # L2 regularization
    l2_loss = l2_regularization(model, l2_lambda)
    
    # Combined loss
    total_loss = (policy_weight * policy_loss + 
                  value_weight * value_loss_val + 
                  l2_loss)
    
    return total_loss


class ChessLoss(keras.losses.Loss):
    """Custom loss class for chess training."""
    
    def __init__(self, policy_weight: float = 1.0, value_weight: float = 1.0, 
                 l2_lambda: float = 1e-4, label_smoothing: float = 0.1, **kwargs):
        """
        Initialize chess loss.
        
        Args:
            policy_weight: Weight for policy loss
            value_weight: Weight for value loss
            l2_lambda: L2 regularization factor
            label_smoothing: Label smoothing factor
        """
        super().__init__(**kwargs)
        self.policy_weight = policy_weight
        self.value_weight = value_weight
        self.l2_lambda = l2_lambda
        self.label_smoothing = label_smoothing
    
    def call(self, y_true: Dict[str, tf.Tensor], y_pred: Dict[str, tf.Tensor]) -> tf.Tensor:
        """Compute loss."""
        # Policy loss
        policy_loss = policy_loss(
            y_true['policy'], 
            y_pred['policy'], 
            y_true.get('legal_mask', None),
            self.label_smoothing
        )
        
        # Value loss
        value_loss_val = value_loss(y_true['value'], y_pred['value'])
        
        # Combined loss
        total_loss = (self.policy_weight * policy_loss + 
                      self.value_weight * value_loss_val)
        
        return total_loss


def create_loss_metrics() -> Dict[str, keras.metrics.Metric]:
    """
    Create loss metrics for monitoring.
    
    Returns:
        Dictionary of metrics
    """
    return {
        'policy_loss': keras.metrics.Mean(name='policy_loss'),
        'value_loss': keras.metrics.Mean(name='value_loss'),
        'total_loss': keras.metrics.Mean(name='total_loss'),
        'policy_accuracy': keras.metrics.SparseCategoricalAccuracy(name='policy_accuracy'),
        'value_mae': keras.metrics.MeanAbsoluteError(name='value_mae')
    }