"""
Test move indexing bijection properties.

Tests that move indexing is stable and correct.
"""

import unittest
import chess
from chessai.engine.move_index import move_index


class TestMoveIndexing(unittest.TestCase):
    """Test move indexing functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.board = chess.Board()
    
    def test_action_space_size(self):
        """Test action space size is positive."""
        size = move_index.action_space_size()
        self.assertGreater(size, 0)
        self.assertIsInstance(size, int)
    
    def test_move_id_stability(self):
        """Test that move IDs are stable across calls."""
        e4 = chess.Move.from_uci("e2e4")
        id1 = move_index.to_id(e4)
        id2 = move_index.to_id(e4)
        self.assertEqual(id1, id2)
    
    def test_bijection_property(self):
        """Test that move to ID and ID to move are inverse operations."""
        # Test with initial position
        legal_moves = list(self.board.legal_moves)
        
        for move in legal_moves:
            # Convert move to ID
            move_id = move_index.to_id(move)
            self.assertGreaterEqual(move_id, 0)
            self.assertLess(move_id, move_index.action_space_size())
            
            # Convert ID back to move
            converted_move = move_index.from_id(move_id, self.board)
            self.assertEqual(converted_move, move)
    
    def test_illegal_move_handling(self):
        """Test handling of illegal moves."""
        # Test with illegal move
        illegal_move = chess.Move.from_uci("e2e5")  # Illegal in initial position
        move_id = move_index.to_id(illegal_move)
        
        # Should return -1 for illegal moves
        self.assertEqual(move_id, -1)
    
    def test_legal_move_mask_consistency(self):
        """Test that legal move mask is consistent with legal moves."""
        legal_moves = list(self.board.legal_moves)
        legal_mask = move_index.get_legal_move_mask(self.board)
        
        # Count legal moves in mask
        legal_count = sum(legal_mask)
        self.assertEqual(legal_count, len(legal_moves))
        
        # Check that all legal moves are marked in mask
        for move in legal_moves:
            move_id = move_index.to_id(move)
            if move_id >= 0:
                self.assertTrue(legal_mask[move_id])
    
    def test_legal_move_ids_consistency(self):
        """Test that legal move IDs are consistent with legal moves."""
        legal_moves = list(self.board.legal_moves)
        legal_ids = move_index.get_legal_move_ids(self.board)
        
        # Should have same number of legal moves
        self.assertEqual(len(legal_ids), len(legal_moves))
        
        # All IDs should be valid
        for move_id in legal_ids:
            self.assertGreaterEqual(move_id, 0)
            self.assertLess(move_id, move_index.action_space_size())
            
            # Should be able to convert back to move
            move = move_index.from_id(move_id, self.board)
            self.assertIsNotNone(move)
            self.assertIn(move, legal_moves)
    
    def test_different_positions(self):
        """Test indexing with different positions."""
        positions = [
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",  # Initial
            "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2",  # After e4 e5
            "r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1",  # Castling position
            "8/8/8/8/8/8/8/4K3 w - - 0 1",  # King only
        ]
        
        for fen in positions:
            board = chess.Board(fen)
            legal_moves = list(board.legal_moves)
            
            # Test bijection for each position
            for move in legal_moves:
                move_id = move_index.to_id(move)
                if move_id >= 0:
                    converted_move = move_index.from_id(move_id, board)
                    self.assertEqual(converted_move, move)
    
    def test_promotion_moves(self):
        """Test indexing with promotion moves."""
        # Set up promotion position
        self.board.set_fen("8/4P3/8/8/8/8/8/8 w - - 0 1")
        
        legal_moves = list(self.board.legal_moves)
        self.assertGreater(len(legal_moves), 0)
        
        # Test bijection for promotion moves
        for move in legal_moves:
            move_id = move_index.to_id(move)
            if move_id >= 0:
                converted_move = move_index.from_id(move_id, self.board)
                self.assertEqual(converted_move, move)
    
    def test_castling_moves(self):
        """Test indexing with castling moves."""
        # Set up castling position
        self.board.set_fen("r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1")
        
        legal_moves = list(self.board.legal_moves)
        
        # Test bijection for castling moves
        for move in legal_moves:
            move_id = move_index.to_id(move)
            if move_id >= 0:
                converted_move = move_index.from_id(move_id, self.board)
                self.assertEqual(converted_move, move)
    
    def test_en_passant_moves(self):
        """Test indexing with en passant moves."""
        # Set up en passant position
        self.board.set_fen("rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 3")
        
        legal_moves = list(self.board.legal_moves)
        
        # Test bijection for en passant moves
        for move in legal_moves:
            move_id = move_index.to_id(move)
            if move_id >= 0:
                converted_move = move_index.from_id(move_id, self.board)
                self.assertEqual(converted_move, move)
    
    def test_edge_cases(self):
        """Test edge cases and error conditions."""
        # Test with empty board
        self.board.set_fen("8/8/8/8/8/8/8/8 w - - 0 1")
        legal_moves = list(self.board.legal_moves)
        self.assertEqual(len(legal_moves), 0)
        
        # Test with checkmate position
        self.board.set_fen("rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 4")
        legal_moves = list(self.board.legal_moves)
        self.assertEqual(len(legal_moves), 0)
        
        # Test with stalemate position
        self.board.set_fen("8/8/8/8/8/8/8/4K3 w - - 0 1")
        legal_moves = list(self.board.legal_moves)
        self.assertEqual(len(legal_moves), 0)


if __name__ == '__main__':
    unittest.main()
