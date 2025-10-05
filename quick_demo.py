#!/usr/bin/env python3
"""
Quick Chess Demo

Simple demonstration of the chess engine working with optimal moves.
"""

import sys
import os
import chess
import time

# Add chessai to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'chessai'))


def print_simple_board(board: chess.Board):
    """Print a simple ASCII chess board."""
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
            
            print(f" {symbol}", end="")
        print(f" {8-i}")
    print("   a b c d e f g h")
    
    # Print game status
    if board.is_checkmate():
        print(f"\n CHECKMATE! {'White' if board.turn == chess.BLACK else 'Black'} wins!")
    elif board.is_stalemate():
        print("\n STALEMATE! Game is a draw.")
    elif board.is_check():
        print(f"\n  CHECK! {'White' if board.turn == chess.WHITE else 'Black'} king is in check.")
    else:
        print(f"\n  Turn: {'White' if board.turn == chess.WHITE else 'Black'}")
    
    print(f"FEN: {board.fen()}")
    print("="*50)


def demo_engine_moves():
    """Demonstrate engine making optimal moves."""
    print(" Chess Engine Demo - Optimal Moves")
    print("="*60)
    
    try:
        # Import engine modules
        from chessai.engine.search_alphabeta import best_move_alphabeta, analyse_alphabeta
        from chessai.engine.evaluation import evaluate_position
        
        print(" Engine modules loaded successfully!")
        
        # Create initial position
        board = chess.Board()
        print_simple_board(board)
        
        # Show some optimal moves
        moves_to_play = 10
        print(f"\n Playing {moves_to_play} optimal moves...")
        
        for move_num in range(1, moves_to_play + 1):
            if board.is_game_over():
                print(f"\n Game over at move {move_num - 1}")
                break
            
            player = "White" if board.turn == chess.WHITE else "Black"
            print(f"\n--- Move {move_num} ({player}) ---")
            
            # Get optimal move
            start_time = time.time()
            best_move = best_move_alphabeta(board, time_limit_s=1.0)
            move_time = time.time() - start_time
            
            if best_move:
                # Make the move
                board.push(best_move)
                print(f" {player} plays: {best_move} (took {move_time:.2f}s)")
                
                # Show position evaluation
                value, centipawns = evaluate_position(board)
                print(f" Position: {value:.3f} ({centipawns:+d} cp)")
                
                # Show board
                print_simple_board(board)
                
                # Brief pause
                time.sleep(0.5)
            else:
                print(f" No legal moves for {player}")
                break
        
        print(f"\n Demo completed! Final result: {board.result()}")
        
    except ImportError as e:
        print(f" Import error: {e}")
        print("Make sure to install dependencies: pip install -r requirements.txt")
    except Exception as e:
        print(f" Error: {e}")
        import traceback
        traceback.print_exc()


def demo_position_analysis():
    """Demonstrate position analysis."""
    print("\n Position Analysis Demo")
    print("="*60)
    
    try:
        from chessai.engine.search_alphabeta import analyse_alphabeta
        from chessai.engine.evaluation import evaluate_position
        
        # Test different positions
        positions = [
            ("Starting Position", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"),
            ("After e4 e5", "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2"),
            ("Tactical Position", "r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1"),
        ]
        
        for name, fen in positions:
            print(f"\n--- {name} ---")
            board = chess.Board(fen)
            print_simple_board(board)
            
            # Analyze position
            print(f"\n Engine analysis:")
            result = analyse_alphabeta(board, time_limit_s=2.0)
            print(f"   Best move: {result.get('bestmove', 'None')}")
            print(f"   Score: {result.get('value', 0):.3f}")
            print(f"   Centipawns: {result.get('centipawns', 0)}")
            print(f"   Nodes: {result.get('nodes', 0)}")
            
            time.sleep(1)
        
    except Exception as e:
        print(f" Analysis error: {e}")


def main():
    """Main demo function."""
    print(" ChessAI Quick Demo")
    print("="*60)
    print("This demo shows the chess engine making optimal moves.")
    print("="*60)
    
    try:
        # Test basic chess functionality
        import chess
        print(" Python-chess library working")
        
        # Demo engine moves
        demo_engine_moves()
        
        # Demo position analysis
        demo_position_analysis()
        
        print(f"\n All demos completed successfully!")
        print(f"\nTo run more advanced demos:")
        print(f"  python bot_vs_bot.py      # Bot vs Bot games")
        print(f"  python tournament.py     # Tournament mode")
        print(f"  python visualize_chess.py # Interactive chess")
        
    except ImportError as e:
        print(f" Missing dependency: {e}")
        print(f"Install with: pip install -r requirements.txt")
    except Exception as e:
        print(f" Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
