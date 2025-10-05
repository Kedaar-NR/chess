"""
Elo rating system for chess engine evaluation.

BayesElo style rating updates for model gating.
"""

import math
from typing import List, Tuple, Dict, Any, Optional
import numpy as np


class EloRating:
    """Elo rating system implementation."""
    
    def __init__(self, initial_rating: float = 1500.0, k_factor: float = 32.0):
        """
        Initialize Elo rating system.
        
        Args:
            initial_rating: Initial rating for new players
            k_factor: K-factor for rating updates
        """
        self.initial_rating = initial_rating
        self.k_factor = k_factor
        self.ratings: Dict[str, float] = {}
        self.games_played: Dict[str, int] = {}
    
    def get_rating(self, player: str) -> float:
        """Get current rating for a player."""
        return self.ratings.get(player, self.initial_rating)
    
    def get_games_played(self, player: str) -> int:
        """Get number of games played by a player."""
        return self.games_played.get(player, 0)
    
    def expected_score(self, rating_a: float, rating_b: float) -> float:
        """
        Calculate expected score for player A against player B.
        
        Args:
            rating_a: Rating of player A
            rating_b: Rating of player B
            
        Returns:
            Expected score for player A (0-1)
        """
        return 1.0 / (1.0 + 10.0 ** ((rating_b - rating_a) / 400.0))
    
    def update_ratings(self, player_a: str, player_b: str, 
                      score_a: float, score_b: Optional[float] = None) -> None:
        """
        Update ratings after a game.
        
        Args:
            player_a: First player
            player_b: Second player
            score_a: Score for player A (1.0 for win, 0.5 for draw, 0.0 for loss)
            score_b: Score for player B (optional, defaults to 1.0 - score_a)
        """
        if score_b is None:
            score_b = 1.0 - score_a
        
        # Get current ratings
        rating_a = self.get_rating(player_a)
        rating_b = self.get_rating(player_b)
        
        # Calculate expected scores
        expected_a = self.expected_score(rating_a, rating_b)
        expected_b = self.expected_score(rating_b, rating_a)
        
        # Update ratings
        new_rating_a = rating_a + self.k_factor * (score_a - expected_a)
        new_rating_b = rating_b + self.k_factor * (score_b - expected_b)
        
        # Store updated ratings
        self.ratings[player_a] = new_rating_a
        self.ratings[player_b] = new_rating_b
        
        # Update games played
        self.games_played[player_a] = self.games_played.get(player_a, 0) + 1
        self.games_played[player_b] = self.games_played.get(player_b, 0) + 1
    
    def get_rating_difference(self, player_a: str, player_b: str) -> float:
        """Get rating difference between two players."""
        return self.get_rating(player_a) - self.get_rating(player_b)
    
    def get_win_probability(self, player_a: str, player_b: str) -> float:
        """Get win probability for player A against player B."""
        rating_a = self.get_rating(player_a)
        rating_b = self.get_rating(player_b)
        return self.expected_score(rating_a, rating_b)


class BayesElo:
    """BayesElo rating system implementation."""
    
    def __init__(self, prior_strength: float = 1.0):
        """
        Initialize BayesElo system.
        
        Args:
            prior_strength: Strength of prior distribution
        """
        self.prior_strength = prior_strength
        self.ratings: Dict[str, float] = {}
        self.uncertainties: Dict[str, float] = {}
        self.games_played: Dict[str, int] = {}
    
    def get_rating(self, player: str) -> Tuple[float, float]:
        """
        Get rating and uncertainty for a player.
        
        Args:
            player: Player name
            
        Returns:
            Tuple of (rating, uncertainty)
        """
        rating = self.ratings.get(player, 0.0)
        uncertainty = self.uncertainties.get(player, 1.0)
        return rating, uncertainty
    
    def update_ratings(self, player_a: str, player_b: str, 
                      score_a: float, score_b: Optional[float] = None) -> None:
        """
        Update ratings using Bayesian inference.
        
        Args:
            player_a: First player
            player_b: Second player
            score_a: Score for player A
            score_b: Score for player B (optional)
        """
        if score_b is None:
            score_b = 1.0 - score_a
        
        # Get current ratings and uncertainties
        rating_a, unc_a = self.get_rating(player_a)
        rating_b, unc_b = self.get_rating(player_b)
        
        # Calculate likelihood
        rating_diff = rating_a - rating_b
        expected_score = 1.0 / (1.0 + math.exp(-rating_diff))
        
        # Update ratings (simplified Bayesian update)
        # This is a simplified version - full BayesElo is more complex
        learning_rate = 0.1
        
        new_rating_a = rating_a + learning_rate * (score_a - expected_score)
        new_rating_b = rating_b + learning_rate * (score_b - (1.0 - expected_score))
        
        # Update uncertainties (decrease with more games)
        new_unc_a = max(0.1, unc_a * 0.99)
        new_unc_b = max(0.1, unc_b * 0.99)
        
        # Store updated values
        self.ratings[player_a] = new_rating_a
        self.ratings[player_b] = new_rating_b
        self.uncertainties[player_a] = new_unc_a
        self.uncertainties[player_b] = new_unc_b
        
        # Update games played
        self.games_played[player_a] = self.games_played.get(player_a, 0) + 1
        self.games_played[player_b] = self.games_played.get(player_b, 0) + 1
    
    def get_win_probability(self, player_a: str, player_b: str) -> float:
        """Get win probability for player A against player B."""
        rating_a, unc_a = self.get_rating(player_a)
        rating_b, unc_b = self.get_rating(player_b)
        
        # Account for uncertainty in win probability
        rating_diff = rating_a - rating_b
        combined_uncertainty = math.sqrt(unc_a**2 + unc_b**2)
        
        # Use normal distribution for win probability
        z_score = rating_diff / math.sqrt(2 * combined_uncertainty**2 + 1)
        return 0.5 * (1 + math.erf(z_score / math.sqrt(2)))


def update_ratings(ratings: Dict[str, float], player_a: str, player_b: str,
                   score_a: float, k_factor: float = 32.0) -> Dict[str, float]:
    """
    Update ratings for two players.
    
    Args:
        ratings: Current ratings dictionary
        player_a: First player
        player_b: Second player
        score_a: Score for player A (1.0 for win, 0.5 for draw, 0.0 for loss)
        k_factor: K-factor for rating updates
        
    Returns:
        Updated ratings dictionary
    """
    # Get current ratings
    rating_a = ratings.get(player_a, 1500.0)
    rating_b = ratings.get(player_b, 1500.0)
    
    # Calculate expected scores
    expected_a = 1.0 / (1.0 + 10.0 ** ((rating_b - rating_a) / 400.0))
    expected_b = 1.0 - expected_a
    
    # Update ratings
    new_rating_a = rating_a + k_factor * (score_a - expected_a)
    new_rating_b = rating_b + k_factor * ((1.0 - score_a) - expected_b)
    
    # Return updated ratings
    updated_ratings = ratings.copy()
    updated_ratings[player_a] = new_rating_a
    updated_ratings[player_b] = new_rating_b
    
    return updated_ratings


def get_rating(player: str, ratings: Dict[str, float]) -> float:
    """Get rating for a player."""
    return ratings.get(player, 1500.0)


def calculate_rating_difference(rating_a: float, rating_b: float) -> float:
    """Calculate rating difference between two players."""
    return rating_a - rating_b


def rating_to_win_probability(rating_diff: float) -> float:
    """Convert rating difference to win probability."""
    return 1.0 / (1.0 + 10.0 ** (-rating_diff / 400.0))


def win_probability_to_rating_diff(win_prob: float) -> float:
    """Convert win probability to rating difference."""
    if win_prob <= 0:
        return -400.0
    elif win_prob >= 1:
        return 400.0
    else:
        return 400.0 * math.log10(win_prob / (1.0 - win_prob))
