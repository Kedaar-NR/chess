"""
Time management for chess engine.

Converts time controls to per-move time budgets.
"""

import time
from typing import Optional, Tuple
try:
    import chess
except ImportError:
    print("Warning: python-chess not installed. Install with: pip install python-chess")
    chess = None


class TimeManager:
    """Manages time allocation for chess moves."""
    
    def __init__(self, time_control: Optional[str] = None):
        """
        Initialize time manager.
        
        Args:
            time_control: Time control string (e.g., "300+5", "60+0", "0.5+0.1")
        """
        self.time_control = time_control
        self.time_left = None
        self.increment = None
        self.moves_to_go = None
        self.start_time = None
        
    def set_time_control(self, time_control: str) -> None:
        """Set the time control."""
        self.time_control = time_control
        self._parse_time_control()
    
    def _parse_time_control(self) -> None:
        """Parse time control string."""
        if not self.time_control:
            return
            
        # Handle different time control formats
        if '+' in self.time_control:
            parts = self.time_control.split('+')
            self.time_left = float(parts[0])
            self.increment = float(parts[1])
        else:
            self.time_left = float(self.time_control)
            self.increment = 0.0
    
    def start_move(self) -> None:
        """Start timing a move."""
        self.start_time = time.time()
    
    def get_time_budget(self, moves_remaining: Optional[int] = None) -> float:
        """
        Calculate time budget for current move.
        
        Args:
            moves_remaining: Number of moves remaining in game
            
        Returns:
            Time budget in seconds
        """
        if self.time_left is None:
            return 5.0  # Default 5 seconds
        
        if moves_remaining is None:
            moves_remaining = 20  # Default assumption
        
        # Basic time allocation
        base_time = self.time_left / max(1, moves_remaining)
        
        # Add increment
        total_time = base_time + self.increment
        
        # Reserve some time for later moves
        reserve_factor = 0.8
        budget = total_time * reserve_factor
        
        # Ensure we don't exceed remaining time
        budget = min(budget, self.time_left * 0.1)
        
        return max(0.1, budget)  # Minimum 0.1 seconds
    
    def update_time(self, time_left: float) -> None:
        """Update remaining time."""
        self.time_left = time_left
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time since move start."""
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time
    
    def should_stop_search(self, max_time: float, nodes_searched: int, max_nodes: Optional[int] = None) -> bool:
        """
        Check if search should stop.
        
        Args:
            max_time: Maximum time to spend
            nodes_searched: Number of nodes searched so far
            max_nodes: Maximum nodes to search (optional)
            
        Returns:
            True if search should stop
        """
        # Time limit
        if self.get_elapsed_time() >= max_time:
            return True
        
        # Node limit
        if max_nodes is not None and nodes_searched >= max_nodes:
            return True
        
        # Emergency stop if very little time left
        if self.time_left is not None and self.time_left < 1.0:
            return True
        
        return False
    
    def get_emergency_time(self) -> float:
        """Get emergency time budget when time is running low."""
        if self.time_left is None:
            return 0.1
        
        return min(0.1, self.time_left * 0.1)