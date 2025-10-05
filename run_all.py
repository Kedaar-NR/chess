#!/usr/bin/env python3
"""
Run All Chess Commands

This script runs all the commands needed to make the chess engine work and display a beautiful board.
"""

import sys
import os
import subprocess
import time

def print_header():
    """Print header."""
    print("="*80)
    print("CHESS ENGINE - RUN ALL COMMANDS")
    print("="*80)
    print("This script will run all commands needed to make the chess engine work")
    print("and display a beautiful board like the one shown.")
    print("="*80)

def run_command(command, description):
    """Run a command and show progress."""
    print(f"\n{'-'*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'-'*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"Success: {description}")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {description}")
        print(f"Error: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def check_python():
    """Check Python version."""
    print(f"\nPython version: {sys.version}")
    if sys.version_info < (3, 8):
        print("Python 3.8+ required")
        return False
    print("Python version OK")
    return True

def install_dependencies():
    """Install all dependencies."""
    print(f"\n{'='*60}")
    print("INSTALLING DEPENDENCIES")
    print(f"{'='*60}")
    
    # Install basic packages
    packages = [
        "python-chess",
        "tensorflow",
        "numpy",
        "pandas",
        "scikit-learn",
        "fastapi",
        "uvicorn",
        "typer",
        "pyyaml",
        "orjson",
        "tensorboard",
        "matplotlib",
        "rich"
    ]
    
    success_count = 0
    for package in packages:
        if run_command(f"pip install {package}", f"Installing {package}"):
            success_count += 1
        else:
            print(f"Warning: Failed to install {package}")
    
    print(f"\nInstallation summary: {success_count}/{len(packages)} packages installed")
    return success_count > len(packages) // 2

def create_directories():
    """Create necessary directories."""
    print(f"\n{'='*60}")
    print("CREATING DIRECTORIES")
    print(f"{'='*60}")
    
    directories = [
        "data/raw",
        "data/tfrecords", 
        "data/selfplay",
        "runs/supervised",
        "runs/rl",
        "logs"
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"Created: {directory}")
        except Exception as e:
            print(f"Failed to create {directory}: {e}")

def test_chess_engine():
    """Test the chess engine."""
    print(f"\n{'='*60}")
    print("TESTING CHESS ENGINE")
    print(f"{'='*60}")
    
    try:
        # Test basic chess functionality
        import chess
        board = chess.Board()
        legal_moves = list(board.legal_moves)
        print(f"Chess board created with {len(legal_moves)} legal moves")
        
        # Test engine modules
        sys.path.append(os.path.join(os.path.dirname(__file__), 'chessai'))
        
        from chessai.engine.search_alphabeta import best_move_alphabeta
        from chessai.engine.evaluation import evaluate_position
        
        # Test move generation
        best_move = best_move_alphabeta(board, time_limit_s=0.5)
        if best_move:
            print(f"Engine generated move: {best_move}")
        else:
            print("Engine failed to generate move")
            return False
        
        # Test position evaluation
        value, centipawns = evaluate_position(board)
        print(f"Position evaluation: {value:.3f} ({centipawns} cp)")
        
        return True
        
    except Exception as e:
        print(f"Chess engine test failed: {e}")
        return False

def run_chess_demo():
    """Run the chess demo."""
    print(f"\n{'='*60}")
    print("RUNNING CHESS DEMO")
    print(f"{'='*60}")
    
    # Run the basic test
    if run_command("python run_chess_clean.py", "Running basic chess test"):
        print("Basic chess test completed")
    else:
        print("Basic chess test failed")
    
    # Run the enhanced UI
    if run_command("python chess_ui_enhanced.py", "Running enhanced chess UI"):
        print("Enhanced chess UI completed")
    else:
        print("Enhanced chess UI failed")

def show_usage():
    """Show usage instructions."""
    print(f"\n{'='*80}")
    print("USAGE INSTRUCTIONS")
    print(f"{'='*80}")
    print("The chess engine is now ready! Here's how to use it:")
    print()
    print("1. BASIC TEST:")
    print("   python run_chess_clean.py")
    print()
    print("2. PROFESSIONAL INTERFACE:")
    print("   python chess_engine_clean.py")
    print()
    print("3. ENHANCED UI (RECOMMENDED):")
    print("   python chess_ui_enhanced.py")
    print()
    print("4. ADVANCED UI:")
    print("   python chess_ui_advanced.py")
    print()
    print("5. BOT VS BOT:")
    print("   python bot_vs_bot_clean.py")
    print()
    print("6. EASY LAUNCHER:")
    print("   python launch_chess.py")
    print()
    print("The enhanced UI will show a beautiful chess board with move logging")
    print("and real-time statistics, just like the one shown!")

def main():
    """Main function."""
    print_header()
    
    # Check Python
    if not check_python():
        print("Python version incompatible")
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("Dependency installation failed")
        return False
    
    # Create directories
    create_directories()
    
    # Test chess engine
    if not test_chess_engine():
        print("Chess engine test failed")
        return False
    
    # Run chess demo
    run_chess_demo()
    
    # Show usage
    show_usage()
    
    print(f"\n{'='*80}")
    print("SETUP COMPLETE!")
    print(f"{'='*80}")
    print("The chess engine is now ready to run!")
    print("Use 'python chess_ui_enhanced.py' for the best experience.")
    print("="*80)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\nAll commands completed successfully!")
            print("The chess engine is ready to use!")
        else:
            print("\nSome commands failed. Check the errors above.")
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user.")
    except Exception as e:
        print(f"\nSetup failed: {e}")
        import traceback
        traceback.print_exc()
