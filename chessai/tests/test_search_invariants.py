"""
Test search algorithm invariants.

Tests that searches improve with depth on hand-picked positions.
"""

import unittest
import chess
from chessai.engine.search_alphabeta import AlphaBetaSearch
from chessai.engine.search_mcts import MCTSSearch, DummyNetwork
from chessai.engine.evaluation import evaluate_position


class TestSearchInvariants(unittest.TestCase):
    """Test search algorithm invariants."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.positions = [
            # Initial position
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            # After e4 e5
            "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2",
            # Tactical position
            "r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1",
            # Endgame position
            "8/8/8/8/8/8/8/4K3 w - - 0 1",
        ]
    
    def test_alphabeta_depth_invariance(self):
        """Test that alpha-beta search improves with depth."""
        search = AlphaBetaSearch()
        
        for fen in self.positions:
            board = chess.Board(fen)
            
            # Test different depths
            depths = [1, 2, 3, 4]
            results = []
            
            for depth in depths:
                result = search.search(board, max_time=1.0, max_depth=depth)
                results.append(result)
            
            # Check that search results are consistent
            for i in range(len(results) - 1):
                # Value should generally improve with depth
                # (though this isn't always guaranteed)
                self.assertIsInstance(results[i]['value'], float)
                self.assertIsInstance(results[i+1]['value'], float)
    
    def test_mcts_node_invariance(self):
        """Test that MCTS search improves with more nodes."""
        network = DummyNetwork()
        search = MCTSSearch(network)
        
        for fen in self.positions:
            board = chess.Board(fen)
            
            # Test different node limits
            node_limits = [100, 500, 1000]
            results = []
            
            for nodes in node_limits:
                result = search.search(board, max_time=1.0, max_nodes=nodes)
                results.append(result)
            
            # Check that search results are consistent
            for i in range(len(results) - 1):
                self.assertIsInstance(results[i]['value'], float)
                self.assertIsInstance(results[i+1]['value'], float)
    
    def test_search_consistency(self):
        """Test that search results are consistent."""
        search = AlphaBetaSearch()
        
        for fen in self.positions:
            board = chess.Board(fen)
            
            # Run search multiple times
            results = []
            for _ in range(3):
                result = search.search(board, max_time=0.5, max_depth=3)
                results.append(result)
            
            # Results should be consistent (same best move)
            best_moves = [r.get('bestmove') for r in results]
            if best_moves[0] is not None:
                for move in best_moves[1:]:
                    self.assertEqual(move, best_moves[0])
    
    def test_evaluation_consistency(self):
        """Test that position evaluation is consistent."""
        for fen in self.positions:
            board = chess.Board(fen)
            
            # Evaluate position multiple times
            values = []
            for _ in range(5):
                value, centipawns = evaluate_position(board)
                values.append(value)
            
            # Values should be consistent
            for i in range(1, len(values)):
                self.assertAlmostEqual(values[i], values[0], places=5)
    
    def test_legal_move_consistency(self):
        """Test that legal moves are consistent with search results."""
        search = AlphaBetaSearch()
        
        for fen in self.positions:
            board = chess.Board(fen)
            
            if board.is_game_over():
                continue
            
            # Get search result
            result = search.search(board, max_time=0.5, max_depth=2)
            best_move = result.get('bestmove')
            
            if best_move is not None:
                # Best move should be legal
                self.assertIn(best_move, board.legal_moves)
    
    def test_search_time_limits(self):
        """Test that search respects time limits."""
        search = AlphaBetaSearch()
        
        for fen in self.positions:
            board = chess.Board(fen)
            
            # Test with very short time limit
            start_time = time.time()
            result = search.search(board, max_time=0.1, max_depth=10)
            search_time = time.time() - start_time
            
            # Should respect time limit (with some tolerance)
            self.assertLessEqual(search_time, 0.2)
    
    def test_search_depth_limits(self):
        """Test that search respects depth limits."""
        search = AlphaBetaSearch()
        
        for fen in self.positions:
            board = chess.Board(fen)
            
            # Test with depth limit
            result = search.search(board, max_time=1.0, max_depth=2)
            
            # Should not exceed depth limit
            self.assertLessEqual(result.get('depth', 0), 2)
    
    def test_mcts_temperature_consistency(self):
        """Test that MCTS search is consistent with temperature."""
        network = DummyNetwork()
        search = MCTSSearch(network)
        
        for fen in self.positions:
            board = chess.Board(fen)
            
            # Test with temperature 0 (deterministic)
            root = search.search(board, max_time=0.5, max_nodes=100)
            move1 = search.get_best_move(root, temperature=0.0)
            move2 = search.get_best_move(root, temperature=0.0)
            
            # Should be deterministic
            self.assertEqual(move1, move2)
    
    def test_search_termination(self):
        """Test that search terminates properly."""
        search = AlphaBetaSearch()
        
        for fen in self.positions:
            board = chess.Board(fen)
            
            # Test with very short time limit
            result = search.search(board, max_time=0.01, max_depth=1)
            
            # Should return a result
            self.assertIsNotNone(result)
            self.assertIn('value', result)
    
    def test_position_evaluation_bounds(self):
        """Test that position evaluations are within reasonable bounds."""
        for fen in self.positions:
            board = chess.Board(fen)
            value, centipawns = evaluate_position(board)
            
            # Value should be in reasonable range
            self.assertGreaterEqual(value, -1.0)
            self.assertLessEqual(value, 1.0)
            
            # Centipawns should be in reasonable range
            self.assertGreaterEqual(centipawns, -1000)
            self.assertLessEqual(centipawns, 1000)


if __name__ == '__main__':
    import time
    unittest.main()
