"""
Dataset utilities for chess training.

Handles TFRecord reading and preprocessing for supervised learning.
"""

import tensorflow as tf
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
import os
import glob


def parse_example(example_proto: tf.Tensor) -> Dict[str, tf.Tensor]:
    """
    Parse a single TFRecord example.
    
    Args:
        example_proto: Serialized example
        
    Returns:
        Dictionary of parsed features
    """
    feature_description = {
        'board_planes': tf.io.FixedLenFeature([], tf.string),
        'policy_index': tf.io.FixedLenFeature([], tf.int64),
        'value_target': tf.io.FixedLenFeature([], tf.float32),
        'legal_mask': tf.io.FixedLenFeature([], tf.string)
    }
    
    parsed = tf.io.parse_single_example(example_proto, feature_description)
    
    # Decode board planes
    board_planes = tf.io.parse_tensor(parsed['board_planes'], out_type=tf.float32)
    board_planes = tf.reshape(board_planes, [8, 8, -1])
    
    # Decode legal mask
    legal_mask = tf.io.parse_tensor(parsed['legal_mask'], out_type=tf.bool)
    
    return {
        'board_planes': board_planes,
        'policy_index': parsed['policy_index'],
        'value_target': parsed['value_target'],
        'legal_mask': legal_mask
    }


def make_dataset(paths: List[str], batch_size: int = 32, shuffle: bool = True, 
                repeat: bool = True, training: bool = True) -> tf.data.Dataset:
    """
    Create a TensorFlow dataset from TFRecord files.
    
    Args:
        paths: List of TFRecord file paths
        batch_size: Batch size
        shuffle: Whether to shuffle the dataset
        repeat: Whether to repeat the dataset
        training: Whether this is for training (affects augmentation)
        
    Returns:
        TensorFlow dataset
    """
    # Create file dataset
    files = tf.data.Dataset.list_files(paths)
    
    # Read TFRecords
    dataset = files.interleave(
        tf.data.TFRecordDataset,
        cycle_length=4,
        num_parallel_calls=tf.data.AUTOTUNE
    )
    
    # Parse examples
    dataset = dataset.map(parse_example, num_parallel_calls=tf.data.AUTOTUNE)
    
    # Cache for performance
    dataset = dataset.cache()
    
    # Shuffle if training
    if shuffle and training:
        dataset = dataset.shuffle(buffer_size=10000)
    
    # Repeat if specified
    if repeat:
        dataset = dataset.repeat()
    
    # Batch the dataset
    dataset = dataset.batch(batch_size, drop_remainder=training)
    
    # Prefetch for performance
    dataset = dataset.prefetch(tf.data.AUTOTUNE)
    
    return dataset


def create_legal_move_mask(board_planes: tf.Tensor, legal_mask: tf.Tensor) -> tf.Tensor:
    """
    Create legal move mask for policy loss.
    
    Args:
        board_planes: Board representation
        legal_mask: Legal move mask
        
    Returns:
        Legal move mask tensor
    """
    return legal_mask


def augment_position(board_planes: tf.Tensor, policy_index: tf.Tensor, 
                    legal_mask: tf.Tensor) -> Tuple[tf.Tensor, tf.Tensor, tf.Tensor]:
    """
    Augment chess position by rotation/reflection.
    
    Args:
        board_planes: Board representation
        policy_index: Policy target
        legal_mask: Legal move mask
        
    Returns:
        Augmented position
    """
    # Random horizontal flip
    if tf.random.uniform([]) < 0.5:
        board_planes = tf.image.flip_left_right(board_planes)
        # TODO: Update policy_index and legal_mask accordingly
    
    return board_planes, policy_index, legal_mask


def get_dataset_stats(dataset_path: str) -> Dict[str, Any]:
    """
    Get statistics about a dataset.
    
    Args:
        dataset_path: Path to dataset directory
        
    Returns:
        Dataset statistics
    """
    # Find all TFRecord files
    pattern = os.path.join(dataset_path, "*.tfrecord")
    files = glob.glob(pattern)
    
    if not files:
        return {"error": "No TFRecord files found"}
    
    # Count examples
    total_examples = 0
    for file_path in files:
        dataset = tf.data.TFRecordDataset(file_path)
        total_examples += sum(1 for _ in dataset)
    
    return {
        "num_files": len(files),
        "total_examples": total_examples,
        "files": files
    }


def create_splits(dataset_path: str, train_ratio: float = 0.8, 
                 val_ratio: float = 0.1, test_ratio: float = 0.1) -> Dict[str, List[str]]:
    """
    Create train/val/test splits from dataset.
    
    Args:
        dataset_path: Path to dataset directory
        train_ratio: Training set ratio
        val_ratio: Validation set ratio
        test_ratio: Test set ratio
        
    Returns:
        Dictionary with split file paths
    """
    # Find all TFRecord files
    pattern = os.path.join(dataset_path, "*.tfrecord")
    files = glob.glob(pattern)
    
    if not files:
        return {"train": [], "val": [], "test": []}
    
    # Shuffle files
    np.random.shuffle(files)
    
    # Calculate split indices
    n_files = len(files)
    train_end = int(n_files * train_ratio)
    val_end = train_end + int(n_files * val_ratio)
    
    return {
        "train": files[:train_end],
        "val": files[train_end:val_end],
        "test": files[val_end:]
    }


def load_dataset_splits(data_dir: str, batch_size: int = 32) -> Dict[str, tf.data.Dataset]:
    """
    Load train/val/test dataset splits.
    
    Args:
        data_dir: Data directory path
        batch_size: Batch size
        
    Returns:
        Dictionary with dataset splits
    """
    splits = create_splits(data_dir)
    
    datasets = {}
    for split_name, file_paths in splits.items():
        if file_paths:
            datasets[split_name] = make_dataset(
                file_paths, 
                batch_size=batch_size,
                shuffle=(split_name == 'train'),
                training=(split_name == 'train')
            )
        else:
            datasets[split_name] = None
    
    return datasets