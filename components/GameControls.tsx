"use client";

import React from "react";
import { RotateCcw, Play, Bot, Undo2 } from "lucide-react";

interface GameControlsProps {
  onNewGame: () => void;
  onAIMove: () => void;
  onStartAIGame: () => void;
  onUndo: () => void;
  aiThinking: boolean;
}

export const GameControls: React.FC<GameControlsProps> = ({
  onNewGame,
  onAIMove,
  onStartAIGame,
  onUndo,
  aiThinking,
}) => {
  return (
    <div className="flex flex-col gap-2.5 bg-slate-800 p-4 rounded-lg border border-slate-700">
      <h3 className="text-slate-400 font-semibold text-sm uppercase tracking-wide mb-1">Game Controls</h3>

      <button
        onClick={onNewGame}
        className="game-btn bg-blue-600 hover:bg-blue-700 border border-blue-700"
        disabled={aiThinking}
      >
        <RotateCcw size={18} />
        <span>New Game</span>
      </button>

      <button
        onClick={onAIMove}
        className="game-btn bg-emerald-600 hover:bg-emerald-700 border border-emerald-700"
        disabled={aiThinking}
      >
        <Play size={18} />
        <span>{aiThinking ? "AI Thinking..." : "AI Move"}</span>
      </button>

      <button
        onClick={onStartAIGame}
        className="game-btn bg-purple-600 hover:bg-purple-700 border border-purple-700"
        disabled={aiThinking}
      >
        <Bot size={18} />
        <span>AI vs AI</span>
      </button>

      <button
        onClick={onUndo}
        className="game-btn bg-amber-600 hover:bg-amber-700 border border-amber-700"
        disabled={aiThinking}
      >
        <Undo2 size={18} />
        <span>Undo Move</span>
      </button>
    </div>
  );
};
