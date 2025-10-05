@echo off
echo ================================================================================
echo CHESS ENGINE - WINDOWS START
echo ================================================================================
echo This will install dependencies, test the engine, and start the game!
echo ================================================================================

echo.
echo 1. Installing dependencies...
pip install python-chess tensorflow numpy pandas scikit-learn fastapi uvicorn typer pyyaml orjson tensorboard matplotlib rich

echo.
echo 2. Creating directories...
mkdir data\raw 2>nul
mkdir data\tfrecords 2>nul
mkdir data\selfplay 2>nul
mkdir runs\supervised 2>nul
mkdir runs\rl 2>nul
mkdir logs 2>nul

echo.
echo 3. Testing chess engine...
python -c "import chess; board = chess.Board(); print('Chess board created with', len(list(board.legal_moves)), 'legal moves')"

echo.
echo 4. Starting enhanced chess UI...
echo ================================================================================
echo CHESS ENGINE READY!
echo ================================================================================
echo The enhanced UI will show a beautiful chess board with move logging
echo and real-time statistics, just like the one shown!
echo ================================================================================

python chess_ui_enhanced.py

pause
