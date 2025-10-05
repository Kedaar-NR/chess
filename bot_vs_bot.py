#!/usr/bin/env python3
"""
Bot vs Bot Chess Game

Two chess engines play against each other with optimal moves and full visualization.
"""

import sys
import os
import chess
import time
import random
from typing import List, Optional, Tuple
from dataclasses import dataclass

# Add chessai to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'chessai'))

from chessai.engine.search_alphabeta import best_move_alphabeta, analyse_alphabeta
from chessai.engine.search_mcts import best_move, analyse_simple
from chessai.engine.evaluation import evaluate_position, value_to_centipawns
from chessai.models.policy_value import PolicyValueNetwork


@dataclass
class GameStats:
    """Game statistics."""
    moves: List[str] = None
    times: List[float] = None
    evaluations: List[float] = None
    nodes_searched: List[int] = None
    
    def __post_init__(self):
        if self.moves is None:
            self.moves = []
        if self.times is None:
            self.times = []
        if self.evaluations is None:
            self.evaluations = []
        if self.nodes_searched is None:
            self.nodes_searched = []


class ChessBot:
    """Chess bot with different playing styles."""
    
    def __init__(self, name: str, engine_type: str = "alphabeta", time_limit: float = 2.0):
        """
        Initialize chess bot.
        
        Args:
            name: Bot name
            engine_type: "alphabeta", "mcts", or "random"
            time_limit: Time limit per move in seconds
        """
        self.name = name
        self.engine_type = engine_type
        self.time_limit = time_limit
        self.total_time = 0.0
        self.total_nodes = 0
        self.moves_played = 0
        
        # Load neural network if available
        self.network = None
        if engine_type == "mcts":
            try:
                model_path = "runs/best/model.h5"
                if os.path.exists(model_path):
                    self.network = PolicyValueNetwork(None)  # Dummy for now
            except:
                self.network = None
    
    def get_move(self, board: chess.Board) -> Optional[chess.Move]:
        """Get best move for the current position."""
        if board.is_game_over():
            return None
        
        start_time = time.time()
        
        try:
            if self.engine_type == "alphabeta":
                move = best_move_alphabeta(board, self.time_limit)
            elif self.engine_type == "mcts":
                move = best_move(board, self.time_limit, network=self.network)
            elif self.engine_type == "random":
                legal_moves = list(board.legal_moves)
                move = random.choice(legal_moves) if legal_moves else None
            else:
                move = None
            
            move_time = time.time() - start_time
            self.total_time += move_time
            self.moves_played += 1
            
            return move
            
        except Exception as e:
            print(f"Error in {self.name}: {e}")
            # Fallback to random move
            legal_moves = list(board.legal_moves)
            return random.choice(legal_moves) if legal_moves else None
    
    def analyze_position(self, board: chess.Board) -> dict:
        """Analyze current position."""
        try:
            if self.engine_type == "alphabeta":
                result = analyse_alphabeta(board, self.time_limit)
            elif self.engine_type == "mcts":
                result = analyse_simple(board, self.time_limit, network=self.network)
            else:
                value, centipawns = evaluate_position(board)
                result = {
                    'value': value,
                    'centipawns': centipawns,
                    'nodes': 0,
                    'bestmove': None
                }
            
            if 'nodes' in result:
                self.total_nodes += result['nodes']
            
            return result
        except:
            value, centipawns = evaluate_position(board)
            return {
                'value': value,
                'centipawns': centipawns,
                'nodes': 0,
                'bestmove': None
            }


def create_visual_board(board: chess.Board, last_move: Optional[chess.Move] = None, 
                       highlight_squares: List[int] = None) -> str:
    """Create a visual ASCII chess board."""
    if highlight_squares is None:
        highlight_squares = []
    
    lines = []
    lines.append("   ┌" + "─" * 31 + "┐")
    
    for i in range(8):
        line = f"{8-i} │"
        for j in range(8):
            square = chess.square(j, 7-i)
            piece = board.piece_at(square)
            
            # Determine piece symbol
            if piece:
                symbol = piece.symbol()
                if piece.color == chess.WHITE:
                    symbol = symbol.upper()
                else:
                    symbol = symbol.lower()
            else:
                symbol = " "
            
            # Determine square color and highlighting
            is_light = (i + j) % 2 == 0
            is_highlighted = square in highlight_squares
            is_last_move = last_move and (square == last_move.from_square or square == last_move.to_square)
            
            if is_last_move:
                bg = "🟨"  # Yellow for last move
            elif is_highlighted:
                bg = "🟦"  # Blue for highlighted
            elif is_light:
                bg = "⬜"  # Light square
            else:
                bg = "⬛"  # Dark square
            
            line += f"{bg}{symbol} "
        
        line += f"│ {8-i}"
        lines.append(line)
    
    lines.append("   └" + "─" * 31 + "┘")
    lines.append("     a  b  c  d  e  f  g  h")
    
    return "\n".join(lines)


def print_game_status(board: chess.Board, move_number: int, current_player: str):
    """Print current game status."""
    print(f"\n{'='*60}")
    print(f"MOVE {move_number} - {current_player} TO PLAY")
    print(f"{'='*60}")
    
    # Game status
    if board.is_checkmate():
        winner = "Black" if board.turn == chess.WHITE else "White"
        print(f" CHECKMATE! {winner} wins!")
    elif board.is_stalemate():
        print(" STALEMATE! Game is a draw.")
    elif board.is_check():
        print(f"  CHECK! {'White' if board.turn == chess.WHITE else 'Black'} king is in check.")
    else:
        print(f"  Turn: {'White' if board.turn == chess.WHITE else 'Black'}")
    
    # Position evaluation
    value, centipawns = evaluate_position(board)
    print(f" Position: {value:.3f} ({centipawns:+d} cp)")
    
    if centipawns > 100:
        print(" White has a significant advantage")
    elif centipawns < -100:
        print(" Black has a significant advantage")
    else:
        print(" Position is roughly equal")


def play_bot_vs_bot(bot1: ChessBot, bot2: ChessBot, max_moves: int = 100, 
                   show_analysis: bool = True) -> Tuple[chess.Board, GameStats]:
    """Play a game between two bots."""
    print(f"\n {bot1.name} vs {bot2.name}")
    print(f"Engine types: {bot1.engine_type} vs {bot2.engine_type}")
    print(f"Time limit: {bot1.time_limit}s per move")
    print("="*60)
    
    board = chess.Board()
    stats = GameStats()
    move_number = 0
    
    # Show initial position
    print_game_status(board, 0, "Starting position")
    print(create_visual_board(board))
    
    while not board.is_game_over() and move_number < max_moves:
        move_number += 1
        current_bot = bot1 if board.turn == chess.WHITE else bot2
        player_name = f"{current_bot.name} (White)" if board.turn == chess.WHITE else f"{current_bot.name} (Black)"
        
        print_game_status(board, move_number, player_name)
        print(create_visual_board(board))
        
        # Get move from current bot
        print(f"\n {current_bot.name} is thinking...")
        start_time = time.time()
        
        move = current_bot.get_move(board)
        move_time = time.time() - start_time
        
        if move is None:
            print(f" {current_bot.name} has no legal moves!")
            break
        
        # Make the move
        board.push(move)
        stats.moves.append(str(move))
        stats.times.append(move_time)
        
        print(f" {current_bot.name} plays: {move} (took {move_time:.2f}s)")
        
        # Show analysis if requested
        if show_analysis:
            analysis = current_bot.analyze_position(board)
            print(f" Analysis: {analysis.get('value', 0):.3f} ({analysis.get('centipawns', 0):+d} cp)")
            if 'nodes' in analysis:
                print(f" Nodes searched: {analysis['nodes']}")
        
        # Brief pause for readability
        time.sleep(0.5)
    
    # Game over
    print_game_status(board, move_number, "Game Over")
    print(create_visual_board(board))
    
    # Final statistics
    print(f"\n GAME STATISTICS")
    print(f"{'='*60}")
    print(f"Total moves: {len(stats.moves)}")
    print(f"Result: {board.result()}")
    print(f"Final position: {board.fen()}")
    
    print(f"\n{bot1.name} stats:")
    print(f"  Total time: {bot1.total_time:.2f}s")
    print(f"  Average time: {bot1.total_time/max(1, bot1.moves_played):.2f}s per move")
    print(f"  Total nodes: {bot1.total_nodes}")
    
    print(f"\n{bot2.name} stats:")
    print(f"  Total time: {bot2.total_time:.2f}s")
    print(f"  Average time: {bot2.total_time/max(1, bot2.moves_played):.2f}s per move")
    print(f"  Total nodes: {bot2.total_nodes}")
    
    return board, stats


def main():
    """Main bot vs bot game."""
    print(" ChessAI Bot vs Bot Game")
    print("="*60)
    
    # Create different types of bots
    bots = {
        "1": ChessBot("AlphaBot", "alphabeta", 1.0),
        "2": ChessBot("MCTSBot", "mcts", 1.0),
        "3": ChessBot("RandomBot", "random", 0.1),
        "4": ChessBot("DeepBot", "alphabeta", 3.0),
        "5": ChessBot("QuickBot", "alphabeta", 0.5),
    }
    
    print("Available bots:")
    for key, bot in bots.items():
        print(f"  {key}. {bot.name} ({bot.engine_type}, {bot.time_limit}s)")
    
    # Select bots
    while True:
        try:
            bot1_choice = input("\nSelect first bot (1-5): ").strip()
            if bot1_choice in bots:
                bot1 = bots[bot1_choice]
                break
            else:
                print("Invalid choice!")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            return
    
    while True:
        try:
            bot2_choice = input("Select second bot (1-5): ").strip()
            if bot2_choice in bots and bot2_choice != bot1_choice:
                bot2 = bots[bot2_choice]
                break
            else:
                print("Invalid choice or same as first bot!")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            return
    
    # Game settings
    try:
        max_moves = int(input("Maximum moves (default 50): ") or "50")
        show_analysis = input("Show analysis? (y/n, default y): ").strip().lower() != 'n'
    except (ValueError, KeyboardInterrupt):
        max_moves = 50
        show_analysis = True
    
    # Play the game
    try:
        final_board, stats = play_bot_vs_bot(bot1, bot2, max_moves, show_analysis)
        
        # Ask for another game
        if input("\nPlay another game? (y/n): ").strip().lower() == 'y':
            main()
        else:
            print("Thanks for playing!")
            
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Goodbye!")
    except Exception as e:
        print(f"\nError during game: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
