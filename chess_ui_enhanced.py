#!/usr/bin/env python3
"""
Enhanced Chess UI - Professional Interface

A complete chess application with beautiful board display, move logging, and professional interface.
"""

import sys
import os
import chess
import time
import random
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Add chessai to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'chessai'))

from chessai.engine.search_alphabeta import best_move_alphabeta, analyse_alphabeta
from chessai.engine.evaluation import evaluate_position, value_to_centipawns


@dataclass
class MoveLog:
    """Move log entry."""
    move_number: int
    white_move: str
    black_move: str
    white_time: float
    black_time: float
    white_eval: float
    black_eval: float
    white_centipawns: int
    black_centipawns: int
    white_nodes: int
    black_nodes: int


class ChessUI:
    """Enhanced chess UI with professional board display."""
    
    def __init__(self):
        """Initialize chess UI."""
        self.board = chess.Board()
        self.move_log = []
        self.game_start_time = time.time()
        self.current_move_number = 1
        
    def create_enhanced_board(self, last_move: Optional[chess.Move] = None, 
                            highlight_squares: List[int] = None) -> str:
        """Create an enhanced visual chess board."""
        if highlight_squares is None:
            highlight_squares = []
        
        lines = []
        
        # Top border
        lines.append("┌" + "─" * 49 + "┐")
        
        # Board with enhanced styling
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
                
                # Determine square color and highlighting
                is_light = (i + j) % 2 == 0
                is_highlighted = square in highlight_squares
                is_last_move = last_move and (square == last_move.from_square or square == last_move.to_square)
                
                if is_last_move:
                    bg = "█"  # Solid block for last move
                elif is_highlighted:
                    bg = "▓"  # Medium block for highlights
                elif is_light:
                    bg = "░"  # Light block for light squares
                else:
                    bg = "▒"  # Medium block for dark squares
                
                line += f"{bg}{symbol} "
            
            line += f"│{8-i}"
            lines.append(line)
        
        # Bottom border
        lines.append("└" + "─" * 49 + "┘")
        lines.append("    a   b   c   d   e   f   g   h")
        
        return "\n".join(lines)
    
    def print_game_header(self):
        """Print game header with information."""
        print("\n" + "="*80)
        print("CHESS GAME - ENHANCED INTERFACE")
        print("="*80)
        print(f"Game started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Move: {self.current_move_number}")
        print(f"Turn: {'White' if self.board.turn == chess.WHITE else 'Black'}")
        
        # Game status
        if self.board.is_checkmate():
            winner = "Black" if self.board.turn == chess.WHITE else "White"
            print(f"STATUS: CHECKMATE! {winner} wins!")
        elif self.board.is_stalemate():
            print("STATUS: STALEMATE! Game is a draw.")
        elif self.board.is_check():
            print(f"STATUS: CHECK! {'White' if self.board.turn == chess.WHITE else 'Black'} king is in check.")
        else:
            print("STATUS: Game in progress")
        
        # Position evaluation
        value, centipawns = evaluate_position(self.board)
        print(f"Position: {value:.3f} ({centipawns:+d} cp)")
        
        if centipawns > 100:
            print("White has a significant advantage")
        elif centipawns < -100:
            print("Black has a significant advantage")
        else:
            print("Position is roughly equal")
    
    def print_move_log(self, max_moves: int = 10):
        """Print recent move log."""
        print(f"\n{'='*80}")
        print("MOVE LOG")
        print(f"{'='*80}")
        print(f"{'Move':<4} {'White':<12} {'Black':<12} {'Time':<8} {'Eval':<8} {'Nodes':<8}")
        print("-" * 80)
        
        # Show recent moves
        recent_moves = self.move_log[-max_moves:] if self.move_log else []
        
        for log_entry in recent_moves:
            white_time = f"{log_entry.white_time:.1f}s" if log_entry.white_time > 0 else "-"
            black_time = f"{log_entry.black_time:.1f}s" if log_entry.black_time > 0 else "-"
            white_eval = f"{log_entry.white_centipawns:+d}" if log_entry.white_centipawns != 0 else "-"
            black_eval = f"{log_entry.black_centipawns:+d}" if log_entry.black_centipawns != 0 else "-"
            white_nodes = f"{log_entry.white_nodes:,}" if log_entry.white_nodes > 0 else "-"
            black_nodes = f"{log_entry.black_nodes:,}" if log_entry.black_nodes > 0 else "-"
            
            print(f"{log_entry.move_number:<4} {log_entry.white_move:<12} {log_entry.black_move:<12} "
                  f"{white_time:<8} {white_eval:<8} {white_nodes:<8}")
            if log_entry.black_move != "-":
                print(f"     {'':<12} {log_entry.black_move:<12} "
                      f"{black_time:<8} {black_eval:<8} {black_nodes:<8}")
    
    def add_move_to_log(self, move: str, player: str, move_time: float, 
                       evaluation: float, centipawns: int, nodes: int):
        """Add move to log."""
        if player == "White":
            if not self.move_log or self.move_log[-1].white_move != "-":
                # Start new move entry
                self.move_log.append(MoveLog(
                    move_number=self.current_move_number,
                    white_move=move,
                    black_move="-",
                    white_time=move_time,
                    black_time=0.0,
                    white_eval=evaluation,
                    black_eval=0.0,
                    white_centipawns=centipawns,
                    black_centipawns=0,
                    white_nodes=nodes,
                    black_nodes=0
                ))
            else:
                # Update existing entry
                self.move_log[-1].white_move = move
                self.move_log[-1].white_time = move_time
                self.move_log[-1].white_eval = evaluation
                self.move_log[-1].white_centipawns = centipawns
                self.move_log[-1].white_nodes = nodes
        else:
            # Black move
            if not self.move_log or self.move_log[-1].black_move != "-":
                # Start new move entry
                self.move_log.append(MoveLog(
                    move_number=self.current_move_number,
                    white_move="-",
                    black_move=move,
                    white_time=0.0,
                    black_time=move_time,
                    white_eval=0.0,
                    black_eval=evaluation,
                    white_centipawns=0,
                    black_centipawns=centipawns,
                    white_nodes=0,
                    black_nodes=nodes
                ))
            else:
                # Update existing entry
                self.move_log[-1].black_move = move
                self.move_log[-1].black_time = move_time
                self.move_log[-1].black_eval = evaluation
                self.move_log[-1].black_centipawns = centipawns
                self.move_log[-1].black_nodes = nodes
    
    def display_board(self, last_move: Optional[chess.Move] = None):
        """Display the chess board with enhanced styling."""
        print(f"\n{'='*80}")
        print("CHESS BOARD")
        print(f"{'='*80}")
        print(self.create_enhanced_board(last_move))
        print(f"{'='*80}")


class ChessEngine:
    """Enhanced chess engine with detailed logging."""
    
    def __init__(self, name: str = "ChessAI", time_limit: float = 2.0):
        """Initialize chess engine."""
        self.name = name
        self.time_limit = time_limit
        self.total_time = 0.0
        self.total_nodes = 0
        self.moves_played = 0
        self.move_times = []
        self.evaluations = []
        self.nodes_searched = []
    
    def get_move_with_analysis(self, board: chess.Board) -> Tuple[Optional[chess.Move], Dict]:
        """Get best move with detailed analysis."""
        if board.is_game_over():
            return None, {}
        
        start_time = time.time()
        
        try:
            # Get move analysis
            result = analyse_alphabeta(board, self.time_limit)
            
            move_time = time.time() - start_time
            self.total_time += move_time
            self.total_nodes += result.get('nodes', 0)
            self.moves_played += 1
            
            # Store statistics
            self.move_times.append(move_time)
            self.evaluations.append(result.get('value', 0))
            self.nodes_searched.append(result.get('nodes', 0))
            
            return result.get('bestmove'), result
            
        except Exception as e:
            print(f"Prediction error: {e}")
            # Fallback to random move
            legal_moves = list(board.legal_moves)
            if legal_moves:
                move = random.choice(legal_moves)
                return move, {'value': 0, 'centipawns': 0, 'nodes': 0}
            return None, {}
    
    def get_statistics(self) -> Dict:
        """Get engine statistics."""
        avg_time = self.total_time / max(1, self.moves_played)
        avg_nodes = self.total_nodes / max(1, self.moves_played)
        
        return {
            'name': self.name,
            'moves_played': self.moves_played,
            'total_time': self.total_time,
            'average_time': avg_time,
            'total_nodes': self.total_nodes,
            'average_nodes': avg_nodes,
            'move_times': self.move_times,
            'evaluations': self.evaluations,
            'nodes_searched': self.nodes_searched
        }


def play_enhanced_game(engine1: ChessEngine, engine2: ChessEngine, max_moves: int = 100):
    """Play an enhanced chess game with detailed logging."""
    ui = ChessUI()
    
    print("ENHANCED CHESS GAME")
    print("="*80)
    print(f"White: {engine1.name}")
    print(f"Black: {engine2.name}")
    print(f"Time limit: {engine1.time_limit}s per move")
    print("="*80)
    
    # Show initial position
    ui.print_game_header()
    ui.display_board()
    
    move_count = 0
    last_move = None
    
    while not ui.board.is_game_over() and move_count < max_moves:
        move_count += 1
        ui.current_move_number = move_count
        
        # Determine current player
        current_engine = engine1 if ui.board.turn == chess.WHITE else engine2
        player_name = f"{current_engine.name} (White)" if ui.board.turn == chess.WHITE else f"{current_engine.name} (Black)"
        
        print(f"\n{'-'*80}")
        print(f"MOVE {move_count} - {player_name}")
        print(f"{'-'*80}")
        
        # Get move with analysis
        print(f"{current_engine.name} is analyzing...")
        move, analysis = current_engine.get_move_with_analysis(ui.board)
        
        if move is None:
            print(f"{current_engine.name} has no legal moves!")
            break
        
        # Make the move
        ui.board.push(move)
        last_move = move
        
        # Calculate move time
        move_time = analysis.get('time', 0)
        evaluation = analysis.get('value', 0)
        centipawns = analysis.get('centipawns', 0)
        nodes = analysis.get('nodes', 0)
        
        # Add to move log
        player = "White" if ui.board.turn == chess.BLACK else "Black"  # Move was just made
        ui.add_move_to_log(str(move), player, move_time, evaluation, centipawns, nodes)
        
        print(f"{current_engine.name} plays: {move}")
        print(f"Move time: {move_time:.2f}s")
        print(f"Evaluation: {evaluation:.3f} ({centipawns:+d} cp)")
        print(f"Nodes searched: {nodes:,}")
        
        if 'pv' in analysis and analysis['pv']:
            print(f"Principal variation: {' '.join(analysis['pv'])}")
        
        # Display updated board
        ui.print_game_header()
        ui.display_board(last_move)
        
        # Show move log
        ui.print_move_log()
        
        # Brief pause
        time.sleep(1)
    
    # Game over
    print(f"\n{'='*80}")
    print("GAME OVER")
    print(f"{'='*80}")
    print(f"Result: {ui.board.result()}")
    print(f"Total moves: {len(ui.move_log)}")
    print(f"Game time: {time.time() - ui.game_start_time:.1f} seconds")
    print(f"Final position: {ui.board.fen()}")
    
    # Final statistics
    print(f"\n{'='*80}")
    print("FINAL STATISTICS")
    print(f"{'='*80}")
    
    stats1 = engine1.get_statistics()
    stats2 = engine2.get_statistics()
    
    print(f"\n{stats1['name']} (White):")
    print(f"  Moves played: {stats1['moves_played']}")
    print(f"  Total time: {stats1['total_time']:.2f}s")
    print(f"  Average time: {stats1['average_time']:.2f}s per move")
    print(f"  Total nodes: {stats1['total_nodes']:,}")
    print(f"  Average nodes: {stats1['average_nodes']:.0f} per move")
    
    print(f"\n{stats2['name']} (Black):")
    print(f"  Moves played: {stats2['moves_played']}")
    print(f"  Total time: {stats2['total_time']:.2f}s")
    print(f"  Average time: {stats2['average_time']:.2f}s per move")
    print(f"  Total nodes: {stats2['total_nodes']:,}")
    print(f"  Average nodes: {stats2['average_nodes']:.0f} per move")
    
    # Show complete move log
    print(f"\n{'='*80}")
    print("COMPLETE MOVE LOG")
    print(f"{'='*80}")
    ui.print_move_log(max_moves=len(ui.move_log))


def main():
    """Main enhanced chess application."""
    print("ENHANCED CHESS ENGINE")
    print("="*80)
    print("Professional chess interface with detailed logging and analysis")
    print("="*80)
    
    # Create engines
    engines = {
        "1": ChessEngine("AlphaBot", 1.0),
        "2": ChessEngine("DeepBot", 3.0),
        "3": ChessEngine("QuickBot", 0.5),
        "4": ChessEngine("MCTSBot", 2.0),
    }
    
    print("\nAvailable engines:")
    for key, engine in engines.items():
        print(f"  {key}. {engine.name} ({engine.time_limit}s)")
    
    # Select engines
    while True:
        try:
            engine1_choice = input("\nSelect first engine (1-4): ").strip()
            if engine1_choice in engines:
                engine1 = engines[engine1_choice]
                break
            else:
                print("Invalid choice!")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            return
    
    while True:
        try:
            engine2_choice = input("Select second engine (1-4): ").strip()
            if engine2_choice in engines and engine2_choice != engine1_choice:
                engine2 = engines[engine2_choice]
                break
            else:
                print("Invalid choice or same as first engine!")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            return
    
    # Game settings
    try:
        max_moves = int(input("Maximum moves (default 50): ") or "50")
    except (ValueError, KeyboardInterrupt):
        max_moves = 50
    
    # Play the game
    try:
        play_enhanced_game(engine1, engine2, max_moves)
        
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
