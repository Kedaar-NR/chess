"use client";

import React from "react";
import { ChessMove } from "@/types/chess";
import { ScrollText } from "lucide-react";

interface MoveLogProps {
  moves: ChessMove[];
}

export const MoveLog: React.FC<MoveLogProps> = ({ moves }) => {
  return (
    <div className="bg-slate-800 rounded-lg p-4 border border-slate-700 h-full max-h-[calc(100vh-12rem)] flex flex-col">
      <div className="flex items-center gap-2 mb-3">
        <ScrollText size={18} className="text-slate-400" />
        <h3 className="font-semibold text-base text-white">Move History</h3>
        {moves.length > 0 && (
          <span className="ml-auto text-xs text-slate-400 bg-slate-700 px-2 py-1 rounded">
            {moves.length} moves
          </span>
        )}
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar">
        {moves.length === 0 ? (
          <div className="text-center text-slate-400 py-12">
            <ScrollText size={48} className="mx-auto mb-4 opacity-30" />
            <p className="font-semibold">No moves yet</p>
            <p className="text-sm mt-2 opacity-70">Make your first move to begin</p>
          </div>
        ) : (
          <div className="space-y-1">
            {Array.from({ length: Math.ceil(moves.length / 2) }, (_, i) => {
              const whiteMove = moves[i * 2];
              const blackMove = moves[i * 2 + 1];
              const moveNumber = i + 1;
              const isLastMove = i === Math.ceil(moves.length / 2) - 1;

              return (
                <div
                  key={moveNumber}
                  className={`grid grid-cols-[40px_1fr_1fr] gap-2 py-2 px-3 rounded transition-colors ${
                    isLastMove
                      ? "bg-emerald-600/30 border border-emerald-600/50"
                      : "bg-slate-700/50 hover:bg-slate-700"
                  }`}
                >
                  <div className="font-semibold text-slate-400 text-sm flex items-center">
                    {moveNumber}.
                  </div>
                  <div className="flex items-center justify-start">
                    <span className="font-mono text-white text-sm">
                      {whiteMove?.notation || "—"}
                    </span>
                  </div>
                  <div className="flex items-center justify-start">
                    <span className="font-mono text-slate-300 text-sm">
                      {blackMove?.notation || "—"}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
