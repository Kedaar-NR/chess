"""
UCI adapter for chess engine.

Implements UCI protocol for engine communication.
"""

import sys
import time
import chess
from typing import Optional, Dict, Any, List
import argparse

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from chessai.engine.search_mcts import best_move, analyse_simple
from chessai.engine.search_alphabeta import best_move_alphabeta, analyse_alphabeta
from chessai.models.policy_value import load_model
from chessai.utils.logging import setup_logging


class UCIEngine:
    """UCI chess engine implementation."""
    
    def __init__(self):
        """Initialize UCI engine."""
        self.board = chess.Board()
        self.model = None
        self.options = {
            'Hash': {'type': 'spin', 'default': 64, 'min': 1, 'max': 1024},
            'Threads': {'type': 'spin', 'default': 1, 'min': 1, 'max': 8},
            'TimeLimit': {'type': 'spin', 'default': 5, 'min': 1, 'max': 300},
            'Depth': {'type': 'spin', 'default': 10, 'min': 1, 'max': 50},
            'UseNeuralNetwork': {'type': 'check', 'default': True},
            'ModelPath': {'type': 'string', 'default': 'runs/best/model.h5'}
        }
        self.current_options = {key: opt['default'] for key, opt in self.options.items()}
        self.logger = setup_logging({'level': 'INFO', 'format': 'text'})
    
    def uci(self) -> None:
        """Respond to UCI command."""
        print("id name ChessAI")
        print("id author ChessAI Team")
        print("uciok")
    
    def isready(self) -> None:
        """Respond to isready command."""
        # Load model if not loaded
        if self.current_options['UseNeuralNetwork'] and self.model is None:
            model_path = self.current_options['ModelPath']
            try:
                self.model = load_model(model_path)
                self.logger.info(f"Loaded model from {model_path}")
            except Exception as e:
                self.logger.warning(f"Failed to load model: {e}")
                self.model = None
        
        print("readyok")
    
    def ucinewgame(self) -> None:
        """Start new game."""
        self.board = chess.Board()
    
    def position(self, fen: Optional[str] = None, moves: Optional[List[str]] = None) -> None:
        """Set position."""
        if fen:
            self.board = chess.Board(fen)
        else:
            self.board = chess.Board()
        
        if moves:
            for move_str in moves:
                move = chess.Move.from_uci(move_str)
                self.board.push(move)
    
    def go(self, **kwargs) -> None:
        """Start search."""
        # Parse go parameters
        time_limit = kwargs.get('movetime', self.current_options['TimeLimit'])
        depth = kwargs.get('depth', self.current_options['Depth'])
        nodes = kwargs.get('nodes', None)
        
        # Start search
        start_time = time.time()
        
        if self.current_options['UseNeuralNetwork'] and self.model is not None:
            # Use neural network with MCTS
            move = best_move(self.board, time_limit, nodes, 0.0, self.model)
        else:
            # Use alpha-beta fallback
            move = best_move_alphabeta(self.board, time_limit, depth)
        
        search_time = time.time() - start_time
        
        # Output best move
        if move:
            print(f"bestmove {move}")
        else:
            print("bestmove 0000")  # Null move
    
    def setoption(self, name: str, value: Any) -> None:
        """Set engine option."""
        if name in self.current_options:
            # Convert value to appropriate type
            option_type = self.options[name]['type']
            if option_type == 'spin':
                self.current_options[name] = int(value)
            elif option_type == 'check':
                self.current_options[name] = value.lower() in ['true', '1', 'yes']
            else:
                self.current_options[name] = value
    
    def quit(self) -> None:
        """Quit engine."""
        sys.exit(0)
    
    def run(self) -> None:
        """Run UCI engine."""
        while True:
            try:
                line = input().strip()
                if not line:
                    continue
                
                parts = line.split()
                command = parts[0].lower()
                
                if command == 'uci':
                    self.uci()
                elif command == 'isready':
                    self.isready()
                elif command == 'ucinewgame':
                    self.ucinewgame()
                elif command == 'position':
                    if len(parts) > 1:
                        if parts[1] == 'startpos':
                            self.position()
                            if len(parts) > 2 and parts[2] == 'moves':
                                moves = parts[3:] if len(parts) > 3 else []
                                self.position(moves=moves)
                        elif parts[1] == 'fen':
                            fen = ' '.join(parts[2:8]) if len(parts) >= 8 else None
                            moves = parts[9:] if len(parts) > 9 and parts[8] == 'moves' else []
                            self.position(fen, moves)
                elif command == 'go':
                    # Parse go parameters
                    go_params = {}
                    i = 1
                    while i < len(parts):
                        if parts[i] == 'movetime':
                            go_params['movetime'] = int(parts[i + 1])
                            i += 2
                        elif parts[i] == 'depth':
                            go_params['depth'] = int(parts[i + 1])
                            i += 2
                        elif parts[i] == 'nodes':
                            go_params['nodes'] = int(parts[i + 1])
                            i += 2
                        elif parts[i] == 'wtime':
                            go_params['wtime'] = int(parts[i + 1])
                            i += 2
                        elif parts[i] == 'btime':
                            go_params['btime'] = int(parts[i + 1])
                            i += 2
                        elif parts[i] == 'winc':
                            go_params['winc'] = int(parts[i + 1])
                            i += 2
                        elif parts[i] == 'binc':
                            go_params['binc'] = int(parts[i + 1])
                            i += 2
                        else:
                            i += 1
                    
                    self.go(**go_params)
                elif command == 'setoption':
                    if len(parts) >= 4 and parts[1] == 'name' and parts[3] == 'value':
                        name = parts[2]
                        value = ' '.join(parts[4:])
                        self.setoption(name, value)
                elif command == 'quit':
                    self.quit()
                else:
                    # Unknown command
                    pass
                    
            except EOFError:
                break
            except Exception as e:
                self.logger.error(f"UCI error: {e}")


def main():
    """Main UCI engine function."""
    parser = argparse.ArgumentParser(description='UCI Chess Engine')
    parser.add_argument('--model', type=str, default='runs/best/model.h5',
                       help='Path to neural network model')
    parser.add_argument('--log-level', type=str, default='INFO',
                       help='Logging level')
    
    args = parser.parse_args()
    
    # Create and run engine
    engine = UCIEngine()
    engine.current_options['ModelPath'] = args.model
    engine.run()


if __name__ == '__main__':
    main()
