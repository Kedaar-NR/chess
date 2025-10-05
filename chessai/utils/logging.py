"""
Logging utilities for chess AI.

Structured JSON logging for monitoring and debugging.
"""

import logging
import json
import sys
from typing import Dict, Any, Optional
from datetime import datetime
import os


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'extra'):
            log_entry.update(record.extra)
        
        return json.dumps(log_entry)


def setup_logging(config: Optional[Dict[str, Any]] = None) -> logging.Logger:
    """
    Setup logging configuration.
    
    Args:
        config: Logging configuration dictionary
        
    Returns:
        Configured logger
    """
    if config is None:
        config = {
            'level': 'INFO',
            'format': 'json',
            'output': 'stdout'
        }
    
    # Create logger
    logger = logging.getLogger('chessai')
    logger.setLevel(getattr(logging, config.get('level', 'INFO')))
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create handler
    if config.get('output') == 'file':
        log_file = config.get('log_file', 'chessai.log')
        handler = logging.FileHandler(log_file)
    else:
        handler = logging.StreamHandler(sys.stdout)
    
    # Set formatter
    if config.get('format') == 'json':
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Prevent duplicate logs
    logger.propagate = False
    
    return logger


def log_training_step(logger: logging.Logger, epoch: int, step: int, 
                     loss: float, metrics: Dict[str, float]) -> None:
    """Log training step information."""
    logger.info("Training step", extra={
        'epoch': epoch,
        'step': step,
        'loss': loss,
        'metrics': metrics,
        'type': 'training_step'
    })


def log_evaluation(logger: logging.Logger, position: str, move: str, 
                   score: float, nodes: int, time_ms: int) -> None:
    """Log position evaluation."""
    logger.info("Position evaluated", extra={
        'position': position,
        'move': move,
        'score': score,
        'nodes': nodes,
        'time_ms': time_ms,
        'type': 'evaluation'
    })


def log_game_result(logger: logging.Logger, result: str, moves: int, 
                   time_seconds: float) -> None:
    """Log game result."""
    logger.info("Game completed", extra={
        'result': result,
        'moves': moves,
        'time_seconds': time_seconds,
        'type': 'game_result'
    })


def log_model_save(logger: logging.Logger, model_path: str, 
                   epoch: int, metrics: Dict[str, float]) -> None:
    """Log model saving."""
    logger.info("Model saved", extra={
        'model_path': model_path,
        'epoch': epoch,
        'metrics': metrics,
        'type': 'model_save'
    })


def log_error(logger: logging.Logger, error: Exception, 
              context: Optional[Dict[str, Any]] = None) -> None:
    """Log error with context."""
    logger.error("Error occurred", extra={
        'error': str(error),
        'error_type': type(error).__name__,
        'context': context or {},
        'type': 'error'
    })


def create_logger(name: str, level: str = 'INFO') -> logging.Logger:
    """
    Create a logger with the specified name and level.
    
    Args:
        name: Logger name
        level: Log level
        
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = JSONFormatter()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False
    
    return logger
