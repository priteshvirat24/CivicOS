"use client";

import useSWR from "swr";
import { useState, useMemo } from "react";
import { formatDistanceToNow } from "date-fns";
import { DatasetDrawer } from "./DatasetDrawer";
import { Search, Filter, ShieldCheck, ArrowRight } from "lucide-react";
import { API_BASE } from "@/utils/config";

export function DatasetExplorer() {
  const { data, error } = useSWR(`${API_BASE}/api/dataset/`, {
    refreshInterval: 10000,
  });
  
  const [selectedRecord, setSelectedRecord] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [sourceFilter, setSourceFilter] = useState("all");

  const records = data?.records || [];

  const filteredRecords = useMemo(() => {
    return records.filter((r: any) => {
      const matchesSearch = r.id.toLowerCase().includes(searchQuery.toLowerCase()) || 
                            JSON.stringify(r.data).toLowerCase().includes(searchQuery.toLowerCase());
      const matchesSource = sourceFilter === "all" || r.source_id === sourceFilter;
      return matchesSearch && matchesSource;
    });
  }, [records, searchQuery, sourceFilter]);

  const uniqueSources = useMemo(() => {
    return Array.from(new Set(records.map((r: any) => r.source_id))) as string[];
  }, [records]);

  if (error) return (
    <div className="bg-red-50 text-red-600 rounded-xl p-8 mt-12 text-center">
      <h3 className="font-semibold mb-1">Failed to load dataset</h3>
    </div>
  );

  return (
    <div className="mt-12">
      
      {/* Editorial Header & Controls */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 mb-8 flex flex-col md:flex-row gap-6 items-center justify-between">
        <div>
          <h3 className="font-serif text-2xl font-semibold text-slate-800">Active Canonical Dataset</h3>
          <p className="text-sm text-slate-500 mt-1">
            {records.length} highly-verified civic records. Click any row for deep provenance.
          </p>
        </div>
        
        <div className="flex items-center gap-4 w-full md:w-auto">
          <div className="relative w-full md:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
            <input 
              type="text" 
              placeholder="Search records..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all"
            />
          </div>
          
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
            <select 
              value={sourceFilter}
              onChange={(e) => setSourceFilter(e.target.value)}
              className="pl-9 pr-8 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm appearance-none focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all capitalize"
            >
              <option value="all">All Sources</option>
              {uniqueSources.map(s => (
                <option key={s} value={s}>{s.replace("_", " ")}</option>
              ))}
            </select>
          </div>
        </div>
      </div>
      
      {/* Editorial List */}
      <div className="space-y-3">
        {filteredRecords.length === 0 ? (
          <div className="text-center py-20 bg-slate-50 rounded-2xl border border-slate-200 border-dashed">
            <p className="text-slate-500 font-medium">No records found matching criteria.</p>
          </div>
        ) : (
          filteredRecords.map((record: any) => (
            <div 
              key={record.id} 
              onClick={() => setSelectedRecord(record.id)}
              className="group bg-white border border-slate-200 hover:border-slate-300 hover:shadow-md transition-all rounded-xl p-5 cursor-pointer flex flex-col md:flex-row md:items-center justify-between gap-4"
            >
              <div className="flex items-center gap-6">
                <div className="bg-emerald-50 text-emerald-600 p-3 rounded-lg hidden md:block">
                  <ShieldCheck size={20} />
                </div>
                <div>
                  <div className="flex items-center gap-3 mb-1">
                    <span className="text-xs font-bold font-mono text-slate-400">{record.id.slice(0, 8)}</span>
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-widest bg-blue-50 text-blue-600 border border-blue-100">
                      {record.source_id.replace("_", " ")}
                    </span>
                  </div>
                  <div className="text-sm font-mono text-slate-700 truncate max-w-md">
                    {JSON.stringify(record.data).substring(0, 80)}...
                  </div>
                </div>
              </div>
              
              <div className="flex items-center gap-6 text-slate-400">
                <div className="text-right">
                  <div className="text-[10px] font-bold uppercase tracking-widest mb-1">Last Updated</div>
                  <div className="text-sm font-medium text-slate-600">
                    {formatDistanceToNow(new Date(record.last_updated_at), { addSuffix: true })}
                  </div>
                </div>
                <div className="w-8 h-8 rounded-full bg-slate-50 group-hover:bg-blue-50 group-hover:text-blue-600 flex items-center justify-center transition-colors">
                  <ArrowRight size={16} />
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      <DatasetDrawer 
        recordId={selectedRecord} 
        onClose={() => setSelectedRecord(null)} 
      />
    </div>
  );
}
