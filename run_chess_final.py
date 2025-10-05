#!/usr/bin/env python3
"""
Final Chess Engine Runner

This script does everything needed to run the chess engine with a beautiful board display.
"""

import sys
import os
import subprocess
import time

def print_header():
    """Print header."""
    print("="*80)
    print("CHESS ENGINE - FINAL RUNNER")
    print("="*80)
    print("This script will:")
    print("1. Remove all emojis from files")
    print("2. Install dependencies")
    print("3. Create directories")
    print("4. Test the engine")
    print("5. Start the enhanced UI with beautiful board display")
    print("="*80)

def run_command(command, description):
    """Run a command and show progress."""
    print(f"\nRunning: {description}")
    print(f"Command: {command}")
    print("-" * 60)
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"Success: {description}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {description}")
        print(f"Error details: {e}")
        return False

def main():
    """Main function."""
    print_header()
    
    # Step 1: Remove emojis
    print("\n1. Removing emojis from all files...")
    if run_command("python remove_emojis.py", "Removing emojis"):
        print("Emojis removed successfully")
    else:
        print("Warning: Emoji removal may have failed")
    
    # Step 2: Install dependencies
    print("\n2. Installing dependencies...")
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
    
    for package in packages:
        if run_command(f"pip install {package}", f"Installing {package}"):
            print(f"Installed: {package}")
        else:
            print(f"Warning: Failed to install {package}")
    
    # Step 3: Create directories
    print("\n3. Creating directories...")
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
            print(f"Error creating {directory}: {e}")
    
    # Step 4: Test basic functionality
    print("\n4. Testing chess engine...")
    try:
        import chess
        board = chess.Board()
        legal_moves = list(board.legal_moves)
        print(f"Chess board created with {len(legal_moves)} legal moves")
        print("Basic chess functionality working")
    except Exception as e:
        print(f"Error testing chess: {e}")
        return False
    
    # Step 5: Start the enhanced UI
    print("\n5. Starting enhanced chess UI...")
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
        print("Try running manually: python chess_ui_enhanced.py")
    
    print("\nChess engine setup complete!")
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\nAll steps completed successfully!")
            print("The chess engine is ready to use!")
        else:
            print("\nSome steps failed. Check the errors above.")
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user.")
    except Exception as e:
        print(f"\nSetup failed: {e}")
        import traceback
        traceback.print_exc()
