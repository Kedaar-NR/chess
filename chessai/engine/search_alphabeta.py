"""
Alpha-beta search implementation for chess.

Fallback search algorithm with iterative deepening and heuristics.
"""

import chess
import time
from typing import List, Optional, Tuple, Dict, Any
from .evaluation import evaluate_position, value_to_centipawns


class AlphaBetaSearch:
    """Alpha-beta search with iterative deepening."""
    
    def __init__(self, evaluator=None):
        """
        Initialize alpha-beta search.
        
        Args:
            evaluator: Position evaluator function
        """
        self.evaluator = evaluator or evaluate_position
        self.nodes_searched = 0
        self.transposition_table: Dict[str, Dict] = {}
        self.killer_moves: Dict[int, List[chess.Move]] = {}
        self.history_table: Dict[chess.Move, int] = {}
    
    def _order_moves(self, board: chess.Board, moves: List[chess.Move]) -> List[chess.Move]:
        """Order moves for better alpha-beta performance."""
        def move_priority(move):
            priority = 0
            
            # Captures first
            if board.is_capture(move):
                captured_piece = board.piece_at(move.to_square)
                capturing_piece = board.piece_at(move.from_square)
                
                if captured_piece and capturing_piece:
                    # MVV-LVA: Most Valuable Victim - Least Valuable Attacker
                    victim_value = self._piece_value(captured_piece.piece_type)
                    attacker_value = self._piece_value(capturing_piece.piece_type)
                    priority += 1000 + victim_value - attacker_value
            
            # Promotions
            if move.promotion:
                priority += 900
            
            # Killer moves
            depth = len(board.move_stack)
            if depth in self.killer_moves and move in self.killer_moves[depth]:
                priority += 800
            
            # History heuristic
            priority += self.history_table.get(move, 0)
            
            return priority
        
        return sorted(moves, key=move_priority, reverse=True)
    
    def _piece_value(self, piece_type: int) -> int:
        """Get piece value for move ordering."""
        values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000
        }
        return values.get(piece_type, 0)
    
    def _quiescence_search(self, board: chess.Board, alpha: float, beta: float, 
                          depth: int, max_depth: int) -> float:
        """Quiescence search for tactical positions."""
        if depth >= max_depth:
            return self.evaluator(board)[0]
        
        # Stand pat
        stand_pat = self.evaluator(board)[0]
        if stand_pat >= beta:
            return beta
        if stand_pat > alpha:
            alpha = stand_pat
        
        # Search captures
        captures = [move for move in board.legal_moves if board.is_capture(move)]
        captures = self._order_moves(board, captures)
        
        for move in captures:
            board.push(move)
            score = -self._quiescence_search(board, -beta, -alpha, depth + 1, max_depth)
            board.pop()
            
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
        
        return alpha
    
    def _alpha_beta(self, board: chess.Board, depth: int, alpha: float, beta: float,
                    max_depth: int, start_time: float, max_time: float) -> float:
        """Alpha-beta search with time limit."""
        self.nodes_searched += 1
        
        # Time check
        if time.time() - start_time >= max_time:
            return self.evaluator(board)[0]
        
        # Terminal positions
        if board.is_checkmate():
            return -1000 if board.turn else 1000
        if board.is_stalemate() or board.is_insufficient_material():
            return 0.0
        
        if depth >= max_depth:
            return self._quiescence_search(board, alpha, beta, 0, 3)
        
        # Transposition table lookup
        fen = board.fen()
        if fen in self.transposition_table:
            entry = self.transposition_table[fen]
            if entry['depth'] >= depth:
                if entry['type'] == 'exact':
                    return entry['value']
                elif entry['type'] == 'lower':
                    alpha = max(alpha, entry['value'])
                elif entry['type'] == 'upper':
                    beta = min(beta, entry['value'])
                
                if alpha >= beta:
                    return entry['value']
        
        # Generate and order moves
        moves = list(board.legal_moves)
        if not moves:
            return self.evaluator(board)[0]
        
        moves = self._order_moves(board, moves)
        
        best_move = None
        best_value = float('-inf')
        original_alpha = alpha
        
        for move in moves:
            board.push(move)
            value = -self._alpha_beta(board, depth + 1, -beta, -alpha, 
                                    max_depth, start_time, max_time)
            board.pop()
            
            if value > best_value:
                best_value = value
                best_move = move
            
            if value >= beta:
                # Beta cutoff
                self._store_killer_move(move, len(board.move_stack))
                break
            
            if value > alpha:
                alpha = value
        
        # Store in transposition table
        tt_type = 'exact'
        if best_value <= original_alpha:
            tt_type = 'upper'
        elif best_value >= beta:
            tt_type = 'lower'
        
        self.transposition_table[fen] = {
            'value': best_value,
            'depth': depth,
            'type': tt_type,
            'move': best_move
        }
        
        return best_value
    
    def _store_killer_move(self, move: chess.Move, depth: int) -> None:
        """Store killer move for move ordering."""
        if depth not in self.killer_moves:
            self.killer_moves[depth] = []
        
        if move not in self.killer_moves[depth]:
            self.killer_moves[depth].insert(0, move)
            if len(self.killer_moves[depth]) > 2:
                self.killer_moves[depth].pop()
    
    def search(self, board: chess.Board, max_time: float, max_depth: int = 10) -> Dict[str, Any]:
        """
        Perform iterative deepening alpha-beta search.
        
        Args:
            board: Chess position
            max_time: Maximum time in seconds
            max_depth: Maximum search depth
            
        Returns:
            Search results
        """
        self.nodes_searched = 0
        start_time = time.time()
        
        best_move = None
        best_value = float('-inf')
        principal_variation = []
        
        # Iterative deepening
        for depth in range(1, max_depth + 1):
            if time.time() - start_time >= max_time:
                break
            
            try:
                value = self._alpha_beta(board, 0, float('-inf'), float('inf'),
                                      depth, start_time, max_time)
                
                if value > best_value:
                    best_value = value
                    # TODO: Extract principal variation from transposition table
                    principal_variation = []
                
            except Exception:
                break
        
        # Convert value to centipawns
        centipawns = value_to_centipawns(best_value)
        
        return {
            'bestmove': best_move,
            'pv': principal_variation,
            'value': best_value,
            'centipawns': centipawns,
            'nodes': self.nodes_searched,
            'depth': depth - 1
        }


def best_move_alphabeta(board: chess.Board, time_limit_s: float, 
                       max_depth: int = 10) -> chess.Move:
    """
    Find best move using alpha-beta search.
    
    Args:
        board: Chess position
        time_limit_s: Time limit in seconds
        max_depth: Maximum search depth
        
    Returns:
        Best move
    """
    search = AlphaBetaSearch()
    result = search.search(board, time_limit_s, max_depth)
    return result['bestmove']


def analyse_alphabeta(board: chess.Board, time_limit_s: float, 
                     max_depth: int = 10) -> Dict[str, Any]:
    """
    Analyze position using alpha-beta search.
    
    Args:
        board: Chess position
        time_limit_s: Time limit in seconds
        max_depth: Maximum search depth
        
    Returns:
        Analysis results
    """
    search = AlphaBetaSearch()
    return search.search(board, time_limit_s, max_depth)