#!/usr/bin/env python3
"""
Chess Engine Setup Script

Installs dependencies and sets up the chess engine.
"""

import sys
import os
import subprocess
import importlib


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print(" Python 3.8+ required. Current version:", sys.version)
        return False
    print(f" Python version: {sys.version}")
    return True


def install_package(package_name, import_name=None):
    """Install a package using pip."""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        print(f"{package_name} already installed")
        return True
    except ImportError:
        print(f"Installing {package_name}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            print(f"{package_name} installed successfully")
            return True
        except subprocess.CalledProcessError:
            print(f"Failed to install {package_name}")
            return False


def install_requirements():
    """Install required packages."""
    print("\nInstalling required packages...")
    
    required_packages = [
        ("python-chess", "chess"),
        ("tensorflow", "tensorflow"),
        ("numpy", "numpy"),
        ("pandas", "pandas"),
        ("scikit-learn", "sklearn"),
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("typer", "typer"),
        ("pyyaml", "yaml"),
        ("orjson", "orjson"),
        ("tensorboard", "tensorboard"),
        ("matplotlib", "matplotlib"),
        ("rich", "rich"),
    ]
    
    success_count = 0
    for package, import_name in required_packages:
        if install_package(package, import_name):
            success_count += 1
    
    print(f"\nInstallation summary: {success_count}/{len(required_packages)} packages installed")
    return success_count == len(required_packages)


def test_chess_engine():
    """Test if chess engine works."""
    print("\nTesting chess engine...")
    
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


def create_directories():
    """Create necessary directories."""
    print("\nCreating directories...")
    
    directories = [
        "data/raw",
        "data/tfrecords",
        "data/selfplay",
        "runs/supervised",
        "runs/rl",
        "logs",
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")


def main():
    """Main setup function."""
    print("Chess Engine Setup")
    print("="*60)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Create directories
    create_directories()
    
    # Install packages
    if not install_requirements():
        print("Some packages failed to install. Please check the errors above.")
        return False
    
    # Test chess engine
    if not test_chess_engine():
        print("Chess engine test failed. Please check the errors above.")
        return False
    
    print("\nSetup completed successfully!")
    print("\nYou can now run:")
    print("  python run_chess.py           # Basic chess engine test")
    print("  python chess_com_style.py    # Chess.com style interface")
    print("  python bot_vs_bot.py        # Bot vs Bot games")
    print("  python tournament.py         # Tournament mode")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nSetup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
