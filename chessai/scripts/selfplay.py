"""
Self-play script for generating training data.

Plays games between different versions of the engine.
"""

import os
import sys
import argparse
import chess
import chess.pgn
import time
import random
from typing import List, Dict, Any, Optional
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from chessai.engine.search_mcts import MCTSSearch
from chessai.models.policy_value import load_model, PolicyValueNetwork
from chessai.utils.config import load_config
from chessai.utils.logging import setup_logging
from chessai.utils.sampling import add_dirichlet_noise


class SelfPlayGame:
    """Self-play game between two engine versions."""
    
    def __init__(self, engine_a: PolicyValueNetwork, engine_b: PolicyValueNetwork,
                 time_limit: float = 5.0, temperature: float = 1.0):
        """
        Initialize self-play game.
        
        Args:
            engine_a: First engine
            engine_b: Second engine
            time_limit: Time limit per move
            temperature: Temperature for move selection
        """
        self.engine_a = engine_a
        self.engine_b = engine_b
        self.time_limit = time_limit
        self.temperature = temperature
        self.moves = []
        self.positions = []
    
    def play_game(self) -> Dict[str, Any]:
        """
        Play a complete game.
        
        Returns:
            Game result dictionary
        """
        board = chess.Board()
        move_count = 0
        max_moves = 200
        
        while not board.is_game_over() and move_count < max_moves:
            # Determine which engine to use
            if board.turn == chess.WHITE:
                engine = self.engine_a
            else:
                engine = self.engine_b
            
            # Get move from engine
            move = self._get_move(engine, board)
            if move is None:
                break
            
            # Record position and move
            self.positions.append({
                'fen': board.fen(),
                'move': str(move),
                'move_number': move_count + 1,
                'side': 'white' if board.turn == chess.WHITE else 'black'
            })
            
            # Make move
            board.push(move)
            self.moves.append(str(move))
            move_count += 1
        
        # Determine result
        if board.is_checkmate():
            if board.turn == chess.WHITE:
                result = '0-1'  # Black wins
            else:
                result = '1-0'  # White wins
        elif board.is_stalemate() or board.is_insufficient_material():
            result = '1/2-1/2'  # Draw
        else:
            result = '*'  # Unknown
        
        return {
            'result': result,
            'moves': self.moves,
            'positions': self.positions,
            'move_count': move_count,
            'final_fen': board.fen()
        }
    
    def _get_move(self, engine: PolicyValueNetwork, board: chess.Board) -> Optional[chess.Move]:
        """Get move from engine."""
        try:
            # Create MCTS search
            mcts = MCTSSearch(engine)
            
            # Search for best move
            root = mcts.search(board, self.time_limit)
            move = mcts.get_best_move(root, self.temperature)
            
            return move
        except Exception as e:
            print(f"Error getting move: {e}")
            # Fallback to random move
            legal_moves = list(board.legal_moves)
            return random.choice(legal_moves) if legal_moves else None


def play_selfplay_games(config_path: str, output_dir: str, 
                       num_games: int = 100) -> None:
    """
    Play self-play games and save results.
    
    Args:
        config_path: Path to configuration file
        output_dir: Output directory for games
        num_games: Number of games to play
    """
    # Load configuration
    config = load_config(config_path)
    
    # Setup logging
    logger = setup_logging(config.get('logging', {}))
    
    # Load models
    model_path = config.get('model_path', 'runs/best/model.h5')
    if os.path.exists(model_path):
        engine = load_model(model_path)
    else:
        logger.warning(f"Model not found at {model_path}, using dummy model")
        engine = PolicyValueNetwork(None)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Play games
    logger.info(f"Starting self-play with {num_games} games")
    
    for game_num in range(num_games):
        logger.info(f"Playing game {game_num + 1}/{num_games}")
        
        # Create self-play game
        game = SelfPlayGame(
            engine_a=engine,
            engine_b=engine,
            time_limit=config.get('time_limit', 5.0),
            temperature=config.get('temperature', 1.0)
        )
        
        # Play game
        start_time = time.time()
        result = game.play_game()
        game_time = time.time() - start_time
        
        # Save game
        game_file = os.path.join(output_dir, f'game_{game_num + 1:04d}.json')
        with open(game_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        logger.info(f"Game {game_num + 1} completed: {result['result']} "
                   f"({result['move_count']} moves, {game_time:.2f}s)")
    
    logger.info(f"Self-play completed. Games saved to {output_dir}")


def main():
    """Main self-play function."""
    parser = argparse.ArgumentParser(description='Play self-play games')
    parser.add_argument('--config', type=str, required=True,
                       help='Path to configuration file')
    parser.add_argument('--output', type=str, required=True,
                       help='Output directory for games')
    parser.add_argument('--games', type=int, default=100,
                       help='Number of games to play')
    
    args = parser.parse_args()
    
    try:
        play_selfplay_games(args.config, args.output, args.games)
    except Exception as e:
        print(f"Self-play failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
