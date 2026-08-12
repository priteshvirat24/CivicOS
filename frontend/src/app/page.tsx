"use client";

import useSWR from "swr";
import { useState } from "react";
import { MetricsPanel } from "@/components/MetricsPanel";
import { ActivityFeed } from "@/components/ActivityFeed";
import { SourceCards } from "@/components/SourceCards";
import { DatasetExplorer } from "@/components/DatasetExplorer";
import { Play, Sparkles, AlertCircle, BookOpen, Activity } from "lucide-react";
import Link from "next/link";
import { API_BASE } from "@/utils/config";

export default function Dashboard() {
  const { data: healthData, error } = useSWR(`${API_BASE}/api/agents/health`, { refreshInterval: 5000 });
  const [demoStatus, setDemoStatus] = useState<string | null>(null);
  const [isMutating, setIsMutating] = useState(false);
  const [isTriggering, setIsTriggering] = useState(false);
  
  // Calculate mock stats from health data for the prototype
  const stats = healthData ? {
    sourcesCount: healthData.agents.length,
    agentsCount: healthData.agents.length,
    changesToday: healthData.agents.filter((a: any) => a.last_change_detected_at).length,
    verifiedToday: healthData.agents.filter((a: any) => a.last_change_detected_at).length, 
  } : {
    sourcesCount: "-",
    agentsCount: "-",
    changesToday: "-",
    verifiedToday: "-"
  };

  const handleMutate = async () => {
    setIsMutating(true);
    try {
      await fetch(`${API_BASE}/api/demo/mutate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ income_limit: 500000 })
      });
      setDemoStatus("Source reality mutated! (Income Limit -> 500000)");
      setTimeout(() => setDemoStatus(null), 3000);
    } catch (e) {
      console.error(e);
    }
    setIsMutating(false);
  };

  const handleTrigger = async () => {
    setIsTriggering(true);
    try {
      await fetch(`${API_BASE}/api/agents/trigger`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ agent_id: "agent_demo_scheme" })
      });
      setDemoStatus("Polling cycle triggered for Demo Agent...");
      setTimeout(() => setDemoStatus(null), 3000);
    } catch (e) {
      console.error(e);
    }
    setIsTriggering(false);
  };

  return (
    <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 pb-32 relative">
      
      {/* Hackathon Demo Controls (Floating) */}
      <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 bg-slate-900 text-white px-6 py-4 rounded-full shadow-2xl flex items-center gap-6 border border-slate-700">
        <div className="flex items-center gap-2">
          <Sparkles size={18} className="text-emerald-400" />
          <span className="font-semibold text-sm tracking-wide">DEMO MODE</span>
        </div>
        <div className="w-px h-6 bg-slate-700"></div>
        <button 
          onClick={handleMutate}
          disabled={isMutating}
          className="text-sm font-medium hover:text-emerald-300 transition-colors flex items-center gap-2 disabled:opacity-50"
        >
          <AlertCircle size={16} />
          1. Mutate Reality
        </button>
        <button 
          onClick={handleTrigger}
          disabled={isTriggering}
          className="text-sm font-medium hover:text-blue-300 transition-colors flex items-center gap-2 disabled:opacity-50"
        >
          <Play size={16} />
          2. Trigger Poll
        </button>
        {demoStatus && (
          <div className="absolute -top-12 left-1/2 -translate-x-1/2 bg-white text-slate-800 px-4 py-2 rounded-sm shadow-md text-xs font-semibold whitespace-nowrap border border-slate-200">
            {demoStatus}
          </div>
        )}
      </div>

      {/* Header */}
      <header className="mb-12 border-b border-[#e2e8f0] pb-8">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-2 gap-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-1 bg-blue-600 rounded-sm"></div>
            <h2 className="text-sm font-semibold tracking-widest text-slate-500 uppercase">CivicOS Engine</h2>
          </div>
          <div className="flex items-center gap-6">
            <Link href="/ops" className="flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-slate-900 transition-colors">
              <Activity size={16} />
              Ops Dashboard
            </Link>
            <Link href="/methodology" className="flex items-center gap-2 text-sm font-medium text-blue-600 hover:text-blue-800 transition-colors">
              <BookOpen size={16} />
              Read Methodology
            </Link>
          </div>
        </div>
        <h1 className="text-5xl font-serif text-slate-900 tracking-tight leading-tight">
          Living Civic Data.
        </h1>
        <p className="mt-4 text-xl text-slate-500 max-w-3xl">
          This dataset maintains itself. Autonomous agents constantly poll external sources, detect deviations, cryptographically verify changes, and merge them into the canonical record.
        </p>
      </header>

      {/* Top Metrics */}
      <MetricsPanel stats={stats} />

      {/* Split View */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Col: Activity Feed */}
        <div className="lg:col-span-5">
          <h2 className="text-2xl font-serif text-slate-800 mb-6">Orchestrator Feed</h2>
          <ActivityFeed />
        </div>
        
        {/* Right Col: Agents */}
        <div className="lg:col-span-7">
          <h2 className="text-2xl font-serif text-slate-800 mb-6">Autonomous Agents</h2>
          <SourceCards />
        </div>
      </div>

      {/* Full Width: Dataset Explorer */}
      <div className="mt-8">
        <DatasetExplorer />
      </div>
      
      {/* Footer */}
      <footer className="mt-24 pt-8 border-t border-[#e2e8f0] text-center pb-12">
        <p className="text-sm text-slate-500 font-mono">
          CivicOS System / 100% Autonomous / Cryptographically Verified
        </p>
      </footer>
    </main>
  );
}
