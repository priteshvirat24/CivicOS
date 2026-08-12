"use client";

import { Activity, Database, ShieldCheck, Zap } from "lucide-react";

export function MetricsPanel({ stats }: { stats: any }) {
  if (!stats) return null;

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
      <div className="bg-white p-6 border border-[#e2e8f0] rounded-sm shadow-sm flex items-start gap-4">
        <div className="p-3 bg-slate-100 rounded-sm text-slate-700">
          <Database size={20} strokeWidth={1.5} />
        </div>
        <div>
          <p className="text-xs font-semibold tracking-wider text-slate-500 uppercase mb-1">Active Sources</p>
          <p className="text-3xl font-serif text-slate-900">{stats.sourcesCount}</p>
        </div>
      </div>

      <div className="bg-white p-6 border border-[#e2e8f0] rounded-sm shadow-sm flex items-start gap-4">
        <div className="p-3 bg-slate-100 rounded-sm text-slate-700">
          <Activity size={20} strokeWidth={1.5} />
        </div>
        <div>
          <p className="text-xs font-semibold tracking-wider text-slate-500 uppercase mb-1">Active Agents</p>
          <p className="text-3xl font-serif text-slate-900">{stats.agentsCount}</p>
        </div>
      </div>

      <div className="bg-white p-6 border border-[#e2e8f0] rounded-sm shadow-sm flex items-start gap-4">
        <div className="p-3 bg-slate-100 rounded-sm text-slate-700">
          <Zap size={20} strokeWidth={1.5} />
        </div>
        <div>
          <p className="text-xs font-semibold tracking-wider text-slate-500 uppercase mb-1">Changes Detected</p>
          <p className="text-3xl font-serif text-slate-900">{stats.changesToday}</p>
        </div>
      </div>

      <div className="bg-white p-6 border border-[#e2e8f0] rounded-sm shadow-sm flex items-start gap-4">
        <div className="p-3 bg-emerald-50 rounded-sm text-emerald-700">
          <ShieldCheck size={20} strokeWidth={1.5} />
        </div>
        <div>
          <p className="text-xs font-semibold tracking-wider text-slate-500 uppercase mb-1">Verified Updates</p>
          <p className="text-3xl font-serif text-slate-900">{stats.verifiedToday}</p>
        </div>
      </div>
    </div>
  );
}
