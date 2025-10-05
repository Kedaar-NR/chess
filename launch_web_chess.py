#!/usr/bin/env python3
"""
Launch Web Chess Interface
Opens the chess web interface in the default browser
"""

import webbrowser
import os
import sys
from pathlib import Path

def main():
    """Launch the web chess interface."""
    print("Launching Web Chess Interface...")
    
    # Get the directory of this script
    script_dir = Path(__file__).parent.absolute()
    
    # Path to the HTML file
    html_file = script_dir / "advanced_chess.html"
    
    if not html_file.exists():
        print(f"Error: {html_file} not found!")
        return 1
    
    # Convert to file URL
    file_url = f"file://{html_file}"
    
    print(f"Opening: {file_url}")
    
    # Open in default browser
    webbrowser.open(file_url)
    
    print("Chess interface opened in your browser!")
    print("\nFeatures:")
    print("- Click pieces to move them")
    print("- AI vs AI mode available")
    print("- Move logging and timers")
    print("- Beautiful visual board")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
