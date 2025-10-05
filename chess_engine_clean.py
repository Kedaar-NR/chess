#!/usr/bin/env python3
"""
Chess Engine - Clean Version

A complete chess application with prediction, move making, and professional interface.
"""

import sys
import os
import chess
import time
import random
from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass

# Add chessai to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'chessai'))

from chessai.engine.search_alphabeta import best_move_alphabeta, analyse_alphabeta
from chessai.engine.evaluation import evaluate_position, value_to_centipawns


@dataclass
class MovePrediction:
    """Move prediction with confidence."""
    move: chess.Move
    confidence: float
    score: float
    centipawns: int
    nodes: int
    time_ms: int
    pv: List[str] = None


class ChessEngine:
    """Advanced chess engine with prediction capabilities."""
    
    def __init__(self, name: str = "ChessAI", time_limit: float = 2.0):
        """Initialize chess engine."""
        self.name = name
        self.time_limit = time_limit
        self.total_time = 0.0
        self.total_nodes = 0
        self.moves_played = 0
    
    def predict_move(self, board: chess.Board) -> MovePrediction:
        """Predict the best move with full analysis."""
        if board.is_game_over():
            return None
        
        start_time = time.time()
        
        try:
            # Get move analysis
            result = analyse_alphabeta(board, self.time_limit)
            
            move_time = time.time() - start_time
            self.total_time += move_time
            self.total_nodes += result.get('nodes', 0)
            self.moves_played += 1
            
            # Calculate confidence based on score and time
            score = result.get('value', 0)
            confidence = min(1.0, abs(score) + 0.5)  # Higher confidence for stronger moves
            
            return MovePrediction(
                move=result.get('bestmove'),
                confidence=confidence,
                score=score,
                centipawns=result.get('centipawns', 0),
                nodes=result.get('nodes', 0),
                time_ms=int(move_time * 1000),
                pv=result.get('pv', [])
            )
            
        except Exception as e:
            print(f"Prediction error: {e}")
            # Fallback to random move
            legal_moves = list(board.legal_moves)
            if legal_moves:
                move = random.choice(legal_moves)
                return MovePrediction(
                    move=move,
                    confidence=0.1,
                    score=0.0,
                    centipawns=0,
                    nodes=0,
                    time_ms=0,
                    pv=[]
                )
            return None
    
    def make_move(self, board: chess.Board) -> bool:
        """Make the predicted move on the board."""
        prediction = self.predict_move(board)
        if prediction and prediction.move:
            board.push(prediction.move)
            return True
        return False


class ChessGame:
    """Chess game with professional interface."""
    
    def __init__(self):
        """Initialize chess game."""
        self.board = chess.Board()
        self.move_history = []
        self.engine_white = ChessEngine("White Engine", 2.0)
        self.engine_black = ChessEngine("Black Engine", 2.0)
        self.current_engine = None
        self.game_start_time = time.time()
    
    def create_visual_board(self, last_move: Optional[chess.Move] = None) -> str:
        """Create professional visual board."""
        lines = []
        lines.append("┌" + "─" * 33 + "┐")
        
        for i in range(8):
            line = f"{8-i}│"
            for j in range(8):
                square = chess.square(j, 7-i)
                piece = self.board.piece_at(square)
                
                # Determine piece symbol
                if piece:
                    symbol = piece.symbol()
                    if piece.color == chess.WHITE:
                        symbol = symbol.upper()
                    else:
                        symbol = symbol.lower()
                else:
                    symbol = " "
                
                # Determine square color
                is_light = (i + j) % 2 == 0
                is_last_move = last_move and (square == last_move.from_square or square == last_move.to_square)
                
                if is_last_move:
                    bg = "■"  # Highlight for last move
                elif is_light:
                    bg = " "  # Light square
                else:
                    bg = "·"  # Dark square
                
                line += f"{bg}{symbol} "
            
            line += f"│{8-i}"
            lines.append(line)
        
        lines.append("└" + "─" * 33 + "┘")
        lines.append("  a  b  c  d  e  f  g  h")
        
        return "\n".join(lines)
    
    def print_game_status(self):
        """Print current game status."""
        print(f"\n{'='*60}")
        print(f"CHESS GAME - MOVE {len(self.move_history) + 1}")
        print(f"{'='*60}")
        
        # Game status
        if self.board.is_checkmate():
            winner = "Black" if self.board.turn == chess.WHITE else "White"
            print(f"CHECKMATE! {winner} wins!")
        elif self.board.is_stalemate():
            print("STALEMATE! Game is a draw.")
        elif self.board.is_check():
            print(f"CHECK! {'White' if self.board.turn == chess.WHITE else 'Black'} king is in check.")
        else:
            print(f"Turn: {'White' if self.board.turn == chess.WHITE else 'Black'}")
        
        # Position evaluation
        value, centipawns = evaluate_position(self.board)
        print(f"Position: {value:.3f} ({centipawns:+d} cp)")
        
        if centipawns > 100:
            print("White has a significant advantage")
        elif centipawns < -100:
            print("Black has a significant advantage")
        else:
            print("Position is roughly equal")
    
    def show_move_predictions(self, engine: ChessEngine) -> MovePrediction:
        """Show move predictions."""
        print(f"\n{engine.name} is analyzing...")
        
        prediction = engine.predict_move(self.board)
        if prediction:
            print(f"Best move: {prediction.move}")
            print(f"Score: {prediction.score:.3f} ({prediction.centipawns:+d} cp)")
            print(f"Confidence: {prediction.confidence:.1%}")
            print(f"Nodes: {prediction.nodes:,}")
            print(f"Time: {prediction.time_ms}ms")
            
            if prediction.pv:
                print(f"Principal variation: {' '.join(prediction.pv)}")
        
        return prediction
    
    def play_engine_vs_engine(self, max_moves: int = 50):
        """Play engine vs engine game."""
        print("ENGINE vs ENGINE GAME")
        print("="*60)
        
        self.print_game_status()
        print(self.create_visual_board())
        
        while not self.board.is_game_over() and len(self.move_history) < max_moves:
            current_engine = self.engine_white if self.board.turn == chess.WHITE else self.engine_black
            player_name = f"{current_engine.name} (White)" if self.board.turn == chess.WHITE else f"{current_engine.name} (Black)"
            
            print(f"\n--- {player_name} to move ---")
            
            # Show predictions
            prediction = self.show_move_predictions(current_engine)
            
            if prediction and prediction.move:
                # Make the move
                self.board.push(prediction.move)
                self.move_history.append(str(prediction.move))
                
                print(f"{current_engine.name} plays: {prediction.move}")
                
                # Show updated board
                self.print_game_status()
                print(self.create_visual_board(prediction.move))
                
                # Brief pause
                time.sleep(1)
            else:
                print(f"{current_engine.name} has no legal moves!")
                break
        
        # Game over
        self.print_final_results()
    
    def play_human_vs_engine(self):
        """Play human vs engine game."""
        print("HUMAN vs ENGINE GAME")
        print("="*60)
        print("You are White, Engine is Black")
        print("Enter moves in UCI format (e.g., 'e2e4')")
        print("Commands: 'analyze', 'undo', 'quit'")
        
        self.print_game_status()
        print(self.create_visual_board())
        
        while not self.board.is_game_over():
            if self.board.turn == chess.WHITE:
                # Human move
                while True:
                    user_input = input(f"\nYour move: ").strip()
                    
                    if user_input.lower() == 'quit':
                        return
                    elif user_input.lower() == 'analyze':
                        prediction = self.show_move_predictions(self.engine_white)
                        continue
                    elif user_input.lower() == 'undo':
                        if self.move_history:
                            self.board.pop()
                            self.move_history.pop()
                            print("Move undone.")
                            self.print_game_status()
                            print(self.create_visual_board())
                            break
                        else:
                            print("No moves to undo.")
                            continue
                    
                    try:
                        move = chess.Move.from_uci(user_input)
                        if move in self.board.legal_moves:
                            self.board.push(move)
                            self.move_history.append(str(move))
                            print(f"You play: {move}")
                            break
                        else:
                            print("Illegal move!")
                    except ValueError:
                        print("Invalid format! Use UCI notation (e.g., 'e2e4')")
            else:
                # Engine move
                prediction = self.show_move_predictions(self.engine_black)
                
                if prediction and prediction.move:
                    self.board.push(prediction.move)
                    self.move_history.append(str(prediction.move))
                    print(f"Engine plays: {prediction.move}")
                else:
                    print("Engine has no legal moves!")
                    break
            
            # Show updated board
            self.print_game_status()
            print(self.create_visual_board())
        
        # Game over
        self.print_final_results()
    
    def print_final_results(self):
        """Print final game results."""
        game_time = time.time() - self.game_start_time
        
        print(f"\nGAME OVER!")
        print(f"Result: {self.board.result()}")
        print(f"Total moves: {len(self.move_history)}")
        print(f"Game time: {game_time:.1f} seconds")
        print(f"Final position: {self.board.fen()}")
        
        # Engine statistics
        print(f"\nENGINE STATISTICS")
        print(f"White Engine ({self.engine_white.name}):")
        print(f"  Moves: {self.engine_white.moves_played}")
        print(f"  Total time: {self.engine_white.total_time:.2f}s")
        print(f"  Average time: {self.engine_white.total_time/max(1, self.engine_white.moves_played):.2f}s per move")
        print(f"  Total nodes: {self.engine_white.total_nodes:,}")
        
        print(f"\nBlack Engine ({self.engine_black.name}):")
        print(f"  Moves: {self.engine_black.moves_played}")
        print(f"  Total time: {self.engine_black.total_time:.2f}s")
        print(f"  Average time: {self.engine_black.total_time/max(1, self.engine_black.moves_played):.2f}s per move")
        print(f"  Total nodes: {self.engine_black.total_nodes:,}")


def main():
    """Main chess application."""
    print("Chess Engine - Professional Interface")
    print("="*60)
    print("Advanced chess engine with move prediction and analysis")
    print("="*60)
    
    while True:
        print("\nChoose game mode:")
        print("1. Engine vs Engine (Bot vs Bot)")
        print("2. Human vs Engine")
        print("3. Position Analysis")
        print("4. Exit")
        
        try:
            choice = input("\nEnter choice (1-4): ").strip()
            
            if choice == '1':
                game = ChessGame()
                max_moves = int(input("Maximum moves (default 50): ") or "50")
                game.play_engine_vs_engine(max_moves)
                
            elif choice == '2':
                game = ChessGame()
                game.play_human_vs_engine()
                
            elif choice == '3':
                analyze_positions()
                
            elif choice == '4':
                print("Goodbye!")
                break
                
            else:
                print("Invalid choice! Please enter 1-4.")
                
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()


def analyze_positions():
    """Analyze famous chess positions."""
    print("\nPOSITION ANALYSIS")
    print("="*60)
    
    positions = [
        ("Starting Position", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"),
        ("After e4 e5", "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2"),
        ("Sicilian Defense", "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2"),
        ("King's Indian", "rnbqkb1r/pppppppp/5n2/8/3PP3/8/PPP2PPP/RNBQKBNR b KQkq d3 0 2"),
    ]
    
    engine = ChessEngine("Analysis Engine", 3.0)
    
    for name, fen in positions:
        print(f"\n--- {name} ---")
        board = chess.Board(fen)
        
        # Show board
        game = ChessGame()
        game.board = board
        print(game.create_visual_board())
        
        # Analyze position
        prediction = engine.predict_move(board)
        if prediction:
            print(f"Engine analysis:")
            print(f"   Best move: {prediction.move}")
            print(f"   Score: {prediction.score:.3f} ({prediction.centipawns:+d} cp)")
            print(f"   Confidence: {prediction.confidence:.1%}")
            print(f"   Nodes: {prediction.nodes:,}")
            print(f"   Time: {prediction.time_ms}ms")
            
            if prediction.pv:
                print(f"   Principal variation: {' '.join(prediction.pv)}")
        
        time.sleep(1)


if __name__ == "__main__":
    main()
