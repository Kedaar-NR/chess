"""
Convert PGN files to TFRecord format for training.

Processes chess games and creates training examples.
"""

import os
import sys
import argparse
import chess
import chess.pgn
import tensorflow as tf
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
import random
from tqdm import tqdm

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from chessai.engine.move_index import move_index
from chessai.utils.logging import setup_logging


def board_to_planes(board: chess.Board) -> np.ndarray:
    """
    Convert chess board to feature planes.
    
    Args:
        board: Chess board position
        
    Returns:
        Feature planes array
    """
    # Create feature planes (simplified version)
    # TODO: Implement full AlphaZero-style feature planes
    planes = np.zeros((8, 8, 119), dtype=np.float32)
    
    # Piece planes (6 pieces * 2 colors = 12 planes)
    piece_types = [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]
    plane_idx = 0
    
    for piece_type in piece_types:
        for color in [chess.WHITE, chess.BLACK]:
            for square in chess.SQUARES:
                piece = board.piece_at(square)
                if piece and piece.piece_type == piece_type and piece.color == color:
                    row, col = divmod(square, 8)
                    planes[row, col, plane_idx] = 1.0
            plane_idx += 1
    
    # Side to move plane
    if board.turn == chess.WHITE:
        planes[:, :, 12] = 1.0
    else:
        planes[:, :, 13] = 1.0
    
    # Castling rights
    if board.has_kingside_castling_rights(chess.WHITE):
        planes[:, :, 14] = 1.0
    if board.has_queenside_castling_rights(chess.WHITE):
        planes[:, :, 15] = 1.0
    if board.has_kingside_castling_rights(chess.BLACK):
        planes[:, :, 16] = 1.0
    if board.has_queenside_castling_rights(chess.BLACK):
        planes[:, :, 17] = 1.0
    
    # Move counters and repetition
    planes[:, :, 18] = board.halfmove_clock / 100.0
    planes[:, :, 19] = board.fullmove_number / 100.0
    
    # TODO: Add more feature planes (repetition, en passant, etc.)
    
    return planes


def get_game_result(game: chess.pgn.Game) -> float:
    """
    Get game result from PGN.
    
    Args:
        game: Chess game object
        
    Returns:
        Game result (1.0 for white win, -1.0 for black win, 0.0 for draw)
    """
    result = game.headers.get('Result', '')
    
    if result == '1-0':
        return 1.0  # White wins
    elif result == '0-1':
        return -1.0  # Black wins
    elif result == '1/2-1/2':
        return 0.0  # Draw
    else:
        return 0.0  # Unknown result


def process_game(game: chess.pgn.Game, min_rating: int = 2000) -> List[Dict[str, Any]]:
    """
    Process a single game and extract training examples.
    
    Args:
        game: Chess game object
        min_rating: Minimum rating for games
        
    Returns:
        List of training examples
    """
    # Check game quality
    white_rating = game.headers.get('WhiteElo', '0')
    black_rating = game.headers.get('BlackElo', '0')
    
    try:
        white_rating = int(white_rating)
        black_rating = int(black_rating)
    except ValueError:
        return []
    
    if white_rating < min_rating or black_rating < min_rating:
        return []
    
    # Get game result
    result = get_game_result(game)
    
    # Process game moves
    board = game.board()
    examples = []
    
    for move in game.mainline_moves():
        # Create training example
        planes = board_to_planes(board)
        legal_mask = move_index.get_legal_move_mask(board)
        move_id = move_index.to_id(move)
        
        if move_id >= 0:
            example = {
                'board_planes': planes,
                'policy_index': move_id,
                'value_target': result,
                'legal_mask': legal_mask
            }
            examples.append(example)
        
        board.push(move)
    
    return examples


def write_tfrecord(examples: List[Dict[str, Any]], output_path: str) -> None:
    """
    Write examples to TFRecord file.
    
    Args:
        examples: List of training examples
        output_path: Output file path
    """
    with tf.io.TFRecordWriter(output_path) as writer:
        for example in examples:
            # Serialize features
            board_planes_bytes = tf.io.serialize_tensor(example['board_planes']).numpy()
            legal_mask_bytes = tf.io.serialize_tensor(example['legal_mask']).numpy()
            
            # Create example
            feature = {
                'board_planes': tf.train.Feature(bytes_list=tf.train.BytesList(value=[board_planes_bytes])),
                'policy_index': tf.train.Feature(int64_list=tf.train.Int64List(value=[example['policy_index']])),
                'value_target': tf.train.Feature(float_list=tf.train.FloatList(value=[example['value_target']])),
                'legal_mask': tf.train.Feature(bytes_list=tf.train.BytesList(value=[legal_mask_bytes]))
            }
            
            example_proto = tf.train.Example(features=tf.train.Features(feature=feature))
            writer.write(example_proto.SerializeToString())


def process_pgn_file(pgn_path: str, output_dir: str, min_rating: int = 2000, 
                    max_games: Optional[int] = None) -> None:
    """
    Process a PGN file and create TFRecords.
    
    Args:
        pgn_path: Path to PGN file
        output_dir: Output directory
        min_rating: Minimum rating for games
        max_games: Maximum number of games to process
    """
    print(f"Processing PGN file: {pgn_path}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Process games
    examples = []
    game_count = 0
    
    with open(pgn_path, 'r') as f:
        while True:
            game = chess.pgn.read_game(f)
            if game is None:
                break
            
            # Process game
            game_examples = process_game(game, min_rating)
            examples.extend(game_examples)
            game_count += 1
            
            if max_games and game_count >= max_games:
                break
            
            if game_count % 1000 == 0:
                print(f"Processed {game_count} games, {len(examples)} examples")
    
    print(f"Total games processed: {game_count}")
    print(f"Total examples: {len(examples)}")
    
    # Write TFRecords
    if examples:
        # Split into train/val/test
        random.shuffle(examples)
        
        train_ratio = 0.8
        val_ratio = 0.1
        test_ratio = 0.1
        
        train_end = int(len(examples) * train_ratio)
        val_end = train_end + int(len(examples) * val_ratio)
        
        train_examples = examples[:train_end]
        val_examples = examples[train_end:val_end]
        test_examples = examples[val_end:]
        
        # Write splits
        write_tfrecord(train_examples, os.path.join(output_dir, 'train.tfrecord'))
        write_tfrecord(val_examples, os.path.join(output_dir, 'val.tfrecord'))
        write_tfrecord(test_examples, os.path.join(output_dir, 'test.tfrecord'))
        
        print(f"Written TFRecords to {output_dir}")
        print(f"Train examples: {len(train_examples)}")
        print(f"Val examples: {len(val_examples)}")
        print(f"Test examples: {len(test_examples)}")


def main():
    """Main conversion function."""
    parser = argparse.ArgumentParser(description='Convert PGN files to TFRecords')
    parser.add_argument('--input', type=str, required=True,
                       help='Input PGN file or directory')
    parser.add_argument('--output', type=str, required=True,
                       help='Output directory for TFRecords')
    parser.add_argument('--min_rating', type=int, default=2000,
                       help='Minimum rating for games')
    parser.add_argument('--max_games', type=int, default=None,
                       help='Maximum number of games to process')
    
    args = parser.parse_args()
    
    # Process input
    if os.path.isfile(args.input):
        # Single file
        process_pgn_file(args.input, args.output, args.min_rating, args.max_games)
    elif os.path.isdir(args.input):
        # Directory of files
        pgn_files = [f for f in os.listdir(args.input) if f.endswith('.pgn')]
        for pgn_file in pgn_files:
            pgn_path = os.path.join(args.input, pgn_file)
            output_subdir = os.path.join(args.output, os.path.splitext(pgn_file)[0])
            process_pgn_file(pgn_path, output_subdir, args.min_rating, args.max_games)
    else:
        print(f"Input path not found: {args.input}")
        sys.exit(1)


if __name__ == '__main__':
    main()
