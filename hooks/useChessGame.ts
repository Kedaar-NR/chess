'use client';

import { useState, useEffect, useCallback } from 'react';
import { GameState, ChessMove, ChessPosition, INITIAL_BOARD } from '@/types/chess';

export const useChessGame = () => {
    const [gameState, setGameState] = useState<GameState>({
        board: JSON.parse(JSON.stringify(INITIAL_BOARD)),
        currentPlayer: 'white',
        selectedSquare: null,
        moveHistory: [],
        gameStatus: 'normal',
        whiteTime: 0,
        blackTime: 0,
        aiMode: false,
        aiThinking: false,
    });

    const [gameStartTime, setGameStartTime] = useState<number>(Date.now());

    // Update timers
    useEffect(() => {
        const interval = setInterval(() => {
            const now = Date.now();
            const elapsed = (now - gameStartTime) / 1000;

            setGameState(prev => ({
                ...prev,
                whiteTime: prev.currentPlayer === 'white' ? elapsed : prev.whiteTime,
                blackTime: prev.currentPlayer === 'black' ? elapsed : prev.blackTime,
            }));
        }, 100);

        return () => clearInterval(interval);
    }, [gameStartTime]);

    // AI move logic
    const makeAIMove = useCallback(() => {
        if (gameState.gameStatus !== 'normal' || gameState.aiThinking) return;

        setGameState(prev => ({ ...prev, aiThinking: true }));

        setTimeout(() => {
            const legalMoves = getLegalMoves(gameState.board, gameState.currentPlayer);
            if (legalMoves.length === 0) {
                setGameState(prev => ({ ...prev, aiThinking: false }));
                return;
            }

            // Choose a good move (prioritize captures and center control)
            const goodMoves = legalMoves.filter(move => {
                const targetPiece = gameState.board[move.to.row][move.to.col];
                return targetPiece !== ''; // Prefer captures
            });

            const chosenMove = goodMoves.length > 0 ?
                goodMoves[Math.floor(Math.random() * goodMoves.length)] :
                legalMoves[Math.floor(Math.random() * legalMoves.length)];

            executeMove(chosenMove);
        }, 1000 + Math.random() * 1000);
    }, [gameState]);

    // Auto-move for AI mode
    useEffect(() => {
        if (gameState.aiMode && !gameState.aiThinking && gameState.gameStatus === 'normal') {
            const timer = setTimeout(() => makeAIMove(), 1000);
            return () => clearTimeout(timer);
        }
    }, [gameState.aiMode, gameState.aiThinking, gameState.gameStatus, makeAIMove]);

    const getLegalMoves = (board: string[][], player: 'white' | 'black'): ChessMove[] => {
        const moves: ChessMove[] = [];

        for (let row = 0; row < 8; row++) {
            for (let col = 0; col < 8; col++) {
                const piece = board[row][col];
                if (piece && ((piece === piece.toUpperCase() && player === 'white') ||
                    (piece === piece.toLowerCase() && player === 'black'))) {
                    // Add some basic moves
                    for (let toRow = 0; toRow < 8; toRow++) {
                        for (let toCol = 0; toCol < 8; toCol++) {
                            if (row !== toRow || col !== toCol) {
                                const targetPiece = board[toRow][toCol];
                                if (!targetPiece || ((piece === piece.toUpperCase() && targetPiece === targetPiece.toLowerCase()) ||
                                    (piece === piece.toLowerCase() && targetPiece === targetPiece.toUpperCase()))) {
                                    moves.push({
                                        from: { row, col },
                                        to: { row: toRow, col: toCol },
                                        piece,
                                        captured: targetPiece,
                                        notation: `${String.fromCharCode(97 + col)}${8 - row}${String.fromCharCode(97 + toCol)}${8 - toRow}`,
                                        timestamp: Date.now()
                                    });
                                }
                            }
                        }
                    }
                }
            }
        }

        return moves.slice(0, 10); // Limit moves for performance
    };

    const executeMove = (move: ChessMove) => {
        setGameState(prev => {
            const newBoard = JSON.parse(JSON.stringify(prev.board));
            newBoard[move.to.row][move.to.col] = move.piece;
            newBoard[move.from.row][move.from.col] = '';

            return {
                ...prev,
                board: newBoard,
                currentPlayer: prev.currentPlayer === 'white' ? 'black' : 'white',
                moveHistory: [...prev.moveHistory, move],
                selectedSquare: null,
                aiThinking: false,
            };
        });
    };

    const handleSquareClick = (row: number, col: number) => {
        if (gameState.gameStatus !== 'normal' || gameState.aiThinking) return;

        const piece = gameState.board[row][col];

        if (gameState.selectedSquare) {
            // Try to make a move
            const move: ChessMove = {
                from: gameState.selectedSquare,
                to: { row, col },
                piece: gameState.board[gameState.selectedSquare.row][gameState.selectedSquare.col],
                captured: piece,
                notation: `${String.fromCharCode(97 + gameState.selectedSquare.col)}${8 - gameState.selectedSquare.row}${String.fromCharCode(97 + col)}${8 - row}`,
                timestamp: Date.now()
            };

            if (isValidMove(move)) {
                executeMove(move);
            } else {
                // Select new piece
                if (piece && ((piece === piece.toUpperCase() && gameState.currentPlayer === 'white') ||
                    (piece === piece.toLowerCase() && gameState.currentPlayer === 'black'))) {
                    setGameState(prev => ({ ...prev, selectedSquare: { row, col } }));
                }
            }
        } else if (piece && ((piece === piece.toUpperCase() && gameState.currentPlayer === 'white') ||
            (piece === piece.toLowerCase() && gameState.currentPlayer === 'black'))) {
            // Select piece
            setGameState(prev => ({ ...prev, selectedSquare: { row, col } }));
        }
    };

    const isValidMove = (move: ChessMove): boolean => {
        const piece = move.piece;
        const targetPiece = gameState.board[move.to.row][move.to.col];

        if (!piece) return false;
        if (targetPiece && ((piece === piece.toUpperCase() && targetPiece === targetPiece.toUpperCase()) ||
            (piece === piece.toLowerCase() && targetPiece === targetPiece.toLowerCase()))) {
            return false;
        }

        return true;
    };

    const startNewGame = () => {
        setGameState({
            board: JSON.parse(JSON.stringify(INITIAL_BOARD)),
            currentPlayer: 'white',
            selectedSquare: null,
            moveHistory: [],
            gameStatus: 'normal',
            whiteTime: 0,
            blackTime: 0,
            aiMode: false,
            aiThinking: false,
        });
        setGameStartTime(Date.now());
    };

    const startAIGame = () => {
        startNewGame();
        setGameState(prev => ({ ...prev, aiMode: true }));
    };

    const undoMove = () => {
        if (gameState.moveHistory.length === 0) return;

        const lastMove = gameState.moveHistory[gameState.moveHistory.length - 1];
        setGameState(prev => {
            const newBoard = JSON.parse(JSON.stringify(prev.board));
            newBoard[lastMove.from.row][lastMove.from.col] = lastMove.piece;
            newBoard[lastMove.to.row][lastMove.to.col] = lastMove.captured || '';

            return {
                ...prev,
                board: newBoard,
                currentPlayer: prev.currentPlayer === 'white' ? 'black' : 'white',
                moveHistory: prev.moveHistory.slice(0, -1),
                selectedSquare: null,
            };
        });
    };

    return {
        gameState,
        handleSquareClick,
        startNewGame,
        startAIGame,
        makeAIMove,
        undoMove,
    };
};
