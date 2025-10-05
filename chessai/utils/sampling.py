"""
Sampling utilities for chess AI.

Dirichlet noise and temperature sampling for exploration.
"""

import numpy as np
from typing import List, Tuple, Optional
import random


def add_dirichlet_noise(priors: np.ndarray, alpha: float = 0.3, 
                       noise_weight: float = 0.25) -> np.ndarray:
    """
    Add Dirichlet noise to prior probabilities.
    
    Args:
        priors: Prior probability vector
        alpha: Dirichlet concentration parameter
        noise_weight: Weight for noise (0-1)
        
    Returns:
        Noisy priors
    """
    noise = np.random.dirichlet([alpha] * len(priors))
    return (1 - noise_weight) * priors + noise_weight * noise


def temperature_sampling(logits: np.ndarray, temperature: float = 1.0) -> np.ndarray:
    """
    Apply temperature scaling to logits.
    
    Args:
        logits: Raw logits
        temperature: Temperature parameter
        
    Returns:
        Scaled probabilities
    """
    if temperature == 0:
        # Greedy selection
        probs = np.zeros_like(logits)
        probs[np.argmax(logits)] = 1.0
        return probs
    
    scaled_logits = logits / temperature
    exp_logits = np.exp(scaled_logits - np.max(scaled_logits))
    return exp_logits / np.sum(exp_logits)


def sample_from_probs(probs: np.ndarray, legal_mask: Optional[np.ndarray] = None) -> int:
    """
    Sample an index from probability distribution.
    
    Args:
        probs: Probability distribution
        legal_mask: Legal move mask (optional)
        
    Returns:
        Sampled index
    """
    if legal_mask is not None:
        # Mask illegal moves
        masked_probs = probs * legal_mask
        if np.sum(masked_probs) == 0:
            # All moves illegal, return random legal move
            legal_indices = np.where(legal_mask)[0]
            return np.random.choice(legal_indices)
        masked_probs = masked_probs / np.sum(masked_probs)
        probs = masked_probs
    
    return np.random.choice(len(probs), p=probs)


def softmax(logits: np.ndarray) -> np.ndarray:
    """
    Compute softmax probabilities.
    
    Args:
        logits: Raw logits
        
    Returns:
        Softmax probabilities
    """
    exp_logits = np.exp(logits - np.max(logits))
    return exp_logits / np.sum(exp_logits)


def gumbel_noise(shape: Tuple[int, ...]) -> np.ndarray:
    """
    Generate Gumbel noise for Gumbel-Max sampling.
    
    Args:
        shape: Shape of noise array
        
    Returns:
        Gumbel noise
    """
    uniform = np.random.uniform(0, 1, shape)
    return -np.log(-np.log(uniform))


def gumbel_max_sampling(logits: np.ndarray, legal_mask: Optional[np.ndarray] = None) -> int:
    """
    Sample using Gumbel-Max trick.
    
    Args:
        logits: Raw logits
        legal_mask: Legal move mask (optional)
        
    Returns:
        Sampled index
    """
    if legal_mask is not None:
        # Mask illegal moves
        masked_logits = np.where(legal_mask, logits, -np.inf)
    else:
        masked_logits = logits
    
    noise = gumbel_noise(logits.shape)
    return np.argmax(masked_logits + noise)


def epsilon_greedy(probs: np.ndarray, epsilon: float = 0.1, 
                   legal_mask: Optional[np.ndarray] = None) -> int:
    """
    Epsilon-greedy sampling.
    
    Args:
        probs: Probability distribution
        epsilon: Exploration rate
        legal_mask: Legal move mask (optional)
        
    Returns:
        Sampled index
    """
    if random.random() < epsilon:
        # Random exploration
        if legal_mask is not None:
            legal_indices = np.where(legal_mask)[0]
            return np.random.choice(legal_indices)
        else:
            return np.random.choice(len(probs))
    else:
        # Greedy exploitation
        if legal_mask is not None:
            masked_probs = probs * legal_mask
            if np.sum(masked_probs) == 0:
                legal_indices = np.where(legal_mask)[0]
                return np.random.choice(legal_indices)
            return np.argmax(masked_probs)
        else:
            return np.argmax(probs)


def boltzmann_sampling(logits: np.ndarray, temperature: float = 1.0,
                      legal_mask: Optional[np.ndarray] = None) -> int:
    """
    Boltzmann (softmax) sampling with temperature.
    
    Args:
        logits: Raw logits
        temperature: Temperature parameter
        legal_mask: Legal move mask (optional)
        
    Returns:
        Sampled index
    """
    probs = temperature_sampling(logits, temperature)
    return sample_from_probs(probs, legal_mask)


def top_k_sampling(probs: np.ndarray, k: int, 
                   legal_mask: Optional[np.ndarray] = None) -> int:
    """
    Sample from top-k moves.
    
    Args:
        probs: Probability distribution
        k: Number of top moves to consider
        legal_mask: Legal move mask (optional)
        
    Returns:
        Sampled index
    """
    if legal_mask is not None:
        masked_probs = probs * legal_mask
        if np.sum(masked_probs) == 0:
            legal_indices = np.where(legal_mask)[0]
            return np.random.choice(legal_indices)
        probs = masked_probs
    
    # Get top-k indices
    top_k_indices = np.argsort(probs)[-k:]
    top_k_probs = probs[top_k_indices]
    top_k_probs = top_k_probs / np.sum(top_k_probs)
    
    # Sample from top-k
    chosen_idx = np.random.choice(len(top_k_indices), p=top_k_probs)
    return top_k_indices[chosen_idx]


def nucleus_sampling(probs: np.ndarray, p: float = 0.9,
                    legal_mask: Optional[np.ndarray] = None) -> int:
    """
    Nucleus (top-p) sampling.
    
    Args:
        probs: Probability distribution
        p: Nucleus parameter (0-1)
        legal_mask: Legal move mask (optional)
        
    Returns:
        Sampled index
    """
    if legal_mask is not None:
        masked_probs = probs * legal_mask
        if np.sum(masked_probs) == 0:
            legal_indices = np.where(legal_mask)[0]
            return np.random.choice(legal_indices)
        probs = masked_probs
    
    # Sort probabilities
    sorted_indices = np.argsort(probs)[::-1]
    sorted_probs = probs[sorted_indices]
    
    # Find nucleus
    cumulative_probs = np.cumsum(sorted_probs)
    nucleus_size = np.searchsorted(cumulative_probs, p) + 1
    nucleus_size = min(nucleus_size, len(probs))
    
    # Sample from nucleus
    nucleus_indices = sorted_indices[:nucleus_size]
    nucleus_probs = probs[nucleus_indices]
    nucleus_probs = nucleus_probs / np.sum(nucleus_probs)
    
    chosen_idx = np.random.choice(len(nucleus_indices), p=nucleus_probs)
    return nucleus_indices[chosen_idx]
