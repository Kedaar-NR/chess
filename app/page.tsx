"use client";

import React from "react";
import { useChessGame } from "@/hooks/useChessGame";
import { ChessBoard } from "@/components/ChessBoard";
import { GameControls } from "@/components/GameControls";
import { PlayerInfo } from "@/components/PlayerInfo";
import { MoveLog } from "@/components/MoveLog";
import { GameStatus } from "@/components/GameStatus";

export default function Home() {
  const {
    gameState,
    handleSquareClick,
    startNewGame,
    startAIGame,
    makeAIMove,
    undoMove,
  } = useChessGame();

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4 sm:p-6 lg:p-8">
      <div className="w-full max-w-7xl">
        {/* Header */}
        <div className="text-center mb-6 lg:mb-8">
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-2">
            Chess Engine
          </h1>
          <p className="text-slate-400 text-sm sm:text-base">
            AI-powered chess with real-time analysis
          </p>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-[320px_1fr_320px] gap-4 lg:gap-6 items-start">
          {/* Left Panel - Player Info & Controls */}
          <div className="order-2 xl:order-1 space-y-4">
            {/* Player Info */}
            <div className="space-y-3">
              <PlayerInfo
                name="Black"
                time={gameState.blackTime}
                isActive={
                  gameState.currentPlayer === "black" && !gameState.aiThinking
                }
              />
              <PlayerInfo
                name="White"
                time={gameState.whiteTime}
                isActive={
                  gameState.currentPlayer === "white" && !gameState.aiThinking
                }
              />
            </div>

            {/* Game Controls */}
            <GameControls
              onNewGame={startNewGame}
              onAIMove={makeAIMove}
              onStartAIGame={startAIGame}
              onUndo={undoMove}
              aiThinking={gameState.aiThinking}
            />
          </div>

          {/* Center Panel - Chess Board */}
          <div className="order-1 xl:order-2 flex flex-col items-center gap-4">
            {/* Game Status */}
            <GameStatus
              status={gameState.gameStatus}
              currentPlayer={gameState.currentPlayer}
              aiThinking={gameState.aiThinking}
            />

            <ChessBoard
              gameState={gameState}
              onSquareClick={handleSquareClick}
            />
          </div>

          {/* Right Panel - Move Log */}
          <div className="order-3">
            <MoveLog moves={gameState.moveHistory} />
          </div>
        </div>
      </div>
    </div>
  );
}
