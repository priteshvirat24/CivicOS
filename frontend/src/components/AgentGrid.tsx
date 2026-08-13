"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Activity, CheckCircle, Clock, AlertCircle, PlayCircle, Code2, ShieldCheck, Zap } from "lucide-react";

interface Agent {
  id: string;
  source_url: string;
  is_healthy: boolean;
  last_run_at: string | null;
  last_change_detected_at: string | null;
}

interface AgentGridProps {
  agents: Agent[] | null;
}

const getAgentState = (agent: Agent) => {
  if (!agent.is_healthy) return { state: "ERROR", color: "text-red-500", bg: "bg-red-500", icon: AlertCircle };
  
  if (agent.last_change_detected_at) {
    const changeTime = new Date(agent.last_change_detected_at).getTime();
    const now = new Date().getTime();
    const diff = now - changeTime;
    
    // Simulate state transitions based on time since last change
    // This provides a beautiful visualization when the demo button is clicked
    if (diff < 2000) return { state: "CHANGE DETECTED", color: "text-emerald-500", bg: "bg-emerald-500", icon: Zap };
    if (diff < 4000) return { state: "PROCESSING", color: "text-emerald-500", bg: "bg-emerald-500", icon: Clock };
    if (diff < 6000) return { state: "PR CREATED", color: "text-emerald-500", bg: "bg-emerald-500", icon: Code2 };
    if (diff < 8000) return { state: "VERIFYING", color: "text-emerald-500", bg: "bg-emerald-500", icon: ShieldCheck };
    if (diff < 10000) return { state: "VERIFIED", color: "text-emerald-500", bg: "bg-emerald-500", icon: CheckCircle };
    if (diff < 14000) return { state: "MERGED", color: "text-emerald-600", bg: "bg-emerald-600", icon: Database };
  }
  
  return { state: "WATCHING", color: "text-slate-400", bg: "bg-slate-400", icon: PlayCircle };
};

const Database = ({ className }: { className?: string }) => (
  <svg className={className} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5V19A9 3 0 0 0 21 19V5"/><path d="M3 12A9 3 0 0 0 21 12"/></svg>
);

export function AgentGrid({ agents }: AgentGridProps) {
  // If data isn't loaded yet, show skeleton or default 8 agents
  const displayAgents = agents || Array.from({ length: 8 }).map((_, i) => ({
    id: `agent_${i}`,
    source_url: `https://api.source${i}.gov`,
    is_healthy: true,
    last_run_at: new Date().toISOString(),
    last_change_detected_at: null
  }));

  // Limit to exactly 8 cards as per design requirements
  const gridAgents = displayAgents.slice(0, 8);

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 w-full">
      <AnimatePresence>
        {gridAgents.map((agent, index) => {
          const { state, color, bg, icon: Icon } = getAgentState(agent);
          const isWatching = state === "WATCHING";
          
          return (
            <motion.div
              key={agent.id}
              layout
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ 
                layout: { type: "spring", stiffness: 300, damping: 30 },
                opacity: { duration: 0.2 } 
              }}
              className={`p-4 rounded-xl border flex flex-col justify-between h-32 transition-colors duration-500
                ${isWatching ? 'bg-white border-slate-200' : 'bg-slate-900 border-slate-700 shadow-xl'}
              `}
            >
              <div className="flex justify-between items-start">
                <div>
                  <h4 className={`text-xs font-bold font-mono tracking-widest ${isWatching ? 'text-slate-900' : 'text-white'}`}>
                    AGENT 0{index + 1}
                  </h4>
                  <p className={`text-[10px] truncate w-24 mt-1 font-mono ${isWatching ? 'text-slate-500' : 'text-slate-400'}`}>
                    {agent.source_url ? new URL(agent.source_url).hostname : 'source'}
                  </p>
                </div>
                <Icon size={16} className={color} />
              </div>
              
              <div className="mt-4">
                <motion.div 
                  key={state}
                  initial={{ opacity: 0, y: 5 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`text-[10px] font-bold tracking-widest uppercase flex items-center gap-1.5 ${color}`}
                >
                  <div className={`w-1.5 h-1.5 rounded-full ${bg} ${isWatching ? '' : 'animate-pulse'}`} />
                  {state}
                </motion.div>
                <p className={`text-[10px] mt-1 ${isWatching ? 'text-slate-400' : 'text-slate-500'}`}>
                  Last checked {agent.last_run_at ? "12s ago" : "never"}
                </p>
              </div>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}
