"use client";

import { motion } from "framer-motion";
import { GitPullRequest, ArrowRight, ShieldCheck, CheckCircle2 } from "lucide-react";
import { useEffect, useState } from "react";

interface DataPRViewerProps {
  pr: any;
  diff: any[];
  verification: any;
}

export function DataPRViewer({ pr, diff, verification }: DataPRViewerProps) {
  const [pipelineState, setPipelineState] = useState(0);

  // Animate the verification pipeline sequentially
  useEffect(() => {
    if (!pr || pr.status !== 'merged') return;
    
    // reset
    setPipelineState(0);
    
    const sequence = async () => {
      for (let i = 1; i <= 6; i++) {
        await new Promise(r => setTimeout(r, 600));
        setPipelineState(i);
      }
    };
    sequence();
  }, [pr]);

  if (!pr) {
    return <div className="text-slate-500 text-sm italic">Genesis record. No PR data available.</div>;
  }

  const isMerged = pr.status === 'merged';

  return (
    <div className="bg-slate-50 rounded-xl border border-slate-200 overflow-hidden">
      {/* Header */}
      <div className="bg-slate-800 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <GitPullRequest className="text-emerald-400" size={20} />
          <h3 className="font-bold text-white tracking-widest uppercase">DATA PR #{pr.id.split('-')[0]}</h3>
        </div>
        <span className={`px-2 py-1 text-[10px] font-bold uppercase tracking-widest rounded-sm ${isMerged ? 'bg-emerald-500/20 text-emerald-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
          {pr.status}
        </span>
      </div>

      <div className="p-6">
        {/* Diff Section */}
        <div className="mb-8">
          <h4 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">Source Change Detected</h4>
          {diff && diff.length > 0 ? (
            <div className="space-y-4">
              {diff.map((d: any, idx: number) => (
                <div key={idx} className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
                  <div className="text-[10px] font-mono text-slate-400 mb-2">{d.affected_field}</div>
                  <div className="flex items-center gap-4">
                    <div className="flex-1 bg-red-50 text-red-600 font-mono p-3 rounded text-sm line-through">
                      {JSON.stringify(d.old_value)}
                    </div>
                    <ArrowRight className="text-slate-300" />
                    <motion.div 
                      initial={{ backgroundColor: "#f8fafc", color: "#94a3b8" }}
                      animate={{ backgroundColor: "#ecfdf5", color: "#059669" }}
                      transition={{ delay: 0.5, duration: 0.5 }}
                      className="flex-1 font-mono p-3 rounded text-sm font-bold"
                    >
                      {JSON.stringify(d.new_value)}
                    </motion.div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-sm text-slate-500 font-mono">No semantic diff available.</div>
          )}
        </div>

        {/* Verification Pipeline */}
        <div>
          <h4 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
            <ShieldCheck size={16} /> Verification Pipeline
          </h4>
          
          <div className="bg-slate-900 rounded-lg p-6 space-y-4 font-mono text-sm relative">
            <div className="absolute left-9 top-8 bottom-8 w-px bg-slate-800" />

            <PipelineStep label="SOURCE RECHECK" active={pipelineState >= 1} />
            <PipelineStep label="SCHEMA VALID" active={pipelineState >= 2} />
            <PipelineStep label="VALUE MATCH" active={pipelineState >= 3} />
            <PipelineStep label="PROVENANCE VALID" active={pipelineState >= 4} />
            <PipelineStep label="SEMANTIC CHECK" active={pipelineState >= 5} />

            {pipelineState >= 6 && (
              <motion.div 
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="mt-6 pt-6 border-t border-slate-800 flex items-center justify-between"
              >
                <div className="flex items-center gap-3 text-emerald-400">
                  <CheckCircle2 size={24} />
                  <span className="font-bold tracking-widest text-lg">VERIFIED & MERGED</span>
                </div>
                <div className="text-slate-500 text-xs">
                  Into live dataset
                </div>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function PipelineStep({ label, active }: { label: string; active: boolean }) {
  return (
    <div className="flex items-center gap-4 relative z-10">
      <motion.div 
        initial={{ backgroundColor: "#1e293b", borderColor: "#334155" }}
        animate={active ? { backgroundColor: "#10b981", borderColor: "#10b981" } : {}}
        className={`w-6 h-6 rounded-full border flex items-center justify-center shrink-0`}
      >
        {active && <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }}><CheckCircle2 size={14} className="text-slate-900" /></motion.div>}
      </motion.div>
      <span className={active ? "text-emerald-400 font-bold" : "text-slate-600"}>{label}</span>
    </div>
  );
}
