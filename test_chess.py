#!/usr/bin/env python3
"""
Test script to verify chess engine functionality.
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import chess
        print("✓ python-chess imported successfully")
    except ImportError:
        print("✗ python-chess not found. Install with: pip install python-chess")
        return False
    
    try:
        import tensorflow as tf
        print("✓ TensorFlow imported successfully")
    except ImportError:
        print("✗ TensorFlow not found. Install with: pip install tensorflow")
        return False
    
    try:
        import numpy as np
        print("✓ NumPy imported successfully")
    except ImportError:
        print("✗ NumPy not found. Install with: pip install numpy")
        return False
    
    return True


def test_chess_basics():
    """Test basic chess functionality."""
    print("\nTesting chess basics...")
    
    try:
        import chess
        
        # Test board creation
        board = chess.Board()
        print(f"✓ Board created: {board.fen()}")
        
        # Test move generation
        legal_moves = list(board.legal_moves)
        print(f"✓ Legal moves generated: {len(legal_moves)} moves")
        
        # Test move execution
        e4 = chess.Move.from_uci("e2e4")
        if e4 in legal_moves:
            board.push(e4)
            print(f"✓ Move executed: e2e4")
            print(f"✓ New position: {board.fen()}")
        else:
            print("✗ Move e2e4 not legal")
            return False
        
        # Test game over detection
        if board.is_game_over():
            print("✗ Game over detected too early")
            return False
        else:
            print("✓ Game not over (correct)")
        
        return True
        
    except Exception as e:
        print(f"✗ Chess basics test failed: {e}")
        return False


def test_engine_modules():
    """Test chess engine modules."""
    print("\nTesting engine modules...")
    
    try:
        # Add chessai to path
        sys.path.append(os.path.join(os.path.dirname(__file__), 'chessai'))
        
        # Test move index
        from chessai.engine.move_index import move_index
        print(f"✓ Move index loaded, action space: {move_index.action_space_size()}")
        
        # Test evaluation
        from chessai.engine.evaluation import evaluate_position, value_to_centipawns
        print("✓ Evaluation module loaded")
        
        # Test search
        from chessai.engine.search_alphabeta import best_move_alphabeta
        print("✓ Alpha-beta search loaded")
        
        # Test models
        from chessai.models.policy_value import PolicyValueNetwork
        print("✓ Policy-value model loaded")
        
        return True
        
    except Exception as e:
        print(f"✗ Engine modules test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_engine_functionality():
    """Test actual engine functionality."""
    print("\nTesting engine functionality...")
    
    try:
        import chess
        sys.path.append(os.path.join(os.path.dirname(__file__), 'chessai'))
        
        from chessai.engine.search_alphabeta import best_move_alphabeta, analyse_alphabeta
        from chessai.engine.evaluation import evaluate_position
        
        # Test position evaluation
        board = chess.Board()
        value, centipawns = evaluate_position(board)
        print(f"✓ Position evaluation: {value:.3f} ({centipawns} cp)")
        
        # Test move generation
        best_move = best_move_alphabeta(board, time_limit_s=1.0)
        if best_move:
            print(f"✓ Best move found: {best_move}")
        else:
            print("✗ No best move found")
            return False
        
        # Test position analysis
        result = analyse_alphabeta(board, time_limit_s=1.0)
        print(f"✓ Position analysis: {result.get('value', 0):.3f}")
        
        return True
        
    except Exception as e:
        print(f"✗ Engine functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("ChessAI Engine Test Suite")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_imports),
        ("Chess Basics", test_chess_basics),
        ("Engine Modules", test_engine_modules),
        ("Engine Functionality", test_engine_functionality),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            print(f"✓ {test_name} PASSED")
            passed += 1
        else:
            print(f"✗ {test_name} FAILED")
    
    print(f"\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print(" All tests passed! Chess engine is working correctly.")
        print("\nYou can now run:")
        print("  python demo.py")
        print("  python visualize_chess.py")
    else:
        print(" Some tests failed. Please check the error messages above.")
        print("\nTo fix issues, try:")
        print("  pip install -r requirements.txt")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
