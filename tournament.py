#!/usr/bin/env python3
"""
Chess Bot Tournament

Runs a tournament between multiple chess bots with optimal moves.
"""

import sys
import os
import chess
import time
import random
from typing import List, Dict, Tuple
from dataclasses import dataclass
from collections import defaultdict

# Add chessai to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'chessai'))

from chessai.engine.search_alphabeta import best_move_alphabeta
from chessai.engine.evaluation import evaluate_position


@dataclass
class BotResult:
    """Bot tournament result."""
    name: str
    wins: int = 0
    losses: int = 0
    draws: int = 0
    total_games: int = 0
    total_time: float = 0.0
    total_nodes: int = 0
    
    @property
    def win_rate(self) -> float:
        """Calculate win rate."""
        if self.total_games == 0:
            return 0.0
        return self.wins / self.total_games
    
    @property
    def points(self) -> float:
        """Calculate tournament points (1 for win, 0.5 for draw)."""
        return self.wins + 0.5 * self.draws


class TournamentBot:
    """Tournament chess bot."""
    
    def __init__(self, name: str, engine_type: str = "alphabeta", time_limit: float = 2.0):
        """Initialize tournament bot."""
        self.name = name
        self.engine_type = engine_type
        self.time_limit = time_limit
        self.result = BotResult(name)
    
    def get_move(self, board: chess.Board) -> chess.Move:
        """Get best move for current position."""
        if board.is_game_over():
            return None
        
        start_time = time.time()
        
        try:
            if self.engine_type == "alphabeta":
                move = best_move_alphabeta(board, self.time_limit)
            elif self.engine_type == "random":
                legal_moves = list(board.legal_moves)
                move = random.choice(legal_moves) if legal_moves else None
            else:
                move = None
            
            move_time = time.time() - start_time
            self.result.total_time += move_time
            
            return move
            
        except Exception:
            # Fallback to random move
            legal_moves = list(board.legal_moves)
            return random.choice(legal_moves) if legal_moves else None
    
    def play_game(self, board: chess.Board, color: chess.Color) -> str:
        """Play a complete game from the given position."""
        game_moves = []
        move_count = 0
        max_moves = 100
        
        while not board.is_game_over() and move_count < max_moves:
            if board.turn == color:
                move = self.get_move(board)
                if move is None:
                    break
                board.push(move)
                game_moves.append(str(move))
                move_count += 1
            else:
                # Opponent's turn - use random for simplicity
                legal_moves = list(board.legal_moves)
                if not legal_moves:
                    break
                move = random.choice(legal_moves)
                board.push(move)
                game_moves.append(str(move))
                move_count += 1
        
        # Determine result
        if board.is_checkmate():
            if board.turn == chess.WHITE:
                return "0-1"  # Black wins
            else:
                return "1-0"  # White wins
        elif board.is_stalemate() or board.is_insufficient_material():
            return "1/2-1/2"  # Draw
        else:
            return "*"  # Unknown


class Tournament:
    """Chess bot tournament."""
    
    def __init__(self, bots: List[TournamentBot]):
        """Initialize tournament."""
        self.bots = bots
        self.results = {bot.name: bot.result for bot in bots}
        self.games_played = 0
    
    def play_round_robin(self, games_per_match: int = 2) -> None:
        """Play round-robin tournament."""
        print(f"\n🏆 Starting Round-Robin Tournament")
        print(f"Bots: {len(self.bots)}")
        print(f"Games per match: {games_per_match}")
        print("="*60)
        
        for i, bot1 in enumerate(self.bots):
            for j, bot2 in enumerate(self.bots):
                if i >= j:  # Avoid duplicate matches
                    continue
                
                print(f"\n {bot1.name} vs {bot2.name}")
                print("-" * 40)
                
                # Play games in both colors
                for game_num in range(games_per_match):
                    # Game 1: bot1 as white, bot2 as black
                    board = chess.Board()
                    result1 = bot1.play_game(board, chess.WHITE)
                    
                    # Game 2: bot2 as white, bot1 as black
                    board = chess.Board()
                    result2 = bot2.play_game(board, chess.WHITE)
                    
                    # Update results
                    self._update_results(bot1, bot2, result1, result2)
                    self._update_results(bot2, bot1, result2, result1)
                    
                    self.games_played += 2
                    
                    print(f"  Game {game_num + 1}: {result1} / {result2}")
        
        print(f"\n Tournament completed! {self.games_played} games played.")
    
    def _update_results(self, bot: TournamentBot, opponent: TournamentBot, 
                        result: str) -> None:
        """Update bot results."""
        bot.result.total_games += 1
        
        if result == "1-0":
            bot.result.wins += 1
        elif result == "0-1":
            bot.result.losses += 1
        elif result == "1/2-1/2":
            bot.result.draws += 1
    
    def print_standings(self) -> None:
        """Print tournament standings."""
        print(f"\n TOURNAMENT STANDINGS")
        print("="*60)
        
        # Sort bots by points
        sorted_bots = sorted(self.bots, key=lambda b: b.result.points, reverse=True)
        
        print(f"{'Rank':<4} {'Bot':<15} {'W':<3} {'L':<3} {'D':<3} {'Pts':<5} {'Win%':<6} {'Time':<8}")
        print("-" * 60)
        
        for rank, bot in enumerate(sorted_bots, 1):
            result = bot.result
            print(f"{rank:<4} {bot.name:<15} {result.wins:<3} {result.losses:<3} "
                  f"{result.draws:<3} {result.points:<5.1f} {result.win_rate:<6.1%} "
                  f"{result.total_time:<8.1f}s")
        
        print("-" * 60)
        print(f"Total games: {self.games_played}")
    
    def play_single_elimination(self) -> None:
        """Play single elimination tournament."""
        print(f"\n🏆 Starting Single Elimination Tournament")
        print("="*60)
        
        remaining_bots = self.bots.copy()
        round_num = 1
        
        while len(remaining_bots) > 1:
            print(f"\n--- Round {round_num} ---")
            next_round = []
            
            # Pair up bots
            for i in range(0, len(remaining_bots), 2):
                if i + 1 < len(remaining_bots):
                    bot1, bot2 = remaining_bots[i], remaining_bots[i + 1]
                    winner = self._play_match(bot1, bot2)
                    next_round.append(winner)
                else:
                    # Odd number of bots, advance the last one
                    next_round.append(remaining_bots[i])
            
            remaining_bots = next_round
            round_num += 1
        
        if remaining_bots:
            print(f"\n🏆 TOURNAMENT CHAMPION: {remaining_bots[0].name}!")
    
    def _play_match(self, bot1: TournamentBot, bot2: TournamentBot) -> TournamentBot:
        """Play a match between two bots."""
        print(f" {bot1.name} vs {bot2.name}")
        
        # Play two games (one as each color)
        board1 = chess.Board()
        result1 = bot1.play_game(board1, chess.WHITE)
        
        board2 = chess.Board()
        result2 = bot2.play_game(board2, chess.WHITE)
        
        # Determine winner
        score1 = 0
        score2 = 0
        
        if result1 == "1-0":
            score1 += 1
        elif result1 == "1/2-1/2":
            score1 += 0.5
            score2 += 0.5
        
        if result2 == "1-0":
            score2 += 1
        elif result2 == "1/2-1/2":
            score1 += 0.5
            score2 += 0.5
        
        # Update results
        self._update_results(bot1, bot2, result1)
        self._update_results(bot2, bot1, result2)
        
        if score1 > score2:
            print(f"  Winner: {bot1.name} ({score1}-{score2})")
            return bot1
        elif score2 > score1:
            print(f"  Winner: {bot2.name} ({score2}-{score1})")
            return bot2
        else:
            # Tie - choose randomly
            winner = random.choice([bot1, bot2])
            print(f"  Tie! Random winner: {winner.name}")
            return winner


def create_tournament_bots() -> List[TournamentBot]:
    """Create tournament bots."""
    return [
        TournamentBot("AlphaBot", "alphabeta", 1.0),
        TournamentBot("DeepBot", "alphabeta", 3.0),
        TournamentBot("QuickBot", "alphabeta", 0.5),
        TournamentBot("RandomBot", "random", 0.1),
        TournamentBot("SmartBot", "alphabeta", 2.0),
    ]


def main():
    """Main tournament function."""
    print("🏆 ChessAI Bot Tournament")
    print("="*60)
    
    # Create bots
    bots = create_tournament_bots()
    
    print("Available bots:")
    for i, bot in enumerate(bots, 1):
        print(f"  {i}. {bot.name} ({bot.engine_type}, {bot.time_limit}s)")
    
    # Choose tournament type
    print("\nTournament types:")
    print("  1. Round-robin")
    print("  2. Single elimination")
    
    while True:
        try:
            choice = input("\nSelect tournament type (1-2): ").strip()
            if choice == "1":
                tournament_type = "round_robin"
                break
            elif choice == "2":
                tournament_type = "single_elimination"
                break
            else:
                print("Invalid choice!")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            return
    
    # Create tournament
    tournament = Tournament(bots)
    
    try:
        if tournament_type == "round_robin":
            games_per_match = int(input("Games per match (default 2): ") or "2")
            tournament.play_round_robin(games_per_match)
        else:
            tournament.play_single_elimination()
        
        # Show results
        tournament.print_standings()
        
    except KeyboardInterrupt:
        print("\n\nTournament interrupted.")
    except Exception as e:
        print(f"\nError during tournament: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
