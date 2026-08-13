"use client";

import useSWR from "swr";
import { format } from "date-fns";
import { motion, AnimatePresence } from "framer-motion";
import { X, ShieldCheck, Database, Server, Link, Hash, Activity, Calendar } from "lucide-react";
import { DataPRViewer } from "./DataPRViewer";
import { API_BASE } from "@/utils/config";

const fetcher = (url: string) => fetch(url).then((res) => res.json());

interface DatasetDrawerProps {
  recordId: string | null;
  onClose: () => void;
}

export function DatasetDrawer({ recordId, onClose }: DatasetDrawerProps) {
  return (
    <AnimatePresence>
      {recordId && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50"
          />

          {/* Drawer */}
          <motion.div
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="fixed top-0 right-0 h-full w-full max-w-3xl bg-white shadow-2xl z-50 overflow-y-auto border-l border-slate-200 flex flex-col"
          >
            {/* Header */}
            <div className="bg-slate-50 border-b border-slate-200 px-8 py-6 flex items-center justify-between sticky top-0 z-10">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <Database size={16} className="text-slate-400" />
                  <span className="text-xs font-bold tracking-widest text-slate-500 uppercase">Dataset Record</span>
                </div>
                <h2 className="text-2xl font-serif font-semibold text-slate-800 font-mono">{recordId}</h2>
              </div>
              <button 
                onClick={onClose}
                className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-full transition-colors"
              >
                <X size={24} />
              </button>
            </div>

            {/* Content */}
            <div className="p-8 flex-1">
              <DrawerContent recordId={recordId} />
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

function DrawerContent({ recordId }: { recordId: string }) {
  const { data, error } = useSWR(`${API_BASE}/api/dataset/${recordId}/provenance`, fetcher);

  if (error) return <div className="text-red-500 p-4 bg-red-50 rounded border border-red-200">Failed to load provenance chain.</div>;
  if (!data) return (
    <div className="space-y-6 animate-pulse">
      <div className="h-48 bg-slate-100 rounded-xl w-full"></div>
      <div className="h-64 bg-slate-100 rounded-xl w-full"></div>
    </div>
  );

  const { record, pr, diff, verification, source_evidence } = data;

  return (
    <div className="space-y-12">
      
      {/* 1. CURRENT VALUE */}
      <section>
        <h3 className="text-xs font-bold tracking-widest text-slate-500 uppercase mb-4">Current Value</h3>
        <div className="bg-slate-900 rounded-xl p-6 shadow-inner">
          <pre className="text-emerald-400 font-mono text-sm overflow-x-auto">
            {JSON.stringify(record.data, null, 2)}
          </pre>
        </div>
      </section>

      {/* 2. PROVENANCE METADATA */}
      <section>
        <h3 className="text-xs font-bold tracking-widest text-slate-500 uppercase mb-4 flex items-center gap-2">
          <ShieldCheck size={16} /> Immutable Provenance
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <ProvenanceCard 
            icon={<Server size={14} />} 
            label="Original Source" 
            value={record.source_id.replace("_", " ")} 
            highlight
          />
          <ProvenanceCard 
            icon={<Link size={14} />} 
            label="Source URL" 
            value={record.provenance?.source_url || "N/A"} 
            isLink
          />
          <ProvenanceCard 
            icon={<Activity size={14} />} 
            label="Owner Agent" 
            value={record.provenance?.agent_id || "System"} 
          />
          <ProvenanceCard 
            icon={<Calendar size={14} />} 
            label="Observed At" 
            value={format(new Date(record.last_updated_at), "PPP 'at' HH:mm:ss")} 
          />
          <ProvenanceCard 
            icon={<ShieldCheck size={14} />} 
            label="Verifier" 
            value={verification ? "System Verifier" : "N/A"} 
          />
          <ProvenanceCard 
            icon={<Hash size={14} />} 
            label="Agent Run ID" 
            value={pr?.agent_run_id || "N/A"} 
            mono
          />
          <ProvenanceCard 
            label="Schema Version" 
            value={record.schema_version} 
            mono
          />
          <ProvenanceCard 
            label="Normalization Version" 
            value={record.normalization_version} 
            mono
          />
        </div>
      </section>

      {/* 3. DATA PR */}
      <section>
        <DataPRViewer pr={pr} diff={diff} verification={verification} />
      </section>

      {/* 4. SOURCE EVIDENCE */}
      {source_evidence && (
        <section>
          <h3 className="text-xs font-bold tracking-widest text-slate-500 uppercase mb-4">Source Evidence Snapshot</h3>
          <div className="bg-slate-50 rounded-xl p-6 border border-slate-200">
            <pre className="text-slate-600 font-mono text-[10px] overflow-x-auto max-h-64">
              {source_evidence}
            </pre>
          </div>
        </section>
      )}

    </div>
  );
}

function ProvenanceCard({ icon, label, value, highlight, isLink, mono }: any) {
  return (
    <div className={`p-4 rounded-lg border ${highlight ? 'bg-blue-50/50 border-blue-100' : 'bg-white border-slate-100'}`}>
      <div className="flex items-center gap-1.5 text-slate-400 mb-1">
        {icon}
        <span className="text-[10px] font-bold uppercase tracking-widest">{label}</span>
      </div>
      <div className={`text-sm text-slate-700 truncate ${mono ? 'font-mono' : 'font-medium'} ${highlight ? 'text-blue-700 capitalize' : ''}`}>
        {isLink && value !== "N/A" ? (
          <a href={value} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline">{value}</a>
        ) : value}
      </div>
    </div>
  );
}
