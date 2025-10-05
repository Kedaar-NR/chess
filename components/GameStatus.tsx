"use client";

import React from "react";
import { AlertCircle, Crown, MinusCircle, Sparkles } from "lucide-react";

interface GameStatusProps {
  status: "normal" | "check" | "checkmate" | "stalemate";
  currentPlayer: "white" | "black";
  aiThinking: boolean;
}

export const GameStatus: React.FC<GameStatusProps> = ({
  status,
  currentPlayer,
  aiThinking,
}) => {
  const getStatusInfo = () => {
    if (aiThinking) {
      return {
        icon: <Sparkles className="animate-pulse" size={24} />,
        text: "AI is thinking...",
        className: "bg-blue-600 text-white border border-blue-700",
      };
    }

    switch (status) {
      case "check":
        return {
          icon: <AlertCircle size={24} />,
          text: `${currentPlayer === "white" ? "White" : "Black"} is in check!`,
          className: "bg-amber-500 text-white border border-amber-600",
        };
      case "checkmate":
        return {
          icon: <Crown size={24} />,
          text: `Checkmate! ${
            currentPlayer === "white" ? "Black" : "White"
          } wins!`,
          className: "bg-red-600 text-white border border-red-700",
        };
      case "stalemate":
        return {
          icon: <MinusCircle size={24} />,
          text: "Stalemate! Game is a draw.",
          className: "bg-slate-600 text-white border border-slate-700",
        };
      default:
        return {
          icon: (
            <div className={`w-6 h-6 rounded-full ${currentPlayer === "white" ? "bg-white border-2 border-slate-700" : "bg-slate-800"}`} />
          ),
          text: `${currentPlayer === "white" ? "White" : "Black"} to move`,
          className: "bg-emerald-600 text-white border border-emerald-700",
        };
    }
  };

  const statusInfo = getStatusInfo();

  return (
    <div
      className={`flex items-center justify-center gap-3 px-6 py-3 rounded-lg ${statusInfo.className} transition-colors w-full max-w-md`}
    >
      <div className="flex-shrink-0">
        {statusInfo.icon}
      </div>
      <span className="font-semibold text-base">{statusInfo.text}</span>
    </div>
  );
};
