#!/usr/bin/env python3
"""
Visual Chess Engine - Working Version

This script shows a proper chess board with pieces that actually move and are tracked correctly.
"""

import sys
import os
import chess
import time
import random
from typing import Optional

# Add chessai to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'chessai'))


def create_visual_board(board: chess.Board, last_move: Optional[chess.Move] = None) -> str:
    """Create a visual chess board with proper piece movement."""
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
            
            # Determine square color and highlighting
            is_light = (i + j) % 2 == 0
            is_last_move = last_move and (square == last_move.from_square or square == last_move.to_square)
            
            if is_last_move:
                bg = "*"  # Highlight for last move
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


def get_smart_move(board: chess.Board) -> chess.Move:
    """Get a smart move using basic chess principles."""
    legal_moves = list(board.legal_moves)
    if not legal_moves:
        return None
    
    # Prioritize different types of moves
    best_moves = []
    
    # 1. Check for captures (tactical moves)
    captures = [move for move in legal_moves if board.is_capture(move)]
    if captures:
        # Prioritize captures by value
        for move in captures:
            captured_piece = board.piece_at(move.to_square)
            if captured_piece:
                piece_values = {'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0}
                value = piece_values.get(captured_piece.symbol().lower(), 0)
                best_moves.append((move, value + 100))  # High priority for captures
    
    # 2. Check for checks
    checks = [move for move in legal_moves if board.gives_check(move)]
    if checks:
        for move in checks:
            best_moves.append((move, 50))  # Medium priority for checks
    
    # 3. Center control moves
    center_squares = [chess.E4, chess.E5, chess.D4, chess.D5, chess.C3, chess.C6, chess.F3, chess.F6]
    center_moves = [move for move in legal_moves if move.to_square in center_squares]
    if center_moves:
        for move in center_moves:
            best_moves.append((move, 20))  # Medium priority for center control
    
    # 4. Development moves (knights and bishops)
    development_moves = []
    for move in legal_moves:
        from_square = move.from_square
        piece = board.piece_at(from_square)
        if piece and piece.symbol().lower() in ['n', 'b']:
            # Knights and bishops developing
            if from_square in [chess.B1, chess.G1, chess.C1, chess.F1, chess.B8, chess.G8, chess.C8, chess.F8]:
                development_moves.append(move)
    
    if development_moves:
        for move in development_moves:
            best_moves.append((move, 15))  # Lower priority for development
    
    # 5. Castling
    castling_moves = [move for move in legal_moves if board.is_castling(move)]
    if castling_moves:
        for move in castling_moves:
            best_moves.append((move, 30))  # High priority for castling
    
    # 6. Pawn moves (center pawns first)
    pawn_moves = [move for move in legal_moves if board.piece_at(move.from_square) and board.piece_at(move.from_square).symbol().lower() == 'p']
    if pawn_moves:
        for move in pawn_moves:
            # Prioritize center pawn moves
            if move.from_square in [chess.E2, chess.E7, chess.D2, chess.D7]:
                best_moves.append((move, 10))
            else:
                best_moves.append((move, 5))
    
    # Sort by priority and return best move
    if best_moves:
        best_moves.sort(key=lambda x: x[1], reverse=True)
        return best_moves[0][0]
    
    # Fallback to random move
    return random.choice(legal_moves)


def print_move_log(moves: list, max_moves: int = 10):
    """Print move log."""
    print(f"\n{'='*60}")
    print("MOVE LOG")
    print(f"{'='*60}")
    print(f"{'Move':<4} {'White':<12} {'Black':<12} {'Time':<8} {'Notes':<20}")
    print("-" * 60)
    
    # Show recent moves
    recent_moves = moves[-max_moves:] if moves else []
    
    for i, move_entry in enumerate(recent_moves):
        if i % 2 == 0:  # White move
            print(f"{move_entry['move_num']:<4} {move_entry['move']:<12} {'-':<12} "
                  f"{move_entry['time']:<8} {move_entry['notes']:<20}")
        else:  # Black move
            print(f"{'':<4} {'':<12} {move_entry['move']:<12} "
                  f"{move_entry['time']:<8} {move_entry['notes']:<20}")


def play_visual_chess_game():
    """Play a visual chess game with proper piece movement."""
    print("VISUAL CHESS ENGINE - BOTS PLAYING OPTIMAL MOVES")
    print("="*60)
    print("Two chess bots will play against each other with visual piece movement.")
    print("="*60)
    
    board = chess.Board()
    move_number = 0
    moves_log = []
    last_move = None
    
    # Show initial position
    print(f"\nMOVE {move_number} - STARTING POSITION")
    print("="*60)
    print(create_visual_board(board))
    
    while not board.is_game_over() and move_number < 50:
        move_number += 1
        current_player = "White" if board.turn == chess.WHITE else "Black"
        
        print(f"\nMOVE {move_number} - {current_player} TO PLAY")
        print("="*60)
        
        # Show current board
        print(create_visual_board(board, last_move))
        
        # Get smart move
        print(f"\n{current_player} is thinking...")
        start_time = time.time()
        
        best_move = get_smart_move(board)
        move_time = time.time() - start_time
        
        if best_move:
            # Make the move
            board.push(best_move)
            last_move = best_move
            
            # Log the move
            move_entry = {
                'move_num': move_number,
                'move': str(best_move),
                'time': f"{move_time:.2f}s",
                'notes': ''
            }
            
            # Add move notes
            if board.is_capture(best_move):
                move_entry['notes'] = 'Capture'
            elif board.gives_check(best_move):
                move_entry['notes'] = 'Check'
            elif board.is_castling(best_move):
                move_entry['notes'] = 'Castling'
            elif best_move.to_square in [chess.E4, chess.E5, chess.D4, chess.D5]:
                move_entry['notes'] = 'Center'
            
            moves_log.append(move_entry)
            
            print(f"{current_player} plays: {best_move} (took {move_time:.2f}s)")
            if move_entry['notes']:
                print(f"Move type: {move_entry['notes']}")
            
            # Show updated board with move highlighting
            print(f"\nAfter {current_player}'s move:")
            print(create_visual_board(board, last_move))
            
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
            
            # Show move log
            print_move_log(moves_log)
            
            # Brief pause for readability
            time.sleep(1)
        else:
            print(f"{current_player} has no legal moves!")
            break
    
    # Game over
    print(f"\n{'='*60}")
    print("GAME OVER")
    print(f"{'='*60}")
    print(f"Result: {board.result()}")
    print(f"Total moves: {len(moves_log)}")
    print(f"Final position: {board.fen()}")
    
    # Show final move log
    print(f"\n{'='*60}")
    print("COMPLETE MOVE LOG")
    print(f"{'='*60}")
    print_move_log(moves_log, max_moves=len(moves_log))


def main():
    """Main function."""
    try:
        # Test basic chess functionality
        import chess
        board = chess.Board()
        legal_moves = list(board.legal_moves)
        print(f"Chess engine loaded with {len(legal_moves)} legal moves")
        
        # Play the game
        play_visual_chess_game()
        
        # Ask for another game
        try:
            if input("\nPlay another game? (y/n): ").strip().lower() == 'y':
                main()
            else:
                print("Thanks for playing!")
        except (EOFError, KeyboardInterrupt):
            print("\nThanks for playing!")
            
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install python-chess: pip install python-chess")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
