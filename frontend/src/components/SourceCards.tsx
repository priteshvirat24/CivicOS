"use client";

import useSWR from "swr";
import { formatDistanceToNow } from "date-fns";
import { CheckCircle, AlertTriangle } from "lucide-react";
import clsx from "clsx";

import { API_BASE } from "@/utils/config";
import { SkeletonCard } from "./Skeletons";

export function SourceCards() {
  const { data, error } = useSWR(`${API_BASE}/api/agents/health`, {
    refreshInterval: 5000,
  });

  if (error) return (
    <div className="bg-red-50 border border-red-200 text-red-600 rounded-lg p-6 text-center">
      <h3 className="font-semibold mb-1">Failed to load agents</h3>
    </div>
  );
  
  if (!data) return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      {[1, 2, 3, 4].map(i => <SkeletonCard key={i} />)}
    </div>
  );

  const getStatusColor = (status: string) => {
    if (status === "healthy" || status === "recovered") return "border-[#e2e8f0]";
    if (status === "degraded") return "border-amber-300 bg-amber-50";
    if (status === "failing") return "border-red-300 bg-red-50";
    if (status === "offline") return "border-slate-300 bg-slate-100";
    return "border-[#e2e8f0]";
  };

  const getStatusIcon = (status: string) => {
    if (status === "healthy" || status === "recovered") return <CheckCircle size={20} className="text-emerald-500" strokeWidth={1.5} />;
    if (status === "degraded") return <AlertTriangle size={20} className="text-amber-500" strokeWidth={1.5} />;
    if (status === "failing") return <AlertTriangle size={20} className="text-red-500" strokeWidth={1.5} />;
    if (status === "offline") return <AlertTriangle size={20} className="text-slate-400" strokeWidth={1.5} />;
    return <CheckCircle size={20} className="text-emerald-500" strokeWidth={1.5} />;
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      {data.agents.map((agent: any) => (
        <div 
          key={agent.agent_id} 
          className={clsx(
            "border rounded-sm p-5 shadow-sm transition-colors",
            getStatusColor(agent.status)
          )}
        >
          <div className="flex justify-between items-start mb-4">
            <div>
              <h4 className="font-serif font-semibold text-slate-800 capitalize flex items-center gap-2">
                {agent.source_id.replace("_", " ")}
                {agent.status && agent.status !== "healthy" && (
                  <span className="text-[10px] font-mono uppercase bg-black/5 px-1.5 rounded-sm text-slate-600">
                    {agent.status}
                  </span>
                )}
              </h4>
              <p className="text-xs text-slate-500 font-mono mt-1">ID: {agent.agent_id}</p>
            </div>
            {getStatusIcon(agent.status)}
          </div>
          
          <div className="space-y-2 mt-4 text-sm">
            <div className="flex justify-between border-b border-slate-100 pb-2">
              <span className="text-slate-500">Last Checked</span>
              <span className="text-slate-900 font-medium">
                {agent.last_run_at ? formatDistanceToNow(new Date(agent.last_run_at), { addSuffix: true }) : "Never"}
              </span>
            </div>
            
            <div className="flex justify-between border-b border-slate-100 pb-2">
              <span className="text-slate-500">Last Change</span>
              <span className="text-slate-900 font-medium">
                {agent.last_change_detected_at ? formatDistanceToNow(new Date(agent.last_change_detected_at), { addSuffix: true }) : "None"}
              </span>
            </div>
            
            <div className="flex justify-between pt-1">
              <span className="text-slate-500">Run Speed</span>
              <span className="text-slate-900 font-mono text-xs">
                {agent.last_run_duration_ms ? `${agent.last_run_duration_ms}ms` : "-"}
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
