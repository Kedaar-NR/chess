"""
Engine match script.

Plays matches between different chess engines.
"""

import os
import sys
import argparse
import chess
import chess.pgn
import time
import subprocess
from typing import List, Dict, Any, Optional
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from chessai.engine.search_mcts import best_move
from chessai.engine.search_alphabeta import best_move_alphabeta
from chessai.models.policy_value import load_model
from chessai.utils.logging import setup_logging


class EngineMatch:
    """Engine match between two chess engines."""
    
    def __init__(self, engine_a: str, engine_b: str, time_control: str = "5+0"):
        """
        Initialize engine match.
        
        Args:
            engine_a: First engine (path or name)
            engine_b: Second engine (path or name)
            time_control: Time control (e.g., "5+0", "60+1")
        """
        self.engine_a = engine_a
        self.engine_b = engine_b
        self.time_control = time_control
        self.games = []
    
    def play_match(self, num_games: int = 10) -> Dict[str, Any]:
        """
        Play a match between the engines.
        
        Args:
            num_games: Number of games to play
            
        Returns:
            Match results
        """
        results = {
            'engine_a': self.engine_a,
            'engine_b': self.engine_b,
            'time_control': self.time_control,
            'games': [],
            'scores': {'engine_a': 0, 'engine_b': 0, 'draws': 0}
        }
        
        for game_num in range(num_games):
            print(f"Playing game {game_num + 1}/{num_games}")
            
            # Alternate colors
            if game_num % 2 == 0:
                white_engine = self.engine_a
                black_engine = self.engine_b
            else:
                white_engine = self.engine_b
                black_engine = self.engine_a
            
            # Play game
            game_result = self._play_game(white_engine, black_engine, game_num + 1)
            results['games'].append(game_result)
            
            # Update scores
            if game_result['result'] == '1-0':
                if white_engine == self.engine_a:
                    results['scores']['engine_a'] += 1
                else:
                    results['scores']['engine_b'] += 1
            elif game_result['result'] == '0-1':
                if black_engine == self.engine_a:
                    results['scores']['engine_a'] += 1
                else:
                    results['scores']['engine_b'] += 1
            else:
                results['scores']['draws'] += 1
        
        return results
    
    def _play_game(self, white_engine: str, black_engine: str, 
                   game_number: int) -> Dict[str, Any]:
        """Play a single game."""
        board = chess.Board()
        moves = []
        start_time = time.time()
        
        while not board.is_game_over():
            # Get move from appropriate engine
            if board.turn == chess.WHITE:
                move = self._get_move(white_engine, board)
            else:
                move = self._get_move(black_engine, board)
            
            if move is None:
                break
            
            board.push(move)
            moves.append(str(move))
        
        game_time = time.time() - start_time
        
        # Determine result
        if board.is_checkmate():
            if board.turn == chess.WHITE:
                result = '0-1'
            else:
                result = '1-0'
        elif board.is_stalemate() or board.is_insufficient_material():
            result = '1/2-1/2'
        else:
            result = '*'
        
        return {
            'game_number': game_number,
            'white_engine': white_engine,
            'black_engine': black_engine,
            'result': result,
            'moves': moves,
            'move_count': len(moves),
            'game_time': game_time,
            'final_fen': board.fen()
        }
    
    def _get_move(self, engine: str, board: chess.Board) -> Optional[chess.Move]:
        """Get move from engine."""
        try:
            if engine == 'stockfish':
                return self._get_stockfish_move(board)
            elif engine.endswith('.h5') or engine.endswith('.hdf5'):
                return self._get_neural_move(engine, board)
            else:
                # Default to random move
                legal_moves = list(board.legal_moves)
                return legal_moves[0] if legal_moves else None
        except Exception as e:
            print(f"Error getting move from {engine}: {e}")
            return None
    
    def _get_stockfish_move(self, board: chess.Board) -> Optional[chess.Move]:
        """Get move from Stockfish engine."""
        try:
            # This is a placeholder - in practice you would use UCI protocol
            # For now, return a random legal move
            legal_moves = list(board.legal_moves)
            return legal_moves[0] if legal_moves else None
        except Exception:
            return None
    
    def _get_neural_move(self, model_path: str, board: chess.Board) -> Optional[chess.Move]:
        """Get move from neural network engine."""
        try:
            # Load model
            model = load_model(model_path)
            
            # Get best move using MCTS
            move = best_move(board, time_limit_s=5.0, network=model)
            return move
        except Exception:
            return None


def play_match(engine_a: str, engine_b: str, num_games: int = 10,
               time_control: str = "5+0", output_file: Optional[str] = None) -> None:
    """
    Play a match between two engines.
    
    Args:
        engine_a: First engine
        engine_b: Second engine
        num_games: Number of games to play
        time_control: Time control
        output_file: Output file for results
    """
    # Create match
    match = EngineMatch(engine_a, engine_b, time_control)
    
    # Play match
    print(f"Starting match: {engine_a} vs {engine_b}")
    print(f"Games: {num_games}, Time control: {time_control}")
    
    results = match.play_match(num_games)
    
    # Print results
    print("\nMatch Results:")
    print(f"Engine A ({engine_a}): {results['scores']['engine_a']} wins")
    print(f"Engine B ({engine_b}): {results['scores']['engine_b']} wins")
    print(f"Draws: {results['scores']['draws']}")
    
    # Save results
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {output_file}")
    
    # Save PGN
    if output_file:
        pgn_file = output_file.replace('.json', '.pgn')
        save_pgn(results, pgn_file)
        print(f"PGN saved to {pgn_file}")


def save_pgn(results: Dict[str, Any], pgn_file: str) -> None:
    """Save match results as PGN file."""
    with open(pgn_file, 'w') as f:
        for game in results['games']:
            # Create PGN game
            game_pgn = chess.pgn.Game()
            game_pgn.headers["White"] = game['white_engine']
            game_pgn.headers["Black"] = game['black_engine']
            game_pgn.headers["Result"] = game['result']
            game_pgn.headers["TimeControl"] = results['time_control']
            
            # Add moves
            board = chess.Board()
            for move_str in game['moves']:
                move = chess.Move.from_uci(move_str)
                board.push(move)
                game_pgn.add_main_variation(move)
            
            # Write game
            print(game_pgn, file=f)
            print(file=f)


def main():
    """Main match function."""
    parser = argparse.ArgumentParser(description='Play engine match')
    parser.add_argument('--engine_a', type=str, required=True,
                       help='First engine (path or name)')
    parser.add_argument('--engine_b', type=str, required=True,
                       help='Second engine (path or name)')
    parser.add_argument('--games', type=int, default=10,
                       help='Number of games to play')
    parser.add_argument('--tc', type=str, default='5+0',
                       help='Time control')
    parser.add_argument('--pgn', type=str, default='match.pgn',
                       help='Output PGN file')
    
    args = parser.parse_args()
    
    try:
        play_match(args.engine_a, args.engine_b, args.games, args.tc, args.pgn)
    except Exception as e:
        print(f"Match failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
