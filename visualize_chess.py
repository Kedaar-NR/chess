#!/usr/bin/env python3
"""
Chess Visualization Tool

Creates visual representations of chess positions and games.
"""

import sys
import os
import chess
import chess.svg
import time
from typing import List, Optional

# Add chessai to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'chessai'))

from chessai.engine.search_alphabeta import best_move_alphabeta, analyse_alphabeta
from chessai.engine.evaluation import evaluate_position


def create_ascii_board(board: chess.Board, last_move: Optional[chess.Move] = None) -> str:
    """Create ASCII representation of chess board."""
    lines = []
    lines.append("   a b c d e f g h")
    
    for i in range(8):
        line = f"{8-i} "
        for j in range(8):
            square = chess.square(j, 7-i)
            piece = board.piece_at(square)
            
            if piece:
                symbol = piece.symbol()
                if piece.color == chess.WHITE:
                    symbol = symbol.upper()
                else:
                    symbol = symbol.lower()
            else:
                symbol = "."
            
            # Highlight last move
            if last_move and (square == last_move.from_square or square == last_move.to_square):
                symbol = f"[{symbol}]"
            else:
                symbol = f" {symbol} "
            
            line += symbol
        line += f" {8-i}"
        lines.append(line)
    
    lines.append("   a b c d e f g h")
    return "\n".join(lines)


def print_position_analysis(board: chess.Board) -> None:
    """Print detailed position analysis."""
    print("\n" + "="*60)
    print("POSITION ANALYSIS")
    print("="*60)
    
    # Print board
    print(create_ascii_board(board))
    
    # Game status
    if board.is_checkmate():
        print(f"\n CHECKMATE! {'White' if board.turn == chess.BLACK else 'Black'} wins!")
    elif board.is_stalemate():
        print("\n STALEMATE! Game is a draw.")
    elif board.is_check():
        print(f"\n  CHECK! {'White' if board.turn == chess.WHITE else 'Black'} king is in check.")
    else:
        print(f"\n  Turn: {'White' if board.turn == chess.WHITE else 'Black'}")
    
    # Legal moves
    legal_moves = list(board.legal_moves)
    print(f" Legal moves: {len(legal_moves)}")
    
    if legal_moves:
        print("Available moves:")
        for i, move in enumerate(legal_moves[:8]):  # Show first 8 moves
            print(f"  {i+1}. {move}")
        if len(legal_moves) > 8:
            print(f"  ... and {len(legal_moves) - 8} more")
    
    # Position evaluation
    value, centipawns = evaluate_position(board)
    print(f"\n Position evaluation:")
    print(f"   Value: {value:.3f}")
    print(f"   Centipawns: {centipawns}")
    
    if centipawns > 100:
        print("    White has a significant advantage")
    elif centipawns < -100:
        print("    Black has a significant advantage")
    else:
        print("    Position is roughly equal")
    
    print(f"\n FEN: {board.fen()}")
    print("="*60)


def play_engine_vs_engine():
    """Play a game between two engine instances."""
    print("\n" + "="*60)
    print("ENGINE vs ENGINE GAME")
    print("="*60)
    
    board = chess.Board()
    move_count = 0
    max_moves = 50
    
    print("Starting engine vs engine game...")
    print_position_analysis(board)
    
    while not board.is_game_over() and move_count < max_moves:
        move_count += 1
        player = "White" if board.turn == chess.WHITE else "Black"
        
        print(f"\n--- Move {move_count} ({player}) ---")
        
        # Get best move
        start_time = time.time()
        best_move = best_move_alphabeta(board, time_limit_s=1.0)
        move_time = time.time() - start_time
        
        if best_move:
            board.push(best_move)
            print(f"Engine plays: {best_move} (took {move_time:.2f}s)")
            print_position_analysis(board)
        else:
            print("No legal moves available!")
            break
        
        time.sleep(0.5)  # Brief pause between moves
    
    # Game result
    print(f"\n GAME OVER!")
    print(f"Result: {board.result()}")
    print(f"Total moves: {move_count}")
    print(f"Final position: {board.fen()}")


def analyze_famous_positions():
    """Analyze famous chess positions."""
    print("\n" + "="*60)
    print("FAMOUS POSITIONS ANALYSIS")
    print("="*60)
    
    famous_positions = [
        ("Starting Position", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"),
        ("After 1.e4 e5", "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2"),
        ("Sicilian Defense", "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2"),
        ("King's Indian", "rnbqkb1r/pppppppp/5n2/8/3PP3/8/PPP2PPP/RNBQKBNR b KQkq d3 0 2"),
        ("Endgame", "8/8/8/8/8/8/8/4K3 w - - 0 1"),
    ]
    
    for name, fen in famous_positions:
        print(f"\n--- {name} ---")
        board = chess.Board(fen)
        print_position_analysis(board)
        
        # Get engine analysis
        print(f"\n Engine analysis:")
        result = analyse_alphabeta(board, time_limit_s=2.0)
        print(f"   Best move: {result.get('bestmove', 'None')}")
        print(f"   Score: {result.get('value', 0):.3f}")
        print(f"   Centipawns: {result.get('centipawns', 0)}")
        print(f"   Nodes: {result.get('nodes', 0)}")
        
        time.sleep(1)  # Brief pause between positions


def interactive_chess():
    """Interactive chess game with human vs engine."""
    print("\n" + "="*60)
    print("INTERACTIVE CHESS (Human vs Engine)")
    print("="*60)
    print("You are White, Engine is Black")
    print("Enter moves in UCI format (e.g., 'e2e4')")
    print("Commands: 'analyze', 'undo', 'quit'")
    print("="*60)
    
    board = chess.Board()
    move_history = []
    
    while not board.is_game_over():
        print_position_analysis(board)
        
        if board.turn == chess.WHITE:
            # Human move
            while True:
                user_input = input("\nYour move: ").strip()
                
                if user_input.lower() == 'quit':
                    return
                elif user_input.lower() == 'analyze':
                    result = analyse_alphabeta(board, time_limit_s=2.0)
                    print(f"Analysis: {result.get('bestmove')} (score: {result.get('value', 0):.3f})")
                    continue
                elif user_input.lower() == 'undo':
                    if move_history:
                        board.pop()
                        move_history.pop()
                        print("Move undone.")
                        break
                    else:
                        print("No moves to undo.")
                        continue
                
                try:
                    move = chess.Move.from_uci(user_input)
                    if move in board.legal_moves:
                        board.push(move)
                        move_history.append(move)
                        print(f"✓ {move}")
                        break
                    else:
                        print("✗ Illegal move!")
                except ValueError:
                    print("✗ Invalid format! Use UCI notation (e.g., 'e2e4')")
        else:
            # Engine move
            print("\n Engine thinking...")
            start_time = time.time()
            best_move = best_move_alphabeta(board, time_limit_s=2.0)
            move_time = time.time() - start_time
            
            if best_move:
                board.push(best_move)
                move_history.append(best_move)
                print(f"Engine plays: {best_move} (took {move_time:.2f}s)")
            else:
                print("Engine has no legal moves!")
                break
    
    # Game over
    print_position_analysis(board)
    print(f"\n GAME OVER! Result: {board.result()}")


def main():
    """Main visualization function."""
    print("ChessAI Visualization Tool")
    print("=========================")
    
    while True:
        print("\nChoose an option:")
        print("1. Analyze famous positions")
        print("2. Engine vs Engine game")
        print("3. Interactive chess (Human vs Engine)")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '1':
            analyze_famous_positions()
        elif choice == '2':
            play_engine_vs_engine()
        elif choice == '3':
            interactive_chess()
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice! Please enter 1-4.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
