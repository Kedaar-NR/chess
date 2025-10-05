"""
Pydantic schemas for API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class GameResult(str, Enum):
    """Game result enumeration."""
    WHITE_WINS = "1-0"
    BLACK_WINS = "0-1"
    DRAW = "1/2-1/2"
    UNKNOWN = "*"


class AnalysisRequest(BaseModel):
    """Request schema for position analysis."""
    fen: str = Field(..., description="FEN string of the position")
    time_limit: Optional[float] = Field(5.0, description="Time limit in seconds")
    max_nodes: Optional[int] = Field(None, description="Maximum nodes to search")
    depth: Optional[int] = Field(None, description="Maximum search depth")


class BestMoveRequest(BaseModel):
    """Request schema for best move."""
    fen: str = Field(..., description="FEN string of the position")
    time_limit: Optional[float] = Field(5.0, description="Time limit in seconds")
    max_nodes: Optional[int] = Field(None, description="Maximum nodes to search")
    depth: Optional[int] = Field(None, description="Maximum search depth")


class MoveInfo(BaseModel):
    """Information about a chess move."""
    move: str = Field(..., description="Move in UCI notation")
    san: Optional[str] = Field(None, description="Move in SAN notation")
    from_square: str = Field(..., description="From square")
    to_square: str = Field(..., description="To square")
    promotion: Optional[str] = Field(None, description="Promotion piece")


class AnalysisResponse(BaseModel):
    """Response schema for position analysis."""
    bestmove: Optional[str] = Field(None, description="Best move in UCI notation")
    pv: List[str] = Field(default_factory=list, description="Principal variation")
    score: float = Field(..., description="Position score")
    centipawns: int = Field(..., description="Score in centipawns")
    value: float = Field(..., description="Neural network value")
    nodes: int = Field(..., description="Nodes searched")
    depth: int = Field(..., description="Search depth")
    time_ms: int = Field(..., description="Search time in milliseconds")
    mate_in: Optional[int] = Field(None, description="Mate in N moves")


class BestMoveResponse(BaseModel):
    """Response schema for best move."""
    bestmove: str = Field(..., description="Best move in UCI notation")
    score: float = Field(..., description="Position score")
    centipawns: int = Field(..., description="Score in centipawns")
    nodes: int = Field(..., description="Nodes searched")
    time_ms: int = Field(..., description="Search time in milliseconds")


class HealthResponse(BaseModel):
    """Response schema for health check."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Engine version")
    model_loaded: bool = Field(..., description="Whether model is loaded")
    model_path: Optional[str] = Field(None, description="Path to loaded model")
    uptime: float = Field(..., description="Service uptime in seconds")


class ErrorResponse(BaseModel):
    """Response schema for errors."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")
    code: Optional[str] = Field(None, description="Error code")


class GameRequest(BaseModel):
    """Request schema for game analysis."""
    moves: List[str] = Field(..., description="List of moves in UCI notation")
    time_limit: Optional[float] = Field(5.0, description="Time limit per move")
    max_nodes: Optional[int] = Field(None, description="Maximum nodes per move")


class GameResponse(BaseModel):
    """Response schema for game analysis."""
    moves: List[MoveInfo] = Field(..., description="Analyzed moves")
    final_position: str = Field(..., description="Final position FEN")
    result: GameResult = Field(..., description="Game result")
    total_time: float = Field(..., description="Total analysis time")


class EngineInfo(BaseModel):
    """Engine information."""
    name: str = Field(..., description="Engine name")
    version: str = Field(..., description="Engine version")
    author: str = Field(..., description="Engine author")
    options: Dict[str, Any] = Field(default_factory=dict, description="Engine options")


class UCIOption(BaseModel):
    """UCI option definition."""
    name: str = Field(..., description="Option name")
    type: str = Field(..., description="Option type")
    default: Optional[str] = Field(None, description="Default value")
    min: Optional[float] = Field(None, description="Minimum value")
    max: Optional[float] = Field(None, description="Maximum value")
    var: Optional[List[str]] = Field(None, description="Variable options")
