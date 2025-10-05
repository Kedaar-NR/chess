#!/usr/bin/env python3
"""
Start Chess Engine - One Command

This script does everything needed to start the chess engine and display a beautiful board.
"""

import sys
import os
import subprocess
import time

def main():
    """Main function - runs everything needed."""
    print("="*80)
    print("CHESS ENGINE - ONE COMMAND START")
    print("="*80)
    print("This will install dependencies, test the engine, and start the game!")
    print("="*80)
    
    # Step 1: Install dependencies
    print("\n1. Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "python-chess", "tensorflow", "numpy", "pandas", "scikit-learn", "fastapi", "uvicorn", "typer", "pyyaml", "orjson", "tensorboard", "matplotlib", "rich"], check=True)
        print("Dependencies installed")
    except:
        print("Some dependencies may not have installed - continuing anyway")
    
    # Step 2: Create directories
    print("\n2. Creating directories...")
    directories = ["data/raw", "data/tfrecords", "data/selfplay", "runs/supervised", "runs/rl", "logs"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    print("Directories created")
    
    # Step 3: Test basic functionality
    print("\n3. Testing chess engine...")
    try:
        import chess
        board = chess.Board()
        print(f"Chess board created with {len(list(board.legal_moves))} legal moves")
    except Exception as e:
        print(f"Chess test failed: {e}")
        return
    
    # Step 4: Start the enhanced UI
    print("\n4. Starting enhanced chess UI...")
    print("="*80)
    print("CHESS ENGINE READY!")
    print("="*80)
    print("The enhanced UI will show a beautiful chess board with move logging")
    print("and real-time statistics, just like the one shown!")
    print("="*80)
    
    try:
        # Run the enhanced UI
        subprocess.run([sys.executable, "chess_ui_enhanced.py"], check=True)
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Goodbye!")
    except Exception as e:
        print(f"\nError running chess UI: {e}")
        print("Try running: python chess_ui_enhanced.py")

if __name__ == "__main__":
    main()
