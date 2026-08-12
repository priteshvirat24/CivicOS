import Link from "next/link";
import { ArrowLeft, ShieldCheck, Activity, Layers, Lock, Code2 } from "lucide-react";

export default function MethodologyPage() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 selection:bg-blue-100 font-sans">
      <header className="bg-white border-b border-[#e2e8f0] sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link href="/" className="text-slate-400 hover:text-slate-600 transition-colors">
              <ArrowLeft size={20} />
            </Link>
            <h1 className="font-serif font-bold text-xl text-slate-900 tracking-tight">CivicOS</h1>
          </div>
          <nav className="text-sm font-medium text-slate-500">
            Methodology
          </nav>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-6 py-16">
        <div className="mb-16">
          <h1 className="font-serif text-4xl font-bold text-slate-900 mb-6 leading-tight">
            Trust Through Transparency: <br/> How CivicOS Maintains Data
          </h1>
          <p className="text-lg text-slate-600 leading-relaxed">
            A static dashboard is fundamentally indefensible. When a user asks, "Why should I trust this data?", we believe the only acceptable answer is a cryptographic, reproducible trail of evidence. This page outlines the agentic methodology behind CivicOS.
          </p>
        </div>

        <div className="space-y-16">
          
          <section>
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center shrink-0">
                <Activity size={20} />
              </div>
              <h2 className="font-serif text-2xl font-bold text-slate-900">Continuous Monitoring</h2>
            </div>
            <p className="text-slate-600 leading-relaxed mb-4">
              CivicOS does not rely on manual data entry. We deploy a fleet of independent, specialized autonomous agents. Each agent is responsible for exactly one slice of civic data. They run in parallel, polling and observing their respective canonical sources.
            </p>
            <ul className="list-disc list-inside text-slate-600 space-y-2 ml-4">
              <li>Agents isolate failures: If the transit API goes offline, the health API continues uninterrupted.</li>
              <li>Agents self-heal: They gracefully degrade during schema drift and automatically recover when the source is fixed.</li>
            </ul>
          </section>

          <section>
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center shrink-0">
                <Code2 size={20} />
              </div>
              <h2 className="font-serif text-2xl font-bold text-slate-900">The Data PR Workflow</h2>
            </div>
            <p className="text-slate-600 leading-relaxed mb-4">
              When an agent detects a semantic change, it does not silently overwrite production data. Instead, it opens a <strong>Data Pull Request (Data PR)</strong>. 
            </p>
            <p className="text-slate-600 leading-relaxed mb-4">
              This Data PR contains a precise diff of the fields changed, the raw source payload at the time of observation, and a cryptographic hash. The PR acts as a deterministic proposal to increment the global dataset version.
            </p>
          </section>

          <section>
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-full bg-amber-100 text-amber-600 flex items-center justify-center shrink-0">
                <ShieldCheck size={20} />
              </div>
              <h2 className="font-serif text-2xl font-bold text-slate-900">Independent Verification</h2>
            </div>
            <p className="text-slate-600 leading-relaxed mb-4">
              A proposed change is never trusted blindly. A secondary <strong>Verifier Agent</strong> intercepts the Data PR. It independently inspects the schema, verifies data types, and validates semantic constraints. Only if the verifier approves the PR is it merged into the active dataset.
            </p>
          </section>

          <section>
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center shrink-0">
                <Lock size={20} />
              </div>
              <h2 className="font-serif text-2xl font-bold text-slate-900">Immutable Audit Trail</h2>
            </div>
            <p className="text-slate-600 leading-relaxed mb-4">
              Every action in the system—agent runs, PR creation, verification, and merges—is recorded in a cryptographically signed audit ledger.
            </p>
            <p className="text-slate-600 leading-relaxed">
              Each ledger entry hashes its own payload along with the signature of the previous entry. This Merkle-like chain guarantees that the dataset's history cannot be silently modified without invalidating the entire chain. You can inspect this history for any record via the Provenance Panel.
            </p>
          </section>

        </div>
      </main>
      
      <footer className="bg-slate-900 text-slate-400 py-12 text-center mt-20">
        <p className="text-sm">CivicOS &copy; {new Date().getFullYear()} — Defensible Civic Data</p>
      </footer>
    </div>
  );
}
