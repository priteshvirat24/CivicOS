"use client";

import useSWR from "swr";
import { API_BASE } from "@/utils/config";
import { ShieldAlert, Server, GitPullRequest, Clock, CheckCircle } from "lucide-react";
import Link from "next/link";
import { formatDistanceToNow, format } from "date-fns";

export default function OpsDashboard() {
  const { data: healthData } = useSWR(`${API_BASE}/api/agents/health`, { refreshInterval: 5000 });
  const { data: prsData } = useSWR(`${API_BASE}/api/prs`, { refreshInterval: 5000 });

  const agents = healthData?.agents || [];
  const prs = prsData || [];

  const openPrs = prs.filter((pr: any) => pr.status === "open" || pr.status === "verifying");
  const failedAgents = agents.filter((a: any) => a.status === "failing" || a.status === "degraded");

  return (
    <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 pb-32">
      <header className="mb-8 border-b border-slate-200 pb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-serif font-bold text-slate-900">Ops Dashboard</h1>
          <p className="text-slate-500 mt-1">Internal operations view and system traceability.</p>
        </div>
        <Link href="/" className="text-sm font-medium text-blue-600 hover:text-blue-800">
          &larr; Back to Public View
        </Link>
      </header>

      {failedAgents.length > 0 && (
        <div className="mb-8 bg-red-50 border border-red-200 rounded-lg p-5 flex items-start gap-4">
          <ShieldAlert className="text-red-500 mt-0.5" />
          <div>
            <h3 className="text-red-800 font-bold mb-1">System Degraded</h3>
            <ul className="text-red-700 text-sm list-disc pl-4 space-y-1">
              {failedAgents.map((agent: any) => (
                <li key={agent.agent_id}>
                  <strong>{agent.agent_id}</strong>: {agent.last_error || "Unknown error"}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Col: Agents Matrix */}
        <div className="lg:col-span-2 space-y-8">
          <section className="bg-white border border-slate-200 rounded-sm shadow-sm overflow-hidden">
            <div className="bg-slate-50 border-b border-slate-200 px-6 py-4 flex items-center gap-2">
              <Server size={18} className="text-slate-500" />
              <h2 className="font-semibold font-serif text-slate-800">Agent Fleet Health</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm whitespace-nowrap">
                <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200">
                  <tr>
                    <th className="px-6 py-3">Agent ID</th>
                    <th className="px-6 py-3">Source</th>
                    <th className="px-6 py-3">Status</th>
                    <th className="px-6 py-3">Last Exec</th>
                    <th className="px-6 py-3">Duration</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {agents.map((agent: any) => (
                    <tr key={agent.agent_id} className="hover:bg-slate-50">
                      <td className="px-6 py-4 font-mono text-xs text-slate-600">{agent.agent_id}</td>
                      <td className="px-6 py-4 text-slate-600 capitalize">{agent.source_id.replace("_", " ")}</td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                          agent.status === "healthy" ? "bg-emerald-100 text-emerald-800" :
                          agent.status === "degraded" ? "bg-amber-100 text-amber-800" :
                          "bg-red-100 text-red-800"
                        }`}>
                          {agent.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-slate-500">
                        {agent.last_run_at ? formatDistanceToNow(new Date(agent.last_run_at), { addSuffix: true }) : "-"}
                      </td>
                      <td className="px-6 py-4 font-mono text-xs text-slate-500">
                        {agent.last_run_duration_ms ? `${agent.last_run_duration_ms}ms` : "-"}
                      </td>
                    </tr>
                  ))}
                  {agents.length === 0 && (
                    <tr><td colSpan={5} className="px-6 py-8 text-center text-slate-400">Loading agents...</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>
        </div>

        {/* Right Col: PRs & Queues */}
        <div className="space-y-8">
          <section className="bg-white border border-slate-200 rounded-sm shadow-sm overflow-hidden">
            <div className="bg-slate-50 border-b border-slate-200 px-6 py-4 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <GitPullRequest size={18} className="text-slate-500" />
                <h2 className="font-semibold font-serif text-slate-800">Verification Queue</h2>
              </div>
              <span className="bg-blue-100 text-blue-800 text-xs font-bold px-2 py-0.5 rounded-full">
                {openPrs.length}
              </span>
            </div>
            <div className="p-0">
              {openPrs.length === 0 ? (
                <div className="p-6 text-center text-slate-400 flex flex-col items-center">
                  <CheckCircle size={24} className="mb-2 text-slate-300" />
                  <p className="text-sm">No pending Data PRs.</p>
                </div>
              ) : (
                <ul className="divide-y divide-slate-100">
                  {openPrs.map((pr: any) => (
                    <li key={pr.id} className="p-4 hover:bg-slate-50">
                      <div className="flex justify-between items-start mb-1">
                        <span className="font-mono text-xs font-semibold text-blue-600">PR #{pr.id.slice(0, 8)}</span>
                        <span className="text-xs bg-amber-100 text-amber-800 px-1.5 rounded uppercase font-bold">{pr.status}</span>
                      </div>
                      <p className="text-xs text-slate-500 font-mono mb-2">Agent: {pr.agent_id || pr.source_id}</p>
                      <div className="flex items-center gap-1 text-[10px] text-slate-400 uppercase font-semibold">
                        <Clock size={12} />
                        {formatDistanceToNow(new Date(pr.created_at), { addSuffix: true })}
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </section>
          
          <section className="bg-white border border-slate-200 rounded-sm shadow-sm overflow-hidden">
             <div className="bg-slate-50 border-b border-slate-200 px-6 py-4">
                <h2 className="font-semibold font-serif text-slate-800">Recent Merges</h2>
             </div>
             <ul className="divide-y divide-slate-100">
               {prs.filter((pr: any) => pr.status === "merged").slice(0, 5).map((pr: any) => (
                 <li key={pr.id} className="p-4 flex justify-between items-center">
                   <div>
                     <p className="font-mono text-xs font-semibold text-emerald-600">PR #{pr.id.slice(0, 8)}</p>
                     <p className="text-xs text-slate-500">{format(new Date(pr.created_at), "MMM d, HH:mm")}</p>
                   </div>
                   <span className="text-[10px] uppercase font-bold text-slate-400 border border-slate-200 px-1 rounded bg-slate-50">
                     v{pr.proposed_dataset_version || "N"}
                   </span>
                 </li>
               ))}
             </ul>
          </section>
        </div>
      </div>
    </main>
  );
}
