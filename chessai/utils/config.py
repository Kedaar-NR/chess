"""
Configuration utilities for chess AI.

YAML configuration loading with type validation.
"""

import yaml
import os
from typing import Dict, Any, Optional, Union
from pathlib import Path


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Validate required sections
    required_sections = ['model', 'training', 'data']
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required configuration section: {section}")
    
    return config


def get_config_value(config: Dict[str, Any], key_path: str, 
                     default: Any = None) -> Any:
    """
    Get configuration value using dot notation.
    
    Args:
        config: Configuration dictionary
        key_path: Dot-separated key path (e.g., 'model.width')
        default: Default value if key not found
        
    Returns:
        Configuration value
    """
    keys = key_path.split('.')
    value = config
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    
    return value


def validate_config(config: Dict[str, Any]) -> None:
    """
    Validate configuration values.
    
    Args:
        config: Configuration dictionary
        
    Raises:
        ValueError: If configuration is invalid
    """
    # Validate model configuration
    model_config = config.get('model', {})
    if 'width' in model_config and model_config['width'] <= 0:
        raise ValueError("Model width must be positive")
    if 'depth' in model_config and model_config['depth'] <= 0:
        raise ValueError("Model depth must be positive")
    
    # Validate training configuration
    training_config = config.get('training', {})
    if 'batch_size' in training_config and training_config['batch_size'] <= 0:
        raise ValueError("Batch size must be positive")
    if 'learning_rate' in training_config and training_config['learning_rate'] <= 0:
        raise ValueError("Learning rate must be positive")
    
    # Validate data configuration
    data_config = config.get('data', {})
    if 'tfrecords_dir' in data_config:
        tfrecords_dir = data_config['tfrecords_dir']
        if not os.path.exists(tfrecords_dir):
            os.makedirs(tfrecords_dir, exist_ok=True)


def create_default_config() -> Dict[str, Any]:
    """
    Create default configuration.
    
    Returns:
        Default configuration dictionary
    """
    return {
        'model': {
            'board_channels': 119,
            'move_space': 4096,
            'width': 256,
            'depth': 2
        },
        'training': {
            'batch_size': 32,
            'learning_rate': 0.001,
            'epochs': 100,
            'optimizer': 'adamw',
            'weight_decay': 1e-4,
            'mixed_precision': True,
            'output_dir': 'runs/supervised'
        },
        'data': {
            'tfrecords_dir': 'data/tfrecords',
            'train_ratio': 0.8,
            'val_ratio': 0.1,
            'test_ratio': 0.1
        },
        'rl': {
            'buffer_size': 100000,
            'games_per_epoch': 100,
            'epochs': 50,
            'batch_size': 32,
            'min_buffer_size': 1000,
            'save_frequency': 10,
            'output_dir': 'runs/rl'
        },
        'logging': {
            'level': 'INFO',
            'format': 'json',
            'output': 'stdout'
        }
    }


def save_config(config: Dict[str, Any], output_path: str) -> None:
    """
    Save configuration to YAML file.
    
    Args:
        config: Configuration dictionary
        output_path: Output file path
    """
    with open(output_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, indent=2)


def merge_configs(base_config: Dict[str, Any], 
                  override_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two configurations, with override taking precedence.
    
    Args:
        base_config: Base configuration
        override_config: Override configuration
        
    Returns:
        Merged configuration
    """
    merged = base_config.copy()
    
    for key, value in override_config.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = merge_configs(merged[key], value)
        else:
            merged[key] = value
    
    return merged


def load_config_with_defaults(config_path: str, 
                             defaults_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration with defaults.
    
    Args:
        config_path: Path to configuration file
        defaults_path: Path to defaults file (optional)
        
    Returns:
        Configuration dictionary
    """
    # Load defaults
    if defaults_path and os.path.exists(defaults_path):
        defaults = load_config(defaults_path)
    else:
        defaults = create_default_config()
    
    # Load user config
    if os.path.exists(config_path):
        user_config = load_config(config_path)
        config = merge_configs(defaults, user_config)
    else:
        config = defaults
    
    # Validate configuration
    validate_config(config)
    
    return config
