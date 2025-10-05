"""
FastAPI application for chess engine.

Provides REST API for chess analysis and best move calculation.
"""

import os
import sys
import time
import chess
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from typing import Optional, Dict, Any
import uvicorn

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from chessai.engine.search_mcts import best_move, analyse_simple
from chessai.engine.search_alphabeta import best_move_alphabeta, analyse_alphabeta
from chessai.engine.evaluation import value_to_centipawns
from chessai.models.policy_value import load_model, PolicyValueNetwork
from chessai.api.schemas import (
    AnalysisRequest, AnalysisResponse, BestMoveRequest, BestMoveResponse,
    HealthResponse, ErrorResponse
)
from chessai.utils.logging import setup_logging


# Global variables
app = FastAPI(
    title="ChessAI Engine",
    description="Deep learning chess engine with MCTS and alpha-beta search",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model
model: Optional[PolicyValueNetwork] = None
model_path = os.getenv("MODEL_PATH", "runs/best/model.h5")
start_time = time.time()


def load_chess_model() -> Optional[PolicyValueNetwork]:
    """Load the chess model."""
    global model
    
    if model is not None:
        return model
    
    try:
        if os.path.exists(model_path):
            model = load_model(model_path)
            print(f"Loaded model from {model_path}")
        else:
            print(f"Model not found at {model_path}, using dummy model")
            model = PolicyValueNetwork(None)
    except Exception as e:
        print(f"Failed to load model: {e}")
        model = PolicyValueNetwork(None)
    
    return model


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    print("Starting ChessAI Engine...")
    load_chess_model()


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    global start_time
    
    model_loaded = model is not None
    uptime = time.time() - start_time
    
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        model_loaded=model_loaded,
        model_path=model_path if model_loaded else None,
        uptime=uptime
    )


@app.post("/analyse", response_model=AnalysisResponse)
async def analyse_position(request: AnalysisRequest):
    """Analyze a chess position."""
    try:
        # Parse FEN
        board = chess.Board(request.fen)
        
        # Get model
        chess_model = load_chess_model()
        
        # Perform analysis
        start_time = time.time()
        
        if chess_model and chess_model.model is not None:
            # Use MCTS with neural network
            result = analyse_simple(board, request.time_limit, chess_model)
        else:
            # Use alpha-beta fallback
            result = analyse_alphabeta(board, request.time_limit)
        
        search_time = time.time() - start_time
        
        # Convert to response
        return AnalysisResponse(
            bestmove=result.get('bestmove'),
            pv=result.get('pv', []),
            score=result.get('value', 0.0),
            centipawns=result.get('centipawns', 0),
            value=result.get('value', 0.0),
            nodes=result.get('nodes', 0),
            depth=result.get('depth', 0),
            time_ms=int(search_time * 1000)
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/bestmove", response_model=BestMoveResponse)
async def get_best_move(request: BestMoveRequest):
    """Get the best move for a position."""
    try:
        # Parse FEN
        board = chess.Board(request.fen)
        
        # Get model
        chess_model = load_chess_model()
        
        # Get best move
        start_time = time.time()
        
        if chess_model and chess_model.model is not None:
            # Use MCTS with neural network
            best_move_result = best_move(board, request.time_limit, request.max_nodes, 0.0, chess_model)
        else:
            # Use alpha-beta fallback
            best_move_result = best_move_alphabeta(board, request.time_limit)
        
        search_time = time.time() - start_time
        
        # Get position evaluation
        if best_move_result:
            # Make the move and evaluate
            board.push(best_move_result)
            if chess_model and chess_model.model is not None:
                _, value = chess_model.predict_policy_value(board)
            else:
                from chessai.engine.evaluation import evaluate_position
                value, _ = evaluate_position(board)
            
            centipawns = value_to_centipawns(value)
        else:
            value = 0.0
            centipawns = 0
        
        return BestMoveResponse(
            bestmove=str(best_move_result) if best_move_result else None,
            score=value,
            centipawns=centipawns,
            nodes=0,  # TODO: Get actual node count
            time_ms=int(search_time * 1000)
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with basic info."""
    return """
    <html>
        <head>
            <title>ChessAI Engine</title>
        </head>
        <body>
            <h1>ChessAI Engine</h1>
            <p>Deep learning chess engine with MCTS and alpha-beta search</p>
            <p><a href="/docs">API Documentation</a></p>
            <p><a href="/static/index.html">Chess Board UI</a></p>
        </body>
    </html>
    """


# Mount static files
app.mount("/static", StaticFiles(directory="chessai/ui/static"), name="static")


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "chessai.api.app:app",
        host="0.0.0.0",
        port=8080,
        reload=True
    )
