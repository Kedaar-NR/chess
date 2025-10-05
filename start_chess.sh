#!/bin/bash

echo "================================================================================"
echo "CHESS ENGINE - MAC/LINUX START"
echo "================================================================================"
echo "This will install dependencies, test the engine, and start the game!"
echo "================================================================================"

echo ""
echo "1. Installing dependencies..."
pip install python-chess tensorflow numpy pandas scikit-learn fastapi uvicorn typer pyyaml orjson tensorboard matplotlib rich

echo ""
echo "2. Creating directories..."
mkdir -p data/raw
mkdir -p data/tfrecords
mkdir -p data/selfplay
mkdir -p runs/supervised
mkdir -p runs/rl
mkdir -p logs

echo ""
echo "3. Testing chess engine..."
python -c "import chess; board = chess.Board(); print('Chess board created with', len(list(board.legal_moves)), 'legal moves')"

echo ""
echo "4. Starting enhanced chess UI..."
echo "================================================================================"
echo "CHESS ENGINE READY!"
echo "================================================================================"
echo "The enhanced UI will show a beautiful chess board with move logging"
echo "and real-time statistics, just like the one shown!"
echo "================================================================================"

python chess_ui_enhanced.py
