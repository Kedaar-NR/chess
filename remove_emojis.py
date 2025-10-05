#!/usr/bin/env python3
"""
Remove All Emojis from Chess Engine Files

This script removes all emojis from all Python files in the chess engine project.
"""

import os
import re
import glob

def remove_emojis_from_file(file_path):
    """Remove emojis from a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Common emojis used in the project
        emoji_patterns = [
            r'[]',
            r'[]',
            r'[]',
            r'[]',
            r'[]',
            r'[]',
            r'[]',
            r'[]',
            r'[]',
            r'[]',
        ]
        
        # Remove all emojis
        for pattern in emoji_patterns:
            content = re.sub(pattern, '', content)
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Processed: {file_path}")
        return True
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to remove emojis from all files."""
    print("Removing emojis from all chess engine files...")
    print("="*60)
    
    # Find all Python files
    python_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    # Also find other text files
    text_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith(('.md', '.txt', '.bat', '.sh')):
                text_files.append(os.path.join(root, file))
    
    all_files = python_files + text_files
    
    print(f"Found {len(all_files)} files to process")
    
    success_count = 0
    for file_path in all_files:
        if remove_emojis_from_file(file_path):
            success_count += 1
    
    print(f"\nProcessed {success_count}/{len(all_files)} files successfully")
    print("All emojis have been removed from the chess engine files!")

if __name__ == "__main__":
    main()
