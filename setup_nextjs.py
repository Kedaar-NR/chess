#!/usr/bin/env python3
"""
Setup Next.js Chess Engine
Installs dependencies and runs the development server
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Setup and run the Next.js chess engine."""
    print("🚀 Setting up Next.js Chess Engine...")
    
    # Check if we're in the right directory
    if not Path("package.json").exists():
        print("❌ package.json not found. Make sure you're in the project directory.")
        return 1
    
    # Install dependencies
    if not run_command("npm install", "Installing dependencies"):
        print("❌ Failed to install dependencies")
        return 1
    
    print("\n🎉 Setup complete!")
    print("\n📋 Next Steps:")
    print("1. Run: npm run dev")
    print("2. Open: http://localhost:3000")
    print("3. Start playing chess!")
    
    print("\n🔧 Available Commands:")
    print("- npm run dev      # Start development server")
    print("- npm run build    # Build for production")
    print("- npm run start    # Start production server")
    print("- npm run lint     # Run ESLint")
    
    # Ask if user wants to start the dev server
    try:
        start_dev = input("\n🚀 Start development server now? (y/n): ").lower().strip()
        if start_dev in ['y', 'yes']:
            print("\n🌟 Starting development server...")
            print("📱 Open http://localhost:3000 in your browser")
            print("⏹️  Press Ctrl+C to stop the server")
            subprocess.run("npm run dev", shell=True)
        else:
            print("\n💡 Run 'npm run dev' when you're ready to start!")
    except KeyboardInterrupt:
        print("\n👋 Setup complete! Run 'npm run dev' when ready.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
