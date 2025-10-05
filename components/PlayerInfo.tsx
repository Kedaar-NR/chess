"use client";

import React from "react";
import { Clock, User } from "lucide-react";

interface PlayerInfoProps {
  name: string;
  time: number;
  isActive: boolean;
}

export const PlayerInfo: React.FC<PlayerInfoProps> = ({
  name,
  time,
  isActive,
}) => {
  const isWhite = name.toLowerCase() === "white";

  return (
    <div
      className={`relative p-4 rounded-lg transition-all ${
        isActive
          ? "bg-slate-700 border-2 border-emerald-500"
          : "bg-slate-800 border border-slate-700 opacity-70"
      }`}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-full flex items-center justify-center ${isWhite ? "bg-white border-2 border-slate-600" : "bg-slate-900 border-2 border-white"}`}>
            <User size={20} className={isWhite ? "text-slate-800" : "text-white"} />
          </div>
          <div>
            <h3 className="font-semibold text-base text-white">{name}</h3>
            <div className="flex items-center gap-2 text-slate-300">
              <Clock size={14} />
              <span className="font-mono text-sm">{time.toFixed(1)}s</span>
            </div>
          </div>
        </div>
        {isActive && (
          <div className="w-2 h-2 bg-emerald-500 rounded-full"></div>
        )}
      </div>
    </div>
  );
};
