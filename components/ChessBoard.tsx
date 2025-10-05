'use client';

import React from 'react';
import { GameState, ChessPosition, PIECE_SYMBOLS } from '@/types/chess';

interface ChessBoardProps {
  gameState: GameState;
  onSquareClick: (row: number, col: number) => void;
}

export const ChessBoard: React.FC<ChessBoardProps> = ({ gameState, onSquareClick }) => {
  const { board, selectedSquare, moveHistory } = gameState;

  const getSquareClass = (row: number, col: number): string => {
    const isLight = (row + col) % 2 === 0;
    let classes = `chess-square ${isLight ? 'light' : 'dark'}`;

    if (selectedSquare && selectedSquare.row === row && selectedSquare.col === col) {
      classes += ' selected';
    }

    // Highlight last move
    if (moveHistory.length > 0) {
      const lastMove = moveHistory[moveHistory.length - 1];
      if ((lastMove.from.row === row && lastMove.from.col === col) ||
          (lastMove.to.row === row && lastMove.to.col === col)) {
        classes += ' last-move';
      }
    }

    return classes;
  };

  const getPieceSymbol = (piece: string): string => {
    return PIECE_SYMBOLS[piece] || '';
  };

  const isWhitePiece = (piece: string): boolean => {
    return piece === piece.toUpperCase();
  };

  const getFileLabel = (col: number): string => {
    return ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'][col];
  };

  const getRankLabel = (row: number): number => {
    return 8 - row;
  };

  return (
    <div className="flex flex-col items-center">
      {/* Chess board */}
      <div className="grid grid-cols-8 grid-rows-8 w-[560px] h-[560px] shadow-2xl rounded-lg overflow-hidden ring-4 ring-slate-700/50">
        {board.map((row, rowIndex) =>
          row.map((piece, colIndex) => {
            const isLight = (rowIndex + colIndex) % 2 === 0;
            const showFileLabel = rowIndex === 7; // Bottom row
            const showRankLabel = colIndex === 0; // Left column

            return (
              <div
                key={`${rowIndex}-${colIndex}`}
                className={getSquareClass(rowIndex, colIndex)}
                onClick={() => onSquareClick(rowIndex, colIndex)}
              >
                {piece && (
                  <div className={`chess-piece ${isWhitePiece(piece) ? 'white' : 'black'}`}>
                    {getPieceSymbol(piece)}
                  </div>
                )}

                {/* File label (a-h) on bottom row */}
                {showFileLabel && (
                  <div className={`absolute bottom-0.5 right-1 text-xs font-bold select-none ${isLight ? 'text-chess-dark' : 'text-chess-light'}`}>
                    {getFileLabel(colIndex)}
                  </div>
                )}

                {/* Rank label (1-8) on left column */}
                {showRankLabel && (
                  <div className={`absolute top-0.5 left-1 text-xs font-bold select-none ${isLight ? 'text-chess-dark' : 'text-chess-light'}`}>
                    {getRankLabel(rowIndex)}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
