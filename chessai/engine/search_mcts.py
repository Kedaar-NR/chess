"""
Monte Carlo Tree Search implementation for chess.

Uses PUCT algorithm with neural network guidance.
"""

import chess
import time
import random
import math
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass
import numpy as np

from .move_index import move_index
from .evaluation import value_to_centipawns


@dataclass
class MCTSNode:
    """Node in the MCTS tree."""
    board: chess.Board
    parent: Optional['MCTSNode'] = None
    move: Optional[chess.Move] = None
    children: List['MCTSNode'] = None
    visits: int = 0
    value_sum: float = 0.0
    prior: float = 0.0
    is_expanded: bool = False
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
    
    @property
    def value(self) -> float:
        """Average value of this node."""
        if self.visits == 0:
            return 0.0
        return self.value_sum / self.visits
    
    def is_leaf(self) -> bool:
        """Check if this is a leaf node."""
        return not self.is_expanded or len(self.children) == 0


class MCTSSearch:
    """Monte Carlo Tree Search implementation."""
    
    def __init__(self, network, c_puct: float = 1.0, dirichlet_alpha: float = 0.3):
        """
        Initialize MCTS search.
        
        Args:
            network: Neural network for policy and value prediction
            c_puct: PUCT exploration constant
            dirichlet_alpha: Dirichlet noise parameter
        """
        self.network = network
        self.c_puct = c_puct
        self.dirichlet_alpha = dirichlet_alpha
        self.transposition_table: Dict[str, MCTSNode] = {}
    
    def _get_position_key(self, board: chess.Board) -> str:
        """Get unique key for position (simplified)."""
        return board.fen()
    
    def _add_dirichlet_noise(self, priors: np.ndarray, legal_mask: np.ndarray) -> np.ndarray:
        """Add Dirichlet noise to root node priors."""
        noise = np.random.dirichlet([self.dirichlet_alpha] * len(priors))
        return 0.75 * priors + 0.25 * noise
    
    def _select_child(self, node: MCTSNode) -> MCTSNode:
        """Select best child using PUCT formula."""
        if not node.children:
            return node
        
        best_child = None
        best_score = float('-inf')
        
        for child in node.children:
            if child.visits == 0:
                # Unvisited child - use prior
                score = child.prior
            else:
                # PUCT formula
                exploitation = child.value
                exploration = self.c_puct * child.prior * math.sqrt(node.visits) / (1 + child.visits)
                score = exploitation + exploration
            
            if score > best_score:
                best_score = score
                best_child = child
        
        return best_child or node.children[0]
    
    def _expand_node(self, node: MCTSNode) -> None:
        """Expand a leaf node."""
        if node.is_expanded or node.board.is_game_over():
            return
        
        # Get legal moves
        legal_moves = list(node.board.legal_moves)
        if not legal_moves:
            node.is_expanded = True
            return
        
        # Get policy and value from network
        try:
            policy, value = self.network.predict_policy_value(node.board)
        except Exception:
            # Fallback to random policy
            policy = np.random.random(move_index.action_space_size())
            value = 0.0
        
        # Create children for legal moves
        legal_mask = move_index.get_legal_move_mask(node.board)
        legal_policy = np.array(policy) * legal_mask
        
        # Normalize policy
        if legal_policy.sum() > 0:
            legal_policy = legal_policy / legal_policy.sum()
        else:
            legal_policy = legal_mask / legal_mask.sum()
        
        for move in legal_moves:
            move_id = move_index.to_id(move)
            if move_id >= 0:
                child_board = node.board.copy()
                child_board.push(move)
                
                child = MCTSNode(
                    board=child_board,
                    parent=node,
                    move=move,
                    prior=legal_policy[move_id]
                )
                node.children.append(child)
        
        node.is_expanded = True
    
    def _backup(self, node: MCTSNode, value: float) -> None:
        """Backup value through the tree."""
        current = node
        while current is not None:
            current.visits += 1
            current.value_sum += value
            value = -value  # Flip for opponent
            current = current.parent
    
    def _simulate(self, node: MCTSNode) -> float:
        """Simulate from a leaf node."""
        board = node.board.copy()
        
        # Simple random simulation
        moves_played = 0
        max_moves = 50
        
        while not board.is_game_over() and moves_played < max_moves:
            legal_moves = list(board.legal_moves)
            if not legal_moves:
                break
            
            move = random.choice(legal_moves)
            board.push(move)
            moves_played += 1
        
        # Evaluate final position
        if board.is_checkmate():
            return -1.0 if board.turn else 1.0
        elif board.is_stalemate() or board.is_insufficient_material():
            return 0.0
        else:
            # Use network evaluation
            try:
                _, value = self.network.predict_policy_value(board)
                return value
            except Exception:
                return 0.0
    
    def search(self, board: chess.Board, max_time: float, max_nodes: Optional[int] = None) -> MCTSNode:
        """
        Perform MCTS search.
        
        Args:
            board: Starting position
            max_time: Maximum time in seconds
            max_nodes: Maximum nodes to search
            
        Returns:
            Root node of search tree
        """
        root = MCTSNode(board=board.copy())
        self._expand_node(root)
        
        start_time = time.time()
        nodes_searched = 0
        
        while True:
            # Check stopping conditions
            elapsed = time.time() - start_time
            if elapsed >= max_time:
                break
            if max_nodes and nodes_searched >= max_nodes:
                break
            
            # Selection phase
            node = root
            path = [node]
            
            while not node.is_leaf():
                node = self._select_child(node)
                path.append(node)
            
            # Expansion phase
            if not node.is_expanded and not node.board.is_game_over():
                self._expand_node(node)
            
            # Simulation phase
            if node.is_leaf():
                if node.board.is_game_over():
                    # Terminal position
                    if node.board.is_checkmate():
                        value = -1.0 if node.board.turn else 1.0
                    else:
                        value = 0.0
                else:
                    value = self._simulate(node)
            else:
                # Use network evaluation
                try:
                    _, value = self.network.predict_policy_value(node.board)
                except Exception:
                    value = 0.0
            
            # Backup phase
            self._backup(node, value)
            nodes_searched += 1
        
        return root
    
    def get_best_move(self, root: MCTSNode, temperature: float = 0.0) -> chess.Move:
        """
        Get best move from root node.
        
        Args:
            root: Root node of search tree
            temperature: Temperature for move selection (0 for deterministic)
            
        Returns:
            Best move
        """
        if not root.children:
            return None
        
        if temperature == 0.0:
            # Deterministic selection - choose most visited
            best_child = max(root.children, key=lambda c: c.visits)
        else:
            # Probabilistic selection based on visit counts
            visits = np.array([c.visits for c in root.children])
            if visits.sum() == 0:
                return root.children[0].move
            
            # Apply temperature
            probs = visits ** (1.0 / temperature)
            probs = probs / probs.sum()
            
            # Sample move
            idx = np.random.choice(len(root.children), p=probs)
            best_child = root.children[idx]
        
        return best_child.move
    
    def get_principal_variation(self, root: MCTSNode, max_depth: int = 10) -> List[chess.Move]:
        """
        Get principal variation from root.
        
        Args:
            root: Root node of search tree
            max_depth: Maximum depth to search
            
        Returns:
            List of moves in principal variation
        """
        pv = []
        node = root
        
        for _ in range(max_depth):
            if not node.children:
                break
            
            best_child = max(node.children, key=lambda c: c.visits)
            pv.append(best_child.move)
            node = best_child
        
        return pv


def best_move(board: chess.Board, time_limit_s: float, max_nodes: Optional[int] = None, 
              temperature: float = 0.0, network=None) -> chess.Move:
    """
    Find best move using MCTS.
    
    Args:
        board: Chess position
        time_limit_s: Time limit in seconds
        max_nodes: Maximum nodes to search
        temperature: Temperature for move selection
        network: Neural network (optional)
        
    Returns:
        Best move
    """
    if network is None:
        # Use dummy network
        network = DummyNetwork()
    
    mcts = MCTSSearch(network)
    root = mcts.search(board, time_limit_s, max_nodes)
    return mcts.get_best_move(root, temperature)


def analyse_simple(board: chess.Board, time_limit_s: float, network=None) -> Dict[str, Any]:
    """
    Analyze position and return best move with score.
    
    Args:
        board: Chess position
        time_limit_s: Time limit in seconds
        network: Neural network (optional)
        
    Returns:
        Dictionary with analysis results
    """
    if network is None:
        network = DummyNetwork()
    
    mcts = MCTSSearch(network)
    root = mcts.search(board, time_limit_s)
    
    best_move = mcts.get_best_move(root, 0.0)
    pv = mcts.get_principal_variation(root)
    
    # Calculate score
    if root.children:
        best_child = max(root.children, key=lambda c: c.visits)
        value = best_child.value
        centipawns = value_to_centipawns(value)
    else:
        value = 0.0
        centipawns = 0
    
    return {
        'bestmove': best_move,
        'pv': pv,
        'value': value,
        'centipawns': centipawns,
        'nodes': root.visits
    }


class DummyNetwork:
    """Dummy network for testing."""
    
    def predict_policy_value(self, board: chess.Board) -> Tuple[np.ndarray, float]:
        """Return random policy and value."""
        policy = np.random.random(move_index.action_space_size())
        value = np.random.uniform(-1, 1)
        return policy, value