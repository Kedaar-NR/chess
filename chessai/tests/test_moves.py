"""
Test chess move legality and round trips.

Tests using python-chess library.
"""

import unittest
import chess
from chessai.engine.move_index import move_index


class TestMoves(unittest.TestCase):
    """Test chess move functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.board = chess.Board()
    
    def test_initial_position(self):
        """Test initial position."""
        self.assertEqual(self.board.fen(), 
                        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    
    def test_legal_moves(self):
        """Test legal move generation."""
        legal_moves = list(self.board.legal_moves)
        self.assertEqual(len(legal_moves), 20)  # 20 legal moves in initial position
    
    def test_move_legality(self):
        """Test move legality checking."""
        # Test legal move
        e4 = chess.Move.from_uci("e2e4")
        self.assertTrue(e4 in self.board.legal_moves)
        
        # Test illegal move
        illegal_move = chess.Move.from_uci("e2e5")
        self.assertFalse(illegal_move in self.board.legal_moves)
    
    def test_move_execution(self):
        """Test move execution."""
        # Make a move
        e4 = chess.Move.from_uci("e2e4")
        self.board.push(e4)
        
        # Check position changed
        self.assertNotEqual(self.board.fen(), 
                           "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        
        # Check turn changed
        self.assertEqual(self.board.turn, chess.BLACK)
    
    def test_move_undo(self):
        """Test move undo."""
        # Make a move
        e4 = chess.Move.from_uci("e2e4")
        self.board.push(e4)
        
        # Undo move
        self.board.pop()
        
        # Check position restored
        self.assertEqual(self.board.fen(), 
                        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    
    def test_castling(self):
        """Test castling moves."""
        # Set up castling position
        self.board.set_fen("r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1")
        
        # Test kingside castling
        kingside_castle = chess.Move.from_uci("e1g1")
        self.assertTrue(kingside_castle in self.board.legal_moves)
        
        # Test queenside castling
        queenside_castle = chess.Move.from_uci("e1c1")
        self.assertTrue(queenside_castle in self.board.legal_moves)
    
    def test_en_passant(self):
        """Test en passant moves."""
        # Set up en passant position
        self.board.set_fen("rnbqkbnr/ppp1pppp/8/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 3")
        
        # Test en passant capture
        en_passant = chess.Move.from_uci("e5d6")
        self.assertTrue(en_passant in self.board.legal_moves)
    
    def test_promotion(self):
        """Test pawn promotion."""
        # Set up promotion position
        self.board.set_fen("8/4P3/8/8/8/8/8/8 w - - 0 1")
        
        # Test promotion moves
        queen_promotion = chess.Move.from_uci("e7e8q")
        self.assertTrue(queen_promotion in self.board.legal_moves)
        
        rook_promotion = chess.Move.from_uci("e7e8r")
        self.assertTrue(rook_promotion in self.board.legal_moves)
    
    def test_check_detection(self):
        """Test check detection."""
        # Set up check position
        self.board.set_fen("rnbqkbnr/pppp1ppp/8/4p3/6P1/5P2/PPPPP2P/RNBQKBNR b KQkq - 0 3")
        
        # Make move that puts king in check
        self.board.push(chess.Move.from_uci("e5e4"))
        
        # Check if position is in check
        self.assertTrue(self.board.is_check())
    
    def test_checkmate_detection(self):
        """Test checkmate detection."""
        # Set up checkmate position
        self.board.set_fen("rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 4")
        
        # Check if position is checkmate
        self.assertTrue(self.board.is_checkmate())
    
    def test_stalemate_detection(self):
        """Test stalemate detection."""
        # Set up stalemate position
        self.board.set_fen("8/8/8/8/8/8/8/4K3 w - - 0 1")
        
        # Check if position is stalemate
        self.assertTrue(self.board.is_stalemate())


class TestMoveIndex(unittest.TestCase):
    """Test move indexing functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.board = chess.Board()
    
    def test_move_to_id(self):
        """Test move to ID conversion."""
        # Test basic move
        e4 = chess.Move.from_uci("e2e4")
        move_id = move_index.to_id(e4)
        self.assertIsInstance(move_id, int)
        self.assertGreaterEqual(move_id, 0)
    
    def test_id_to_move(self):
        """Test ID to move conversion."""
        # Test basic move
        e4 = chess.Move.from_uci("e2e4")
        move_id = move_index.to_id(e4)
        
        # Convert back to move
        converted_move = move_index.from_id(move_id, self.board)
        self.assertEqual(converted_move, e4)
    
    def test_legal_move_mask(self):
        """Test legal move mask generation."""
        mask = move_index.get_legal_move_mask(self.board)
        self.assertEqual(len(mask), move_index.action_space_size())
        self.assertTrue(any(mask))  # Should have some legal moves
    
    def test_legal_move_ids(self):
        """Test legal move ID generation."""
        legal_ids = move_index.get_legal_move_ids(self.board)
        self.assertGreater(len(legal_ids), 0)
        self.assertTrue(all(isinstance(id, int) for id in legal_ids))


if __name__ == '__main__':
    unittest.main()
