"""
NNUE (Efficiently Updatable Neural Network) head for chess evaluation.

Simplified NNUE implementation for experimentation.
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from typing import Tuple, List
import numpy as np
import chess


class NNUEHead:
    """NNUE evaluation head for chess positions."""
    
    def __init__(self, feature_size: int = 256, hidden_size: int = 32):
        """
        Initialize NNUE head.
        
        Args:
            feature_size: Size of input features
            hidden_size: Size of hidden layer
        """
        self.feature_size = feature_size
        self.hidden_size = hidden_size
        self.model = self._build_model()
    
    def _build_model(self) -> keras.Model:
        """Build the NNUE model."""
        inputs = layers.Input(shape=(self.feature_size,), name='features')
        
        # Hidden layer
        hidden = layers.Dense(self.hidden_size, activation='relu')(inputs)
        hidden = layers.Dropout(0.1)(hidden)
        
        # Output layer
        output = layers.Dense(1, activation='tanh', name='evaluation')(hidden)
        
        model = keras.Model(inputs=inputs, outputs=output)
        
        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def extract_features(self, board: chess.Board) -> np.ndarray:
        """
        Extract features from chess position.
        
        Args:
            board: Chess position
            
        Returns:
            Feature vector
        """
        features = np.zeros(self.feature_size)
        
        # Material balance
        piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0  # King value handled separately
        }
        
        material_balance = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is not None:
                value = piece_values.get(piece.piece_type, 0)
                if piece.color == chess.WHITE:
                    material_balance += value
                else:
                    material_balance -= value
        
        features[0] = material_balance / 100.0  # Normalize
        
        # Piece positions (simplified)
        piece_squares = {
            'white_pawns': [],
            'black_pawns': [],
            'white_pieces': [],
            'black_pieces': []
        }
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is not None:
                if piece.piece_type == chess.PAWN:
                    if piece.color == chess.WHITE:
                        piece_squares['white_pawns'].append(square)
                    else:
                        piece_squares['black_pawns'].append(square)
                else:
                    if piece.color == chess.WHITE:
                        piece_squares['white_pieces'].append(square)
                    else:
                        piece_squares['black_pieces'].append(square)
        
        # Center control
        center_squares = [chess.D4, chess.D5, chess.E4, chess.E5]
        center_control = 0
        for square in center_squares:
            if board.piece_at(square):
                piece = board.piece_at(square)
                if piece.color == chess.WHITE:
                    center_control += 1
                else:
                    center_control -= 1
        
        features[1] = center_control / 4.0
        
        # King safety (simplified)
        white_king_square = board.king(chess.WHITE)
        black_king_square = board.king(chess.BLACK)
        
        if white_king_square is not None:
            white_king_rank = chess.square_rank(white_king_square)
            features[2] = white_king_rank / 7.0
        
        if black_king_square is not None:
            black_king_rank = chess.square_rank(black_king_square)
            features[3] = black_king_rank / 7.0
        
        # Castling rights
        features[4] = 1.0 if board.has_kingside_castling_rights(chess.WHITE) else 0.0
        features[5] = 1.0 if board.has_queenside_castling_rights(chess.WHITE) else 0.0
        features[6] = 1.0 if board.has_kingside_castling_rights(chess.BLACK) else 0.0
        features[7] = 1.0 if board.has_queenside_castling_rights(chess.BLACK) else 0.0
        
        # Side to move
        features[8] = 1.0 if board.turn == chess.WHITE else -1.0
        
        # Fill remaining features with random values (placeholder)
        for i in range(9, self.feature_size):
            features[i] = np.random.normal(0, 0.1)
        
        return features
    
    def predict(self, board: chess.Board) -> float:
        """
        Predict evaluation for a chess position.
        
        Args:
            board: Chess position
            
        Returns:
            Evaluation score in range [-1, 1]
        """
        features = self.extract_features(board)
        features = features.reshape(1, -1)
        
        prediction = self.model.predict(features, verbose=0)
        return float(prediction[0, 0])
    
    def predict_batch(self, boards: List[chess.Board]) -> np.ndarray:
        """
        Predict evaluation for a batch of positions.
        
        Args:
            boards: List of chess positions
            
        Returns:
            Array of evaluations
        """
        features = np.array([self.extract_features(board) for board in boards])
        predictions = self.model.predict(features, verbose=0)
        return predictions.flatten()
    
    def train(self, boards: List[chess.Board], targets: List[float], 
              epochs: int = 10, batch_size: int = 32) -> None:
        """
        Train the NNUE head.
        
        Args:
            boards: Training positions
            targets: Target evaluations
            epochs: Number of training epochs
            batch_size: Batch size
        """
        features = np.array([self.extract_features(board) for board in boards])
        targets = np.array(targets)
        
        self.model.fit(
            features, targets,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.1,
            verbose=1
        )
    
    def save(self, filepath: str) -> None:
        """Save the model to file."""
        self.model.save(filepath)
    
    def load(self, filepath: str) -> None:
        """Load the model from file."""
        self.model = keras.models.load_model(filepath)


def create_nnue_head(feature_size: int = 256, hidden_size: int = 32) -> NNUEHead:
    """
    Create a new NNUE head.
    
    Args:
        feature_size: Size of input features
        hidden_size: Size of hidden layer
        
    Returns:
        New NNUE head instance
    """
    return NNUEHead(feature_size, hidden_size)