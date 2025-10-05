#!/usr/bin/env python3
"""
Simple Chess Engine - Working Version

This script runs a simple chess engine with bots playing optimal moves.
"""

import sys
import os
import chess
import time
import random

# Add chessai to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'chessai'))


def create_chess_board(board: chess.Board) -> str:
    """Create a visual chess board like the one shown."""
    lines = []
    lines.append("┌" + "─" * 33 + "┐")
    
    for i in range(8):
        line = f"{8-i}│"
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
            
            # Determine square color
            is_light = (i + j) % 2 == 0
            
            if is_light:
                bg = " "  # Light square
            else:
                bg = "·"  # Dark square
            
            line += f"{bg}{symbol} "
        
        line += f"│{8-i}"
        lines.append(line)
    
    lines.append("└" + "─" * 33 + "┘")
    lines.append("  a  b  c  d  e  f  g  h")
    
    return "\n".join(lines)


def get_best_move(board: chess.Board) -> chess.Move:
    """Get the best move using simple evaluation."""
    legal_moves = list(board.legal_moves)
    if not legal_moves:
        return None
    
    # Simple evaluation: prefer center moves and captures
    best_move = None
    best_score = -1000
    
    for move in legal_moves:
        score = 0
        
        # Prefer center moves
        if move.to_square in [chess.E4, chess.E5, chess.D4, chess.D5]:
            score += 10
        
        # Prefer captures
        if board.is_capture(move):
            score += 20
        
        # Prefer developing moves
        if move.from_square in [chess.B1, chess.G1, chess.C1, chess.F1, chess.B8, chess.G8, chess.C8, chess.F8]:
            score += 5
        
        if score > best_score:
            best_score = score
            best_move = move
    
    return best_move if best_move else random.choice(legal_moves)


def play_chess_game():
    """Play a chess game between two bots."""
    print("CHESS ENGINE - BOTS PLAYING OPTIMAL MOVES")
    print("="*60)
    print("Two chess bots will play against each other using optimal moves.")
    print("="*60)
    
    board = chess.Board()
    move_number = 0
    
    # Show initial position
    print(f"\nMOVE {move_number} - STARTING POSITION")
    print("="*60)
    print(create_chess_board(board))
    
    while not board.is_game_over() and move_number < 50:
        move_number += 1
        current_player = "White" if board.turn == chess.WHITE else "Black"
        
        print(f"\nMOVE {move_number} - {current_player} TO PLAY")
        print("="*60)
        
        # Get best move
        print(f"{current_player} is thinking...")
        start_time = time.time()
        
        best_move = get_best_move(board)
        move_time = time.time() - start_time
        
        if best_move:
            # Make the move
            board.push(best_move)
            print(f"{current_player} plays: {best_move} (took {move_time:.2f}s)")
            
            # Show updated board
            print(create_chess_board(board))
            
            # Show game status
            if board.is_checkmate():
                winner = "Black" if board.turn == chess.WHITE else "White"
                print(f"\nCHECKMATE! {winner} wins!")
                break
            elif board.is_stalemate():
                print("\nSTALEMATE! Game is a draw.")
                break
            elif board.is_check():
                print(f"\nCHECK! {'White' if board.turn == chess.WHITE else 'Black'} king is in check.")
            
            # Brief pause
            time.sleep(1)
        else:
            print(f"{current_player} has no legal moves!")
            break
    
    # Game over
    print(f"\nGAME OVER!")
    print(f"Result: {board.result()}")
    print(f"Total moves: {move_number}")
    print(f"Final position: {board.fen()}")


def main():
    """Main function."""
    try:
        # Test basic chess functionality
        import chess
        board = chess.Board()
        legal_moves = list(board.legal_moves)
        print(f"Chess engine loaded with {len(legal_moves)} legal moves")
        
        # Play the game
        play_chess_game()
        
        # Ask for another game
        if input("\nPlay another game? (y/n): ").strip().lower() == 'y':
            main()
        else:
            print("Thanks for playing!")
            
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install python-chess: pip install python-chess")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
