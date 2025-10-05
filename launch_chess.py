#!/usr/bin/env python3
"""
Chess Engine Launcher

Launch different versions of the chess engine with enhanced UI and move logging.
"""

import sys
import os
import subprocess

def print_header():
    """Print application header."""
    print("="*80)
    print("CHESS ENGINE LAUNCHER")
    print("="*80)
    print("Professional chess engine with enhanced UI and comprehensive move logging")
    print("="*80)

def print_menu():
    """Print main menu."""
    print("\nAvailable Chess Engines:")
    print("1. Basic Engine Test - Simple functionality test")
    print("2. Clean Professional Interface - No emojis, professional look")
    print("3. Enhanced UI - Better board display and move logging")
    print("4. Advanced UI - Comprehensive logging and statistics")
    print("5. Bot vs Bot - Multiple engine types competing")
    print("6. Setup - Install dependencies and test engine")
    print("7. Exit")

def run_script(script_name):
    """Run a Python script."""
    try:
        print(f"\nLaunching {script_name}...")
        print("-" * 50)
        result = subprocess.run([sys.executable, script_name], check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}: {e}")
        return False
    except FileNotFoundError:
        print(f"Script {script_name} not found!")
        return False

def main():
    """Main launcher function."""
    print_header()
    
    while True:
        print_menu()
        
        try:
            choice = input("\nSelect option (1-7): ").strip()
            
            if choice == '1':
                print("\nRunning Basic Engine Test...")
                run_script("run_chess_clean.py")
                
            elif choice == '2':
                print("\nRunning Clean Professional Interface...")
                run_script("chess_engine_clean.py")
                
            elif choice == '3':
                print("\nRunning Enhanced UI...")
                run_script("chess_ui_enhanced.py")
                
            elif choice == '4':
                print("\nRunning Advanced UI...")
                run_script("chess_ui_advanced.py")
                
            elif choice == '5':
                print("\nRunning Bot vs Bot...")
                run_script("bot_vs_bot_clean.py")
                
            elif choice == '6':
                print("\nRunning Setup...")
                run_script("setup_clean.py")
                
            elif choice == '7':
                print("\nGoodbye!")
                break
                
            else:
                print("Invalid choice! Please enter 1-7.")
                
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
