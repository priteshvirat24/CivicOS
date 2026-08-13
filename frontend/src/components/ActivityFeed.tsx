"use client";

import useSWR from "swr";
import { format } from "date-fns";
import { ServerCog, GitPullRequest, ShieldCheck, CheckCircle2, FileJson } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { SkeletonFeed } from "./Skeletons";
import { API_BASE } from "@/utils/config";

export function ActivityFeed() {
  const { data, error } = useSWR(`${API_BASE}/api/activity/`, {
    refreshInterval: 3000,
  });

  if (error) return (
    <div className="bg-red-50 border border-red-200 text-red-600 rounded-lg p-6 text-center">
      <h3 className="font-semibold mb-1">Failed to load activity</h3>
    </div>
  );
  if (!data) return <SkeletonFeed />;

  const getIcon = (type: string, status?: string) => {
    if (type === "agent_run") return <ServerCog size={16} className="text-slate-500" />;
    if (type === "data_pr") {
      if (status === "merged") return <CheckCircle2 size={16} className="text-emerald-500" />;
      if (status === "verifying") return <ShieldCheck size={16} className="text-emerald-500" />;
      return <GitPullRequest size={16} className="text-emerald-500" />;
    }
    return <ServerCog size={16} className="text-slate-400" />;
  };

  return (
    <div className="bg-white border border-[#e2e8f0] rounded-sm shadow-sm overflow-hidden h-[600px] flex flex-col">
      <div className="bg-slate-50 border-b border-[#e2e8f0] px-6 py-4 flex items-center justify-between">
        <h3 className="font-serif font-semibold text-slate-800">Live System Activity</h3>
        <span className="flex h-2 w-2 relative">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
        </span>
      </div>
      
      <div className="flex-1 overflow-y-auto p-6">
        <AnimatePresence mode="popLayout">
          {data.events?.length === 0 ? (
            <motion.div 
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="flex flex-col items-center justify-center h-full text-slate-400 mt-20"
            >
              <FileJson size={32} className="mb-2 opacity-50" />
              <p className="text-sm">No activity recorded yet.</p>
            </motion.div>
          ) : (
            data.events.map((event: any, idx: number) => (
              <motion.div 
                layout
                initial={{ opacity: 0, y: -20, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                transition={{ type: "spring", stiffness: 300, damping: 25 }}
                key={`${event.timestamp}-${idx}`} 
                className="flex gap-4 group mb-6"
              >
                <div className="flex flex-col items-center">
                  <div className="bg-white z-10 py-1">
                    {getIcon(event.type, event.status)}
                  </div>
                  {idx !== data.events.length - 1 && (
                    <div className="w-px h-full bg-slate-200 mt-2"></div>
                  )}
                </div>
                
                <div className="pb-2">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-mono text-slate-400">
                      {format(new Date(event.timestamp), "HH:mm:ss")}
                    </span>
                    <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500 bg-slate-100 px-2 py-0.5 rounded-sm">
                      {event.agent_id?.replace("agent_", "") || "system"}
                    </span>
                  </div>
                  <p className="text-sm text-slate-700 leading-snug font-medium">
                    {event.message}
                  </p>
                  {event.duration_ms && (
                    <p className="text-[10px] text-slate-400 mt-1 font-mono">Duration: {event.duration_ms}ms</p>
                  )}
                </div>
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
