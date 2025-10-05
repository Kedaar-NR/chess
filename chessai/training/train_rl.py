"""
Reinforcement learning training script.

Self-play training using MCTS and experience replay.
"""

import os
import sys
import argparse
import yaml
import tensorflow as tf
from tensorflow import keras
import numpy as np
from typing import Dict, Any, List, Tuple
import random
import chess

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from chessai.models.policy_value import PolicyValueNetwork, load_model
from chessai.engine.search_mcts import MCTSSearch
from chessai.training.dataset import make_dataset
from chessai.training.losses import ChessLoss
from chessai.utils.config import load_config
from chessai.utils.logging import setup_logging
from chessai.utils.elo import update_ratings, get_rating
from chessai.utils.sampling import add_dirichlet_noise


class SelfPlayBuffer:
    """Buffer for self-play experience."""
    
    def __init__(self, max_size: int = 100000):
        """
        Initialize self-play buffer.
        
        Args:
            max_size: Maximum buffer size
        """
        self.max_size = max_size
        self.buffer = []
        self.current_game = []
    
    def add_position(self, board: chess.Board, policy: np.ndarray, 
                    value: float, legal_mask: np.ndarray) -> None:
        """Add a position to the current game."""
        self.current_game.append({
            'board': board.copy(),
            'policy': policy,
            'value': value,
            'legal_mask': legal_mask
        })
    
    def finish_game(self, result: float) -> None:
        """Finish the current game and add to buffer."""
        # Update values based on game result
        for i, position in enumerate(self.current_game):
            # Use game result for terminal positions
            if i == len(self.current_game) - 1:
                position['value'] = result
            else:
                # Use MCTS value for non-terminal positions
                pass
        
        # Add to buffer
        self.buffer.extend(self.current_game)
        
        # Trim buffer if too large
        if len(self.buffer) > self.max_size:
            self.buffer = self.buffer[-self.max_size:]
        
        # Clear current game
        self.current_game = []
    
    def sample_batch(self, batch_size: int) -> List[Dict[str, Any]]:
        """Sample a batch from the buffer."""
        if len(self.buffer) < batch_size:
            return self.buffer
        return random.sample(self.buffer, batch_size)
    
    def size(self) -> int:
        """Get buffer size."""
        return len(self.buffer)


def play_self_game(network: PolicyValueNetwork, mcts: MCTSSearch, 
                   temperature: float = 1.0) -> List[Dict[str, Any]]:
    """
    Play a self-play game.
    
    Args:
        network: Policy-value network
        mcts: MCTS search
        temperature: Temperature for move selection
        
    Returns:
        List of game positions
    """
    board = chess.Board()
    positions = []
    
    while not board.is_game_over():
        # Get MCTS search result
        root = mcts.search(board, time_limit_s=1.0, max_nodes=1000)
        
        # Get policy from MCTS
        if root.children:
            policy = np.zeros(4096)  # Default move space size
            total_visits = sum(child.visits for child in root.children)
            
            for child in root.children:
                move_id = 0  # TODO: Get move ID from move
                if total_visits > 0:
                    policy[move_id] = child.visits / total_visits
        
        # Get legal move mask
        legal_mask = np.zeros(4096, dtype=bool)
        for move in board.legal_moves:
            move_id = 0  # TODO: Get move ID from move
            legal_mask[move_id] = True
        
        # Add position to game
        positions.append({
            'board': board.copy(),
            'policy': policy,
            'legal_mask': legal_mask
        })
        
        # Select move
        if root.children:
            best_child = max(root.children, key=lambda c: c.visits)
            move = best_child.move
        else:
            # Random move if no children
            move = random.choice(list(board.legal_moves))
        
        board.push(move)
    
    # Determine game result
    if board.is_checkmate():
        result = 1.0 if board.turn else -1.0  # Previous player won
    else:
        result = 0.0  # Draw
    
    # Update values based on result
    for i, position in enumerate(positions):
        # Flip result for black positions
        if i % 2 == 1:
            position['value'] = -result
        else:
            position['value'] = result
    
    return positions


def train_rl(config_path: str, model_path: Optional[str] = None) -> None:
    """
    Train the model using reinforcement learning.
    
    Args:
        config_path: Path to configuration file
        model_path: Path to pretrained model
    """
    # Load configuration
    config = load_config(config_path)
    
    # Setup logging
    logger = setup_logging(config.get('logging', {}))
    
    # Load or create model
    if model_path and os.path.exists(model_path):
        logger.info(f"Loading model from {model_path}")
        network = load_model(model_path)
    else:
        logger.info("Creating new model")
        model = build_model(
            board_channels=config['model']['board_channels'],
            move_space=config['model']['move_space'],
            width=config['model']['width'],
            depth=config['model']['depth']
        )
        network = PolicyValueNetwork(model)
    
    # Create MCTS search
    mcts = MCTSSearch(network)
    
    # Create self-play buffer
    buffer = SelfPlayBuffer(max_size=config['rl']['buffer_size'])
    
    # Training loop
    for epoch in range(config['rl']['epochs']):
        logger.info(f"Starting epoch {epoch + 1}")
        
        # Self-play phase
        logger.info("Playing self-play games...")
        for game in range(config['rl']['games_per_epoch']):
            # Play self-play game
            positions = play_self_game(network, mcts, temperature=1.0)
            
            # Add to buffer
            for position in positions:
                buffer.add_position(
                    position['board'],
                    position['policy'],
                    position['value'],
                    position['legal_mask']
                )
            buffer.finish_game(positions[-1]['value'])
        
        # Training phase
        if buffer.size() >= config['rl']['min_buffer_size']:
            logger.info("Training on self-play data...")
            
            # Sample training batch
            batch = buffer.sample_batch(config['rl']['batch_size'])
            
            # Prepare training data
            boards = [pos['board'] for pos in batch]
            policies = np.array([pos['policy'] for pos in batch])
            values = np.array([pos['value'] for pos in batch])
            legal_masks = np.array([pos['legal_mask'] for pos in batch])
            
            # Train model
            # TODO: Implement actual training step
            logger.info(f"Training on {len(batch)} positions")
        
        # Save model periodically
        if (epoch + 1) % config['rl']['save_frequency'] == 0:
            model_path = os.path.join(config['rl']['output_dir'], f'model_epoch_{epoch + 1}.h5')
            network.model.save(model_path)
            logger.info(f"Saved model to {model_path}")
    
    logger.info("RL training completed!")


def main():
    """Main RL training function."""
    parser = argparse.ArgumentParser(description='Train chess model with RL')
    parser.add_argument('--config', type=str, required=True,
                       help='Path to configuration file')
    parser.add_argument('--model', type=str, default=None,
                       help='Path to pretrained model')
    
    args = parser.parse_args()
    
    try:
        train_rl(args.config, args.model)
    except Exception as e:
        print(f"RL training failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()