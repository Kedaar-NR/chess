"""
Match report generator.

Analyzes match results and generates reports.
"""

import os
import sys
import argparse
import chess
import chess.pgn
import json
from typing import List, Dict, Any, Optional
import matplotlib.pyplot as plt
import numpy as np

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from chessai.utils.logging import setup_logging


class MatchAnalyzer:
    """Analyzes match results and generates reports."""
    
    def __init__(self, match_file: str):
        """
        Initialize match analyzer.
        
        Args:
            match_file: Path to match results file
        """
        self.match_file = match_file
        self.results = self._load_results()
    
    def _load_results(self) -> Dict[str, Any]:
        """Load match results from file."""
        if self.match_file.endswith('.json'):
            with open(self.match_file, 'r') as f:
                return json.load(f)
        elif self.match_file.endswith('.pgn'):
            return self._load_pgn()
        else:
            raise ValueError("Unsupported file format")
    
    def _load_pgn(self) -> Dict[str, Any]:
        """Load results from PGN file."""
        results = {
            'engine_a': 'Unknown',
            'engine_b': 'Unknown',
            'time_control': 'Unknown',
            'games': [],
            'scores': {'engine_a': 0, 'engine_b': 0, 'draws': 0}
        }
        
        with open(self.match_file, 'r') as f:
            while True:
                game = chess.pgn.read_game(f)
                if game is None:
                    break
                
                # Extract game information
                white = game.headers.get('White', 'Unknown')
                black = game.headers.get('Black', 'Unknown')
                result = game.headers.get('Result', '*')
                
                # Count moves
                move_count = 0
                for move in game.mainline_moves():
                    move_count += 1
                
                # Add to results
                results['games'].append({
                    'game_number': len(results['games']) + 1,
                    'white_engine': white,
                    'black_engine': black,
                    'result': result,
                    'move_count': move_count,
                    'final_fen': game.board().fen()
                })
                
                # Update scores
                if result == '1-0':
                    if white == results['engine_a']:
                        results['scores']['engine_a'] += 1
                    else:
                        results['scores']['engine_b'] += 1
                elif result == '0-1':
                    if black == results['engine_a']:
                        results['scores']['engine_a'] += 1
                    else:
                        results['scores']['engine_b'] += 1
                else:
                    results['scores']['draws'] += 1
        
        return results
    
    def generate_report(self, output_file: str) -> None:
        """Generate match report."""
        report = {
            'match_summary': self._get_match_summary(),
            'game_analysis': self._analyze_games(),
            'statistics': self._calculate_statistics(),
            'recommendations': self._get_recommendations()
        }
        
        # Save report
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Generate plots
        self._generate_plots(output_file.replace('.json', '_plots.png'))
        
        print(f"Report generated: {output_file}")
    
    def _get_match_summary(self) -> Dict[str, Any]:
        """Get match summary."""
        total_games = len(self.results['games'])
        engine_a_wins = self.results['scores']['engine_a']
        engine_b_wins = self.results['scores']['engine_b']
        draws = self.results['scores']['draws']
        
        return {
            'total_games': total_games,
            'engine_a': self.results['engine_a'],
            'engine_b': self.results['engine_b'],
            'engine_a_wins': engine_a_wins,
            'engine_b_wins': engine_b_wins,
            'draws': draws,
            'engine_a_win_rate': engine_a_wins / total_games if total_games > 0 else 0,
            'engine_b_win_rate': engine_b_wins / total_games if total_games > 0 else 0,
            'draw_rate': draws / total_games if total_games > 0 else 0
        }
    
    def _analyze_games(self) -> Dict[str, Any]:
        """Analyze individual games."""
        games = self.results['games']
        
        # Game length analysis
        game_lengths = [game['move_count'] for game in games]
        
        # Result distribution
        results = [game['result'] for game in games]
        result_counts = {}
        for result in results:
            result_counts[result] = result_counts.get(result, 0) + 1
        
        return {
            'average_game_length': np.mean(game_lengths),
            'shortest_game': min(game_lengths),
            'longest_game': max(game_lengths),
            'result_distribution': result_counts
        }
    
    def _calculate_statistics(self) -> Dict[str, Any]:
        """Calculate match statistics."""
        games = self.results['games']
        
        # Calculate win streaks
        engine_a_streak = 0
        engine_b_streak = 0
        max_engine_a_streak = 0
        max_engine_b_streak = 0
        
        for game in games:
            if game['result'] == '1-0':
                if game['white_engine'] == self.results['engine_a']:
                    engine_a_streak += 1
                    engine_b_streak = 0
                    max_engine_a_streak = max(max_engine_a_streak, engine_a_streak)
                else:
                    engine_b_streak += 1
                    engine_a_streak = 0
                    max_engine_b_streak = max(max_engine_b_streak, engine_b_streak)
            elif game['result'] == '0-1':
                if game['black_engine'] == self.results['engine_a']:
                    engine_a_streak += 1
                    engine_b_streak = 0
                    max_engine_a_streak = max(max_engine_a_streak, engine_a_streak)
                else:
                    engine_b_streak += 1
                    engine_a_streak = 0
                    max_engine_b_streak = max(max_engine_b_streak, engine_b_streak)
            else:
                engine_a_streak = 0
                engine_b_streak = 0
        
        return {
            'max_engine_a_streak': max_engine_a_streak,
            'max_engine_b_streak': max_engine_b_streak,
            'total_moves': sum(game['move_count'] for game in games),
            'average_moves_per_game': np.mean([game['move_count'] for game in games])
        }
    
    def _get_recommendations(self) -> List[str]:
        """Get recommendations based on match results."""
        recommendations = []
        
        summary = self._get_match_summary()
        
        if summary['engine_a_win_rate'] > 0.7:
            recommendations.append(f"{self.results['engine_a']} is significantly stronger")
        elif summary['engine_b_win_rate'] > 0.7:
            recommendations.append(f"{self.results['engine_b']} is significantly stronger")
        else:
            recommendations.append("Engines are closely matched")
        
        if summary['draw_rate'] > 0.3:
            recommendations.append("High draw rate - consider longer time controls")
        
        return recommendations
    
    def _generate_plots(self, output_file: str) -> None:
        """Generate match plots."""
        games = self.results['games']
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Game length distribution
        game_lengths = [game['move_count'] for game in games]
        axes[0, 0].hist(game_lengths, bins=20, alpha=0.7)
        axes[0, 0].set_title('Game Length Distribution')
        axes[0, 0].set_xlabel('Moves')
        axes[0, 0].set_ylabel('Frequency')
        
        # Result distribution
        results = [game['result'] for game in games]
        result_counts = {}
        for result in results:
            result_counts[result] = result_counts.get(result, 0) + 1
        
        axes[0, 1].pie(result_counts.values(), labels=result_counts.keys(), autopct='%1.1f%%')
        axes[0, 1].set_title('Result Distribution')
        
        # Win rate over time
        engine_a_wins = 0
        engine_b_wins = 0
        win_rates_a = []
        win_rates_b = []
        
        for i, game in enumerate(games):
            if game['result'] == '1-0':
                if game['white_engine'] == self.results['engine_a']:
                    engine_a_wins += 1
                else:
                    engine_b_wins += 1
            elif game['result'] == '0-1':
                if game['black_engine'] == self.results['engine_a']:
                    engine_a_wins += 1
                else:
                    engine_b_wins += 1
            
            win_rates_a.append(engine_a_wins / (i + 1))
            win_rates_b.append(engine_b_wins / (i + 1))
        
        axes[1, 0].plot(win_rates_a, label=self.results['engine_a'])
        axes[1, 0].plot(win_rates_b, label=self.results['engine_b'])
        axes[1, 0].set_title('Win Rate Over Time')
        axes[1, 0].set_xlabel('Game Number')
        axes[1, 0].set_ylabel('Win Rate')
        axes[1, 0].legend()
        axes[1, 0].grid(True)
        
        # Game length over time
        axes[1, 1].plot(game_lengths)
        axes[1, 1].set_title('Game Length Over Time')
        axes[1, 1].set_xlabel('Game Number')
        axes[1, 1].set_ylabel('Moves')
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()


def main():
    """Main report function."""
    parser = argparse.ArgumentParser(description='Generate match report')
    parser.add_argument('--match', type=str, required=True,
                       help='Match results file (JSON or PGN)')
    parser.add_argument('--out', type=str, required=True,
                       help='Output report file')
    
    args = parser.parse_args()
    
    try:
        analyzer = MatchAnalyzer(args.match)
        analyzer.generate_report(args.out)
    except Exception as e:
        print(f"Report generation failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
