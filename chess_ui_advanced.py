#!/usr/bin/env python3
"""
Advanced Chess UI - Professional Interface

A complete chess application with beautiful board display, comprehensive move logging, and professional interface.
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
class MoveEntry:
    """Detailed move log entry."""
    move_number: int
    move: str
    player: str
    time_taken: float
    evaluation: float
    centipawns: int
    nodes_searched: int
    principal_variation: List[str]
    timestamp: datetime


class AdvancedChessUI:
    """Advanced chess UI with professional board display and comprehensive logging."""
    
    def __init__(self):
        """Initialize advanced chess UI."""
        self.board = chess.Board()
        self.move_history = []
        self.game_start_time = time.time()
        self.current_move_number = 1
        self.white_moves = []
        self.black_moves = []
        
    def create_professional_board(self, last_move: Optional[chess.Move] = None, 
                                highlight_squares: List[int] = None) -> str:
        """Create a professional visual chess board."""
        if highlight_squares is None:
            highlight_squares = []
        
        lines = []
        
        # Top border with coordinates
        lines.append("┌" + "─" * 65 + "┐")
        lines.append("│" + " " * 65 + "│")
        
        # Board with enhanced styling
        for i in range(8):
            line = f"│ {8-i} │"
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
            
            line += f"│ {8-i} │"
            lines.append(line)
        
        # Bottom border with coordinates
        lines.append("│" + " " * 65 + "│")
        lines.append("└" + "─" * 65 + "┘")
        lines.append("    a   b   c   d   e   f   g   h")
        
        return "\n".join(lines)
    
    def print_game_status(self):
        """Print comprehensive game status."""
        print("\n" + "="*80)
        print("CHESS GAME STATUS")
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
    
    def print_move_log(self, max_moves: int = 15):
        """Print comprehensive move log."""
        print(f"\n{'='*80}")
        print("MOVE LOG")
        print(f"{'='*80}")
        print(f"{'Move':<4} {'White':<15} {'Black':<15} {'Time':<8} {'Eval':<8} {'Nodes':<10} {'PV':<20}")
        print("-" * 80)
        
        # Show recent moves
        recent_moves = self.move_history[-max_moves:] if self.move_history else []
        
        for i, move_entry in enumerate(recent_moves):
            if i % 2 == 0:  # White move
                white_time = f"{move_entry.time_taken:.1f}s"
                white_eval = f"{move_entry.centipawns:+d}"
                white_nodes = f"{move_entry.nodes_searched:,}"
                white_pv = " ".join(move_entry.principal_variation[:3]) if move_entry.principal_variation else "-"
                
                print(f"{move_entry.move_number:<4} {move_entry.move:<15} {'-':<15} "
                      f"{white_time:<8} {white_eval:<8} {white_nodes:<10} {white_pv:<20}")
            else:  # Black move
                black_time = f"{move_entry.time_taken:.1f}s"
                black_eval = f"{move_entry.centipawns:+d}"
                black_nodes = f"{move_entry.nodes_searched:,}"
                black_pv = " ".join(move_entry.principal_variation[:3]) if move_entry.principal_variation else "-"
                
                print(f"{'':<4} {'':<15} {move_entry.move:<15} "
                      f"{black_time:<8} {black_eval:<8} {black_nodes:<10} {black_pv:<20}")
    
    def add_move_to_history(self, move_entry: MoveEntry):
        """Add move to history."""
        self.move_history.append(move_entry)
        
        if move_entry.player == "White":
            self.white_moves.append(move_entry)
        else:
            self.black_moves.append(move_entry)
    
    def display_board(self, last_move: Optional[chess.Move] = None):
        """Display the chess board with professional styling."""
        print(f"\n{'='*80}")
        print("CHESS BOARD")
        print(f"{'='*80}")
        print(self.create_professional_board(last_move))
        print(f"{'='*80}")
    
    def print_statistics(self, engine1_stats: Dict, engine2_stats: Dict):
        """Print comprehensive statistics."""
        print(f"\n{'='*80}")
        print("ENGINE STATISTICS")
        print(f"{'='*80}")
        
        print(f"\n{engine1_stats['name']} (White):")
        print(f"  Moves played: {engine1_stats['moves_played']}")
        print(f"  Total time: {engine1_stats['total_time']:.2f}s")
        print(f"  Average time: {engine1_stats['average_time']:.2f}s per move")
        print(f"  Total nodes: {engine1_stats['total_nodes']:,}")
        print(f"  Average nodes: {engine1_stats['average_nodes']:.0f} per move")
        print(f"  Fastest move: {min(engine1_stats['move_times']):.2f}s" if engine1_stats['move_times'] else "  No moves")
        print(f"  Slowest move: {max(engine1_stats['move_times']):.2f}s" if engine1_stats['move_times'] else "  No moves")
        
        print(f"\n{engine2_stats['name']} (Black):")
        print(f"  Moves played: {engine2_stats['moves_played']}")
        print(f"  Total time: {engine2_stats['total_time']:.2f}s")
        print(f"  Average time: {engine2_stats['average_time']:.2f}s per move")
        print(f"  Total nodes: {engine2_stats['total_nodes']:,}")
        print(f"  Average nodes: {engine2_stats['average_nodes']:.0f} per move")
        print(f"  Fastest move: {min(engine2_stats['move_times']):.2f}s" if engine2_stats['move_times'] else "  No moves")
        print(f"  Slowest move: {max(engine2_stats['move_times']):.2f}s" if engine2_stats['move_times'] else "  No moves")
    
    def print_game_summary(self):
        """Print game summary."""
        print(f"\n{'='*80}")
        print("GAME SUMMARY")
        print(f"{'='*80}")
        print(f"Result: {self.board.result()}")
        print(f"Total moves: {len(self.move_history)}")
        print(f"Game time: {time.time() - self.game_start_time:.1f} seconds")
        print(f"Final position: {self.board.fen()}")
        print(f"White moves: {len(self.white_moves)}")
        print(f"Black moves: {len(self.black_moves)}")


class AdvancedChessEngine:
    """Advanced chess engine with comprehensive logging."""
    
    def __init__(self, name: str = "ChessAI", time_limit: float = 2.0):
        """Initialize advanced chess engine."""
        self.name = name
        self.time_limit = time_limit
        self.total_time = 0.0
        self.total_nodes = 0
        self.moves_played = 0
        self.move_times = []
        self.evaluations = []
        self.nodes_searched = []
        self.centipawns_history = []
    
    def get_move_with_comprehensive_analysis(self, board: chess.Board) -> Tuple[Optional[chess.Move], MoveEntry]:
        """Get best move with comprehensive analysis."""
        if board.is_game_over():
            return None, None
        
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
            self.centipawns_history.append(result.get('centipawns', 0))
            
            # Create move entry
            move_entry = MoveEntry(
                move_number=self.moves_played,
                move=str(result.get('bestmove', '')),
                player="White" if board.turn == chess.WHITE else "Black",
                time_taken=move_time,
                evaluation=result.get('value', 0),
                centipawns=result.get('centipawns', 0),
                nodes_searched=result.get('nodes', 0),
                principal_variation=result.get('pv', []),
                timestamp=datetime.now()
            )
            
            return result.get('bestmove'), move_entry
            
        except Exception as e:
            print(f"Analysis error: {e}")
            # Fallback to random move
            legal_moves = list(board.legal_moves)
            if legal_moves:
                move = random.choice(legal_moves)
                move_entry = MoveEntry(
                    move_number=self.moves_played + 1,
                    move=str(move),
                    player="White" if board.turn == chess.WHITE else "Black",
                    time_taken=0.1,
                    evaluation=0.0,
                    centipawns=0,
                    nodes_searched=0,
                    principal_variation=[],
                    timestamp=datetime.now()
                )
                return move, move_entry
            return None, None
    
    def get_statistics(self) -> Dict:
        """Get comprehensive engine statistics."""
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
            'nodes_searched': self.nodes_searched,
            'centipawns_history': self.centipawns_history
        }


def play_advanced_game(engine1: AdvancedChessEngine, engine2: AdvancedChessEngine, max_moves: int = 100):
    """Play an advanced chess game with comprehensive logging."""
    ui = AdvancedChessUI()
    
    print("ADVANCED CHESS GAME")
    print("="*80)
    print(f"White: {engine1.name}")
    print(f"Black: {engine2.name}")
    print(f"Time limit: {engine1.time_limit}s per move")
    print("="*80)
    
    # Show initial position
    ui.print_game_status()
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
        
        # Get move with comprehensive analysis
        print(f"{current_engine.name} is analyzing...")
        move, move_entry = current_engine.get_move_with_comprehensive_analysis(ui.board)
        
        if move is None:
            print(f"{current_engine.name} has no legal moves!")
            break
        
        # Make the move
        ui.board.push(move)
        last_move = move
        
        # Add to move history
        ui.add_move_to_history(move_entry)
        
        print(f"{current_engine.name} plays: {move}")
        print(f"Move time: {move_entry.time_taken:.2f}s")
        print(f"Evaluation: {move_entry.evaluation:.3f} ({move_entry.centipawns:+d} cp)")
        print(f"Nodes searched: {move_entry.nodes_searched:,}")
        
        if move_entry.principal_variation:
            print(f"Principal variation: {' '.join(move_entry.principal_variation)}")
        
        # Display updated board
        ui.print_game_status()
        ui.display_board(last_move)
        
        # Show move log
        ui.print_move_log()
        
        # Brief pause
        time.sleep(1)
    
    # Game over
    print(f"\n{'='*80}")
    print("GAME OVER")
    print(f"{'='*80}")
    
    # Show game summary
    ui.print_game_summary()
    
    # Show final statistics
    stats1 = engine1.get_statistics()
    stats2 = engine2.get_statistics()
    ui.print_statistics(stats1, stats2)
    
    # Show complete move log
    print(f"\n{'='*80}")
    print("COMPLETE MOVE LOG")
    print(f"{'='*80}")
    ui.print_move_log(max_moves=len(ui.move_history))


def main():
    """Main advanced chess application."""
    print("ADVANCED CHESS ENGINE")
    print("="*80)
    print("Professional chess interface with comprehensive logging and analysis")
    print("="*80)
    
    # Create engines
    engines = {
        "1": AdvancedChessEngine("AlphaBot", 1.0),
        "2": AdvancedChessEngine("DeepBot", 3.0),
        "3": AdvancedChessEngine("QuickBot", 0.5),
        "4": AdvancedChessEngine("MCTSBot", 2.0),
        "5": AdvancedChessEngine("ProBot", 1.5),
    }
    
    print("\nAvailable engines:")
    for key, engine in engines.items():
        print(f"  {key}. {engine.name} ({engine.time_limit}s)")
    
    # Select engines
    while True:
        try:
            engine1_choice = input("\nSelect first engine (1-5): ").strip()
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
            engine2_choice = input("Select second engine (1-5): ").strip()
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
        play_advanced_game(engine1, engine2, max_moves)
        
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
