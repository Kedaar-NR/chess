#!/usr/bin/env python3
"""
ChessAI Engine Demo

Demonstrates the chess engine with working examples and visualization.
"""

import sys
import os
import chess
import chess.svg
import time
from typing import List, Optional

# Add chessai to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'chessai'))

from chessai.engine.search_mcts import best_move, analyse_simple
from chessai.engine.search_alphabeta import best_move_alphabeta, analyse_alphabeta
from chessai.engine.evaluation import evaluate_position, value_to_centipawns
from chessai.engine.move_index import move_index
from chessai.models.policy_value import PolicyValueNetwork


def print_board(board: chess.Board, last_move: Optional[chess.Move] = None) -> None:
    """Print a visual representation of the chess board."""
    print("\n" + "="*50)
    print("CHESS BOARD")
    print("="*50)
    
    # Print board with coordinates
    print("   a b c d e f g h")
    for i in range(8):
        print(f"{8-i} ", end="")
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
            
            print(symbol, end="")
        print(f" {8-i}")
    print("   a b c d e f g h")
    
    # Print game status
    if board.is_checkmate():
        print(f"\nCHECKMATE! {'White' if board.turn == chess.BLACK else 'Black'} wins!")
    elif board.is_stalemate():
        print("\nSTALEMATE! Game is a draw.")
    elif board.is_check():
        print(f"\nCHECK! {'White' if board.turn == chess.WHITE else 'Black'} king is in check.")
    else:
        print(f"\nTurn: {'White' if board.turn == chess.WHITE else 'Black'}")
    
    print(f"FEN: {board.fen()}")
    print("="*50)


def analyze_position(board: chess.Board, engine_type: str = "alphabeta") -> dict:
    """Analyze a chess position."""
    print(f"\nAnalyzing position with {engine_type} engine...")
    
    start_time = time.time()
    
    if engine_type == "alphabeta":
        result = analyse_alphabeta(board, time_limit_s=2.0)
    else:
        # Use dummy network for MCTS
        network = PolicyValueNetwork(None)
        result = analyse_simple(board, time_limit_s=2.0, network=network)
    
    analysis_time = time.time() - start_time
    
    print(f"Analysis completed in {analysis_time:.2f} seconds")
    print(f"Best move: {result.get('bestmove', 'None')}")
    print(f"Score: {result.get('value', 0):.3f}")
    print(f"Centipawns: {result.get('centipawns', 0)}")
    print(f"Nodes searched: {result.get('nodes', 0)}")
    
    if 'pv' in result and result['pv']:
        print(f"Principal variation: {' '.join(result['pv'])}")
    
    return result


def play_interactive_game():
    """Play an interactive chess game."""
    print("\n" + "="*60)
    print("INTERACTIVE CHESS GAME")
    print("="*60)
    print("Commands:")
    print("  - Enter moves in UCI format (e.g., 'e2e4')")
    print("  - Type 'analyze' to analyze current position")
    print("  - Type 'undo' to undo last move")
    print("  - Type 'quit' to exit")
    print("="*60)
    
    board = chess.Board()
    move_history = []
    
    while not board.is_game_over():
        print_board(board)
        
        # Show legal moves
        legal_moves = list(board.legal_moves)
        print(f"\nLegal moves ({len(legal_moves)}):")
        for i, move in enumerate(legal_moves[:10]):  # Show first 10 moves
            print(f"  {i+1}. {move}")
        if len(legal_moves) > 10:
            print(f"  ... and {len(legal_moves) - 10} more")
        
        # Get user input
        user_input = input(f"\n{'White' if board.turn == chess.WHITE else 'Black'} to move: ").strip()
        
        if user_input.lower() == 'quit':
            break
        elif user_input.lower() == 'analyze':
            analyze_position(board)
            continue
        elif user_input.lower() == 'undo':
            if move_history:
                board.pop()
                move_history.pop()
                print("Move undone.")
            else:
                print("No moves to undo.")
            continue
        
        # Try to make the move
        try:
            move = chess.Move.from_uci(user_input)
            if move in legal_moves:
                board.push(move)
                move_history.append(move)
                print(f"Move {len(move_history)}: {move}")
            else:
                print("Illegal move! Try again.")
        except ValueError:
            print("Invalid move format! Use UCI notation (e.g., 'e2e4').")
    
    # Game over
    print_board(board)
    print(f"\nGame over! Result: {board.result()}")


def test_engine_strength():
    """Test engine strength with different positions."""
    print("\n" + "="*60)
    print("ENGINE STRENGTH TEST")
    print("="*60)
    
    test_positions = [
        ("Initial Position", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"),
        ("After e4 e5", "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2"),
        ("Tactical Position", "r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1"),
        ("Endgame", "8/8/8/8/8/8/8/4K3 w - - 0 1"),
    ]
    
    for name, fen in test_positions:
        print(f"\n--- {name} ---")
        board = chess.Board(fen)
        print_board(board)
        
        # Test both engines
        for engine_type in ["alphabeta", "mcts"]:
            print(f"\n{engine_type.upper()} Engine:")
            result = analyze_position(board, engine_type)
            time.sleep(0.5)  # Brief pause between analyses


def test_move_indexing():
    """Test move indexing functionality."""
    print("\n" + "="*60)
    print("MOVE INDEXING TEST")
    print("="*60)
    
    board = chess.Board()
    legal_moves = list(board.legal_moves)
    
    print(f"Testing {len(legal_moves)} legal moves...")
    
    # Test move to ID conversion
    move_ids = []
    for move in legal_moves:
        move_id = move_index.to_id(move)
        move_ids.append(move_id)
        print(f"Move {move} -> ID {move_id}")
    
    # Test ID to move conversion
    print("\nTesting reverse conversion...")
    for i, move in enumerate(legal_moves):
        move_id = move_ids[i]
        converted_move = move_index.from_id(move_id, board)
        if converted_move == move:
            print(f"✓ ID {move_id} -> Move {converted_move}")
        else:
            print(f"✗ ID {move_id} -> Move {converted_move} (expected {move})")
    
    # Test legal move mask
    legal_mask = move_index.get_legal_move_mask(board)
    legal_count = sum(legal_mask)
    print(f"\nLegal move mask: {legal_count} legal moves out of {len(legal_mask)} total")
    
    print(f"Action space size: {move_index.action_space_size()}")


def main():
    """Main demo function."""
    print("ChessAI Engine Demo")
    print("==================")
    
    # Test move indexing
    test_move_indexing()
    
    # Test engine strength
    test_engine_strength()
    
    # Interactive game
    play_interactive_game()
    
    print("\nDemo completed!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
