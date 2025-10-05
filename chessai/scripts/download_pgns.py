"""
Download PGN files from various sources.

Supports downloading from Kaggle datasets and other sources.
"""

import os
import sys
import argparse
import requests
import zipfile
import tarfile
from typing import List, Optional
import kagglehub

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from chessai.utils.logging import setup_logging


def download_kaggle_dataset(dataset_name: str, output_dir: str) -> str:
    """
    Download dataset from Kaggle.
    
    Args:
        dataset_name: Kaggle dataset name
        output_dir: Output directory
        
    Returns:
        Path to downloaded dataset
    """
    print(f"Downloading Kaggle dataset: {dataset_name}")
    
    try:
        # Download dataset
        path = kagglehub.dataset_download(dataset_name)
        print(f"Downloaded to: {path}")
        
        # Copy files to output directory
        import shutil
        if os.path.exists(path):
            for item in os.listdir(path):
                src = os.path.join(path, item)
                dst = os.path.join(output_dir, item)
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
                else:
                    shutil.copytree(src, dst, dirs_exist_ok=True)
        
        return path
        
    except Exception as e:
        print(f"Failed to download dataset {dataset_name}: {e}")
        return None


def download_lichess_games(output_dir: str, year: int = 2023, month: int = 1) -> Optional[str]:
    """
    Download Lichess games for a specific month.
    
    Args:
        output_dir: Output directory
        year: Year
        month: Month
        
    Returns:
        Path to downloaded file
    """
    url = f"https://database.lichess.org/standard/lichess_db_standard_rated_{year:04d}-{month:02d}.pgn.zst"
    filename = f"lichess_{year:04d}_{month:02d}.pgn.zst"
    filepath = os.path.join(output_dir, filename)
    
    print(f"Downloading Lichess games: {year}-{month:02d}")
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Downloaded to: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"Failed to download Lichess games: {e}")
        return None


def download_chess_com_games(output_dir: str, year: int = 2023, month: int = 1) -> Optional[str]:
    """
    Download Chess.com games for a specific month.
    
    Args:
        output_dir: Output directory
        year: Year
        month: Month
        
    Returns:
        Path to downloaded file
    """
    # Note: This is a placeholder - Chess.com doesn't provide direct downloads
    # In practice, you would need to use their API or other methods
    print("Chess.com games download not implemented - use API or other methods")
    return None


def download_ccrl_games(output_dir: str) -> Optional[str]:
    """
    Download CCRL (Computer Chess Rating Lists) games.
    
    Args:
        output_dir: Output directory
        
    Returns:
        Path to downloaded file
    """
    url = "http://ccrl.chessdom.com/ccrl/4040/games.pgn"
    filename = "ccrl_games.pgn"
    filepath = os.path.join(output_dir, filename)
    
    print("Downloading CCRL games...")
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Downloaded to: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"Failed to download CCRL games: {e}")
        return None


def main():
    """Main download function."""
    parser = argparse.ArgumentParser(description='Download chess PGN files')
    parser.add_argument('--output', type=str, default='data/raw',
                       help='Output directory')
    parser.add_argument('--source', type=str, choices=['kaggle', 'lichess', 'chesscom', 'ccrl'],
                       default='kaggle', help='Data source')
    parser.add_argument('--dataset', type=str, default='koryakinp/chess-positions',
                       help='Kaggle dataset name')
    parser.add_argument('--year', type=int, default=2023, help='Year for monthly downloads')
    parser.add_argument('--month', type=int, default=1, help='Month for monthly downloads')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    # Download based on source
    if args.source == 'kaggle':
        download_kaggle_dataset(args.dataset, args.output)
    elif args.source == 'lichess':
        download_lichess_games(args.output, args.year, args.month)
    elif args.source == 'chesscom':
        download_chess_com_games(args.output, args.year, args.month)
    elif args.source == 'ccrl':
        download_ccrl_games(args.output)
    
    print(f"Download completed. Files saved to: {args.output}")


if __name__ == '__main__':
    main()
