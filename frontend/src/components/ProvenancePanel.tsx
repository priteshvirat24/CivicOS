"use client";

import useSWR from "swr";
import { format } from "date-fns";
import { Hash, Link, ShieldCheck, GitPullRequest, Activity, History, FileText } from "lucide-react";
import ReactMarkdown from 'react-markdown';
import { API_BASE } from "@/utils/config";

const fetcher = (url: string) => fetch(url).then((res) => res.json());

export function ProvenancePanel({ recordId }: { recordId: string }) {
  const { data, error } = useSWR(`${API_BASE}/api/dataset/${recordId}/provenance`, fetcher);

  if (error) return <div className="p-6 text-red-500 text-sm">Failed to load provenance chain.</div>;
  if (!data) return <div className="p-6 animate-pulse"><div className="h-4 bg-slate-200 rounded w-full"></div></div>;

  const { record, pr, change, diff, verification, source_evidence, audit_trail } = data;

  return (
    <div className="bg-slate-50 p-6 border-b border-[#e2e8f0]">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Column 1: Record Details */}
        <div className="space-y-6">
          <div>
            <h5 className="font-semibold text-slate-800 text-xs uppercase tracking-wider mb-4 flex items-center gap-2">
              <ShieldCheck size={14} className="text-emerald-600" />
              Verified Record Details
            </h5>
            <div className="space-y-3">
              <div className="flex justify-between items-center bg-white p-2 rounded border border-slate-200">
                <span className="text-xs text-slate-500">Source</span>
                <span className="text-xs font-mono font-medium text-slate-800 capitalize">{record.source_id.replace("_", " ")}</span>
              </div>
              <div className="flex justify-between items-center bg-white p-2 rounded border border-slate-200">
                <span className="text-xs text-slate-500">Schema Version</span>
                <span className="text-xs font-mono font-medium text-slate-800">{record.schema_version}</span>
              </div>
              <div className="flex justify-between items-center bg-white p-2 rounded border border-slate-200">
                <span className="text-xs text-slate-500">Normalization</span>
                <span className="text-xs font-mono font-medium text-slate-800">{record.normalization_version}</span>
              </div>
              <div className="flex justify-between items-center bg-white p-2 rounded border border-slate-200">
                <span className="text-xs text-slate-500">Owner Agent</span>
                <span className="text-xs font-mono font-medium text-blue-600">{record.provenance?.agent_id || "Unknown"}</span>
              </div>
            </div>
          </div>
          
          <div>
            <h5 className="font-semibold text-slate-800 text-xs uppercase tracking-wider mb-3">Payload Data</h5>
            <pre className="bg-slate-900 text-emerald-400 p-4 rounded-sm text-xs font-mono overflow-auto max-h-40 shadow-inner">
              {JSON.stringify(record.data, null, 2)}
            </pre>
          </div>
        </div>

        {/* Column 2: Data PR & Diff */}
        <div className="space-y-6">
          <div>
            <h5 className="font-semibold text-slate-800 text-xs uppercase tracking-wider mb-4 flex items-center gap-2">
              <GitPullRequest size={14} className="text-blue-600" />
              Data PR Origin
            </h5>
            {pr ? (
              <div className="bg-white p-3 rounded border border-slate-200 space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-xs text-slate-500">PR ID</span>
                  <span className="text-xs font-mono text-slate-800">{pr.id.split('-')[0]}...</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-slate-500">Status</span>
                  <span className="text-xs font-mono font-medium text-emerald-600 uppercase">{pr.status}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-xs text-slate-500">Created At</span>
                  <span className="text-xs font-mono text-slate-800">{format(new Date(pr.created_at), "MMM d, HH:mm:ss")}</span>
                </div>
                {pr.agent_run_id && (
                  <div className="flex justify-between items-center mt-2 pt-2 border-t border-slate-100">
                    <span className="text-xs text-slate-500">Agent Run ID</span>
                    <span className="text-xs font-mono text-slate-400" title={pr.agent_run_id}>
                      {pr.agent_run_id.split('-')[0]}...
                    </span>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-xs text-slate-500 italic">Genesis record, no PR history.</p>
            )}
          </div>

          <div>
            <h5 className="font-semibold text-slate-800 text-xs uppercase tracking-wider mb-3">Change Diff</h5>
            {diff && diff.length > 0 ? (
              <div className="space-y-2">
                {diff.map((d: any, idx: number) => (
                  <div key={idx} className="bg-white border rounded text-xs font-mono overflow-hidden">
                    <div className="bg-slate-100 p-1.5 border-b font-semibold text-slate-600">{d.affected_field}</div>
                    <div className="p-2 bg-red-50 text-red-700 line-through">
                      - {JSON.stringify(d.old_value)}
                    </div>
                    <div className="p-2 bg-emerald-50 text-emerald-700">
                      + {JSON.stringify(d.new_value)}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-500 italic">No semantic diff available.</p>
            )}
          </div>
        </div>

        {/* Column 3: Evidence & Audit Trail */}
        <div className="space-y-6">
          <div>
            <h5 className="font-semibold text-slate-800 text-xs uppercase tracking-wider mb-4 flex items-center gap-2">
              <FileText size={14} className="text-purple-600" />
              Source Evidence
            </h5>
            <div className="space-y-3">
              <div className="flex items-start gap-2">
                <Link size={14} className="text-slate-400 mt-0.5 shrink-0" />
                <a href={record.provenance?.source_url} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline text-xs break-all">
                  {record.provenance?.source_url || "N/A"}
                </a>
              </div>
              
              {source_evidence && (
                <div className="mt-2">
                  <p className="text-[10px] uppercase text-slate-500 mb-1">Raw Snapshot</p>
                  <pre className="bg-white border border-slate-200 p-2 rounded-sm text-[10px] font-mono overflow-auto max-h-32 text-slate-600">
                    {source_evidence}
                  </pre>
                </div>
              )}
            </div>
          </div>

          <div>
            <h5 className="font-semibold text-slate-800 text-xs uppercase tracking-wider mb-4 flex items-center gap-2">
              <History size={14} className="text-amber-600" />
              Immutable Audit Trail
            </h5>
            {audit_trail && audit_trail.length > 0 ? (
              <div className="space-y-3 relative before:absolute before:inset-0 before:ml-2 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-200 before:to-transparent">
                {audit_trail.map((audit: any, idx: number) => (
                  <div key={audit.id} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group">
                    <div className="flex items-center justify-center w-4 h-4 rounded-full bg-slate-200 border-2 border-white shrink-0 z-10 mx-auto" />
                    <div className="w-[calc(100%-2rem)] md:w-[calc(50%-1.5rem)] bg-white p-2 rounded border border-slate-200 shadow-sm text-left">
                      <div className="flex justify-between items-center mb-1">
                        <span className="font-semibold text-[10px] uppercase text-slate-800">{audit.action}</span>
                        <span className="text-[10px] text-slate-400 font-mono">{format(new Date(audit.timestamp), "HH:mm:ss")}</span>
                      </div>
                      <p className="text-[10px] text-slate-500">
                        Actor: <span className="font-mono text-blue-600">{audit.actor}</span>
                      </p>
                      <div className="mt-1 flex items-center gap-1 text-[8px] text-slate-400 font-mono truncate cursor-help" title={`Signature: ${audit.signature}`}>
                        <Hash size={10} /> {audit.signature?.slice(0,16)}...
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-500 italic">No audit events found.</p>
            )}
          </div>
        </div>
        
      </div>
    </div>
  );
}
