"use client";

import useSWR from "swr";
import { useState } from "react";
import { formatDistanceToNow } from "date-fns";
import { ProvenancePanel } from "./ProvenancePanel";
import { SkeletonTable } from "./Skeletons";
import { API_BASE } from "@/utils/config";

export function DatasetExplorer() {
  const { data, error } = useSWR(`${API_BASE}/api/dataset/`, {
    refreshInterval: 10000,
  });
  
  const [expandedRecord, setExpandedRecord] = useState<string | null>(null);

  if (error) return (
    <div className="bg-red-50 border border-red-200 text-red-600 rounded-lg p-6 mt-12 text-center">
      <h3 className="font-semibold mb-1">Failed to load dataset</h3>
      <p className="text-sm">The backend API could not be reached. Please check the connection.</p>
    </div>
  );
  
  if (!data) return <div className="mt-12"><SkeletonTable /></div>;

  const records = data.records || [];

  return (
    <div className="bg-white border border-[#e2e8f0] rounded-sm shadow-sm overflow-hidden mt-12">
      <div className="bg-slate-50 border-b border-[#e2e8f0] px-6 py-5">
        <h3 className="font-serif font-semibold text-slate-800 text-lg">Active Canonical Dataset</h3>
        <p className="text-sm text-slate-500 mt-1">
          Explore the live data. Every record exposes verifiable provenance to its original source.
        </p>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-[#e2e8f0]">
            <tr>
              <th className="px-6 py-4 font-serif">Record ID</th>
              <th className="px-6 py-4 font-serif">Source</th>
              <th className="px-6 py-4 font-serif">Last Updated</th>
              <th className="px-6 py-4 font-serif text-right">Provenance</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#e2e8f0]">
            {records.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-6 py-12 text-center text-slate-500 bg-white">
                  <p className="font-medium text-slate-700 mb-1">No active records found</p>
                  <p className="text-sm">Trigger the agent or wait for the next polling cycle to populate the dataset.</p>
                </td>
              </tr>
            ) : (
              records.map((record: any) => (
                <tr key={record.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-4 font-mono text-xs text-slate-600">
                    {record.id.slice(0, 8)}
                  </td>
                  <td className="px-6 py-4">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-800 capitalize border border-slate-200 shadow-sm">
                      {record.source_id.replace("_", " ")}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-slate-500">
                    {formatDistanceToNow(new Date(record.last_updated_at), { addSuffix: true })}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button 
                      onClick={() => setExpandedRecord(expandedRecord === record.id ? null : record.id)}
                      className="text-xs font-semibold text-blue-600 hover:text-blue-800 uppercase tracking-wider"
                    >
                      {expandedRecord === record.id ? "Hide Details" : "View Details"}
                    </button>
                  </td>
                </tr>
              ))
            )}
            
            {records.map((record: any) => 
              expandedRecord === record.id ? (
                <tr key={`${record.id}-details`}>
                  <td colSpan={4} className="p-0 border-b border-[#e2e8f0]">
                    <ProvenancePanel recordId={record.id} />
                  </td>
                </tr>
              ) : null
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
