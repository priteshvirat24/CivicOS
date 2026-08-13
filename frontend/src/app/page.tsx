"use client";

import useSWR from "swr";
import { useState } from "react";
import { MetricsPanel } from "@/components/MetricsPanel";
import { ActivityFeed } from "@/components/ActivityFeed";
import { SourceCards } from "@/components/SourceCards";
import { DatasetExplorer } from "@/components/DatasetExplorer";
import { InteractiveArchitecture } from "@/components/InteractiveArchitecture";
import { AgentGrid } from "@/components/AgentGrid";
import { Play, Sparkles, AlertCircle, BookOpen, Activity } from "lucide-react";
import Link from "next/link";
import { API_BASE } from "@/utils/config";
import { Hero } from "@/components/Hero";
import { JudgeMode } from "@/components/JudgeMode";
import { motion, AnimatePresence } from "framer-motion";

export default function Dashboard() {
  const { data: healthData, error } = useSWR(`${API_BASE}/api/agents/health`, { refreshInterval: 5000 });
  const [demoStatus, setDemoStatus] = useState<string | null>(null);
  const [isMutating, setIsMutating] = useState(false);
  const [isTriggering, setIsTriggering] = useState(false);
  const [isJudgeMode, setIsJudgeMode] = useState(false);
  
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

  const handleExperienceClick = () => {
    setIsJudgeMode(true);
    // Ensure we start from top of page when returning
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="bg-[#fafafa] min-h-screen font-sans selection:bg-slate-200 selection:text-slate-900">
      <AnimatePresence>
        {isJudgeMode && (
          <JudgeMode onClose={() => setIsJudgeMode(false)} />
        )}
      </AnimatePresence>

      <Hero onExperienceClick={handleExperienceClick} />

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

      {/* Header sections removed in favor of Hero */}

      {/* Top Metrics */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, margin: "-50px" }}
        id="data" className="mt-8"
      >
        <MetricsPanel stats={stats} />
      </motion.div>

      {/* HOW CIVICOS STAYS ALIVE */}
      <motion.div 
        initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, margin: "-100px" }}
        className="mt-24 mb-12"
      >
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-sm font-bold tracking-widest text-slate-400 uppercase">How CivicOS Stays Alive</h2>
        </div>
        
        {/* 3D Interactive Architecture */}
        <InteractiveArchitecture />
        
        {/* Mobile/Simple Explanation Fallback */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-4 gap-6 text-sm text-slate-500 font-medium">
          <div className="bg-white p-4 rounded-xl border border-slate-200">
            <strong className="text-slate-800 block mb-1">1. Observe</strong>
            Every source has an owner agent.
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200">
            <strong className="text-slate-800 block mb-1">2. Detect</strong>
            Every change becomes a proposal.
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200">
            <strong className="text-slate-800 block mb-1">3. Verify</strong>
            Every proposal is independently verified.
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200">
            <strong className="text-slate-800 block mb-1">4. Merge</strong>
            Only verified changes reach the live dataset.
          </div>
        </div>

        {/* Live Agent Grid */}
        <div className="mt-12">
          <AgentGrid agents={healthData?.agents || null} />
        </div>
      </motion.div>

      {/* Split View */}
      <motion.div 
        initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, margin: "-100px" }}
        id="activity" className="grid grid-cols-1 lg:grid-cols-12 gap-12 mt-24"
      >
        {/* Left Col: Activity Feed */}
        <div className="lg:col-span-5">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-sm font-bold tracking-widest text-slate-400 uppercase">Orchestrator Feed</h2>
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
          </div>
          <ActivityFeed />
        </div>
        
        {/* Right Col: Agents */}
        <div id="sources" className="lg:col-span-7">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-sm font-bold tracking-widest text-slate-400 uppercase">Autonomous Agents</h2>
            <Link href="/ops" className="text-xs font-semibold text-blue-600 hover:text-blue-800 uppercase tracking-widest flex items-center gap-1">
              Ops Dashboard <Activity size={12} />
            </Link>
          </div>
          <SourceCards />
        </div>
      </motion.div>

      {/* Full Width: Dataset Explorer */}
      <motion.div 
        initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, margin: "-100px" }}
        className="mt-20 border-t border-slate-200 pt-16"
      >
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-sm font-bold tracking-widest text-slate-400 uppercase">Live Canonical Dataset</h2>
          <Link href="/methodology" className="text-xs font-semibold text-slate-500 hover:text-slate-800 uppercase tracking-widest flex items-center gap-1">
            Methodology <BookOpen size={12} />
          </Link>
        </div>
        <DatasetExplorer />
      </motion.div>
      
      {/* FINAL SECTION */}
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }} whileInView={{ opacity: 1, scale: 1 }} viewport={{ once: true, margin: "-100px" }}
        className="mt-32 pt-16 pb-16 border-t border-slate-200 text-center flex flex-col items-center justify-center"
      >
        <h2 className="text-4xl md:text-6xl font-black font-sans text-slate-900 tracking-tighter mb-4">
          REALITY CHANGED.<br />CIVICOS NOTICED.
        </h2>
        <p className="text-xl font-serif text-slate-500 font-medium">
          CivicOS<br />Living civic data, continuously maintained.
        </p>
      </motion.div>

      {/* Footer */}
      <footer className="mt-12 pt-8 border-t border-slate-200 text-center pb-12">
        <p className="text-xs text-slate-400 uppercase tracking-widest font-semibold">
          CivicOS System / 100% Autonomous / Cryptographically Verified
        </p>
      </footer>
      </main>
    </div>
  );
}
