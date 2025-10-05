"""
Chess position evaluation utilities.

Converts between neural network value outputs and centipawn scores.
"""

try:
    import chess
except ImportError:
    print("Warning: python-chess not installed. Install with: pip install python-chess")
    chess = None
from typing import Tuple
import math


def value_to_centipawns(value: float) -> int:
    """
    Convert neural network value (-1 to 1) to centipawns.
    
    Args:
        value: Neural network output in range [-1, 1]
        
    Returns:
        Centipawn score (positive for white advantage)
    """
    # Simple linear mapping: -1 -> -1000, 0 -> 0, 1 -> 1000
    return int(value * 1000)


def centipawns_to_value(cp: int) -> float:
    """
    Convert centipawn score to neural network value.
    
    Args:
        cp: Centipawn score
        
    Returns:
        Neural network value in range [-1, 1]
    """
    # Clamp to reasonable range and normalize
    cp = max(-1000, min(1000, cp))
    return cp / 1000.0


def evaluate_position(board: chess.Board) -> Tuple[float, int]:
    """
    Evaluate a chess position.
    
    Args:
        board: Chess position to evaluate
        
    Returns:
        Tuple of (value, centipawns) where value is in [-1, 1] and centipawns is the score
    """
    # Simple material evaluation as placeholder
    # TODO: Replace with neural network evaluation
    
    material_score = 0
    
    # Count material
    piece_values = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000
    }
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is not None:
            value = piece_values[piece.piece_type]
            if piece.color == chess.WHITE:
                material_score += value
            else:
                material_score -= value
    
    # Adjust for side to move
    if not board.turn:
        material_score = -material_score
    
    # Convert to value range [-1, 1]
    value = centipawns_to_value(material_score)
    
    return value, material_score


def is_winning_position(value: float, threshold: float = 0.8) -> bool:
    """Check if position is winning based on value."""
    return abs(value) > threshold


def is_drawish_position(value: float, threshold: float = 0.1) -> bool:
    """Check if position is drawish based on value."""
    return abs(value) < threshold