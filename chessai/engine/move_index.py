"""
Move indexing for chess positions.

Provides stable mapping between moves and integer IDs for policy vectors.
"""

import chess
from typing import Dict, List, Tuple, Optional


class MoveIndex:
    """Stable mapping from moves to integer IDs."""
    
    def __init__(self):
        """Initialize the move index."""
        self._move_to_id: Dict[str, int] = {}
        self._id_to_move: Dict[int, str] = {}
        self._next_id = 0
        
        # Generate all possible moves
        self._generate_all_moves()
    
    def _generate_all_moves(self) -> None:
        """Generate all possible chess moves and assign IDs."""
        # Generate moves for each square to each square
        for from_square in range(64):
            for to_square in range(64):
                if from_square == to_square:
                    continue
                    
                # Generate moves for each piece type
                for piece_type in [None, chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]:
                    move_str = self._move_to_string(from_square, to_square, piece_type)
                    if move_str not in self._move_to_id:
                        self._move_to_id[move_str] = self._next_id
                        self._id_to_move[self._next_id] = move_str
                        self._next_id += 1
    
    def _move_to_string(self, from_square: int, to_square: int, promotion: Optional[int] = None) -> str:
        """Convert move components to string representation."""
        from_sq = chess.square_name(from_square)
        to_sq = chess.square_name(to_square)
        
        if promotion is not None:
            piece_char = chess.piece_symbol(promotion).upper()
            return f"{from_sq}{to_sq}{piece_char}"
        else:
            return f"{from_sq}{to_sq}"
    
    def to_id(self, move: chess.Move) -> int:
        """Convert a chess move to its integer ID."""
        move_str = self._move_to_string(move.from_square, move.to_square, move.promotion)
        return self._move_to_id.get(move_str, -1)
    
    def from_id(self, move_id: int, board: chess.Board) -> Optional[chess.Move]:
        """Convert an integer ID to a chess move for the given board."""
        if move_id not in self._id_to_move:
            return None
            
        move_str = self._id_to_move[move_id]
        
        # Parse the move string
        if len(move_str) == 4:  # No promotion
            from_sq = chess.parse_square(move_str[:2])
            to_sq = chess.parse_square(move_str[2:])
            move = chess.Move(from_sq, to_sq)
        elif len(move_str) == 5:  # With promotion
            from_sq = chess.parse_square(move_str[:2])
            to_sq = chess.parse_square(move_str[2:4])
            promotion = chess.PIECE_SYMBOLS.index(move_str[4].lower())
            move = chess.Move(from_sq, to_sq, promotion=promotion)
        else:
            return None
        
        # Check if the move is legal in the current position
        if move in board.legal_moves:
            return move
        else:
            return None
    
    def action_space_size(self) -> int:
        """Return the total number of possible moves."""
        return self._next_id
    
    def get_legal_move_mask(self, board: chess.Board) -> List[bool]:
        """Get a boolean mask for legal moves in the current position."""
        mask = [False] * self.action_space_size()
        
        for move in board.legal_moves:
            move_id = self.to_id(move)
            if move_id >= 0:
                mask[move_id] = True
        
        return mask
    
    def get_legal_move_ids(self, board: chess.Board) -> List[int]:
        """Get list of legal move IDs for the current position."""
        legal_ids = []
        
        for move in board.legal_moves:
            move_id = self.to_id(move)
            if move_id >= 0:
                legal_ids.append(move_id)
        
        return legal_ids


# Global move index instance
move_index = MoveIndex()