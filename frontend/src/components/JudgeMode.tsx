"use client";

import { useState, useEffect, useRef, Suspense, lazy } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Play, Pause, RotateCcw, Activity } from "lucide-react";
import { API_BASE } from "@/utils/config";

const CinematicDataCore = lazy(() => import("./CinematicDataCore"));

interface JudgeModeProps {
  onClose: () => void;
}

export function JudgeMode({ onClose }: JudgeModeProps) {
  const [elapsed, setElapsed] = useState(0);
  const [isPlaying, setIsPlaying] = useState(true);
  const [phase, setPhase] = useState(1);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  
  // Track if we already triggered backend APIs to prevent duplicate calls
  const [hasMutated, setHasMutated] = useState(false);
  const [hasTriggered, setHasTriggered] = useState(false);

  // Master Timeline Sequence
  useEffect(() => {
    if (isPlaying) {
      timerRef.current = setInterval(() => {
        setElapsed((prev) => {
          if (prev >= 30) {
            onClose();
            return 30;
          }
          return prev + 1;
        });
      }, 1000);
    } else if (timerRef.current) {
      clearInterval(timerRef.current);
    }

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isPlaying, onClose]);

  // Phase Calculation based on elapsed seconds
  // 0-5s: Static dashboards dead
  // 5-15s: Agents watching
  // 15-25s: Independent verification
  // 25-30s: Dataset maintains itself
  useEffect(() => {
    if (elapsed < 2) setPhase(1);
    else if (elapsed < 5) setPhase(2);
    else if (elapsed < 10) setPhase(3);
    else if (elapsed < 15) setPhase(4);
    else if (elapsed < 18) setPhase(5);
    else if (elapsed < 23) setPhase(6);
    else if (elapsed < 25) setPhase(7);
    else if (elapsed < 27) setPhase(8);
    else setPhase(9);
    
    // Backend Integrations (Fire and Forget)
    if (elapsed === 10 && !hasMutated) {
      setHasMutated(true);
      fetch(`${API_BASE}/api/demo/mutate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ income_limit: 500000 })
      }).catch(console.error);
    }
    
    if (elapsed === 15 && !hasTriggered) {
      setHasTriggered(true);
      fetch(`${API_BASE}/api/agents/trigger`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ agent_id: "agent_demo_scheme" })
      }).catch(console.error);
    }
    
  }, [elapsed, hasMutated, hasTriggered]);

  const reset = () => {
    setElapsed(0);
    setPhase(1);
    setHasMutated(false);
    setHasTriggered(false);
    setIsPlaying(true);
  };

  // Shared framer motion variants
  const fadeUp = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0, transition: { duration: 0.6 } },
    exit: { opacity: 0, y: -20, transition: { duration: 0.4 } }
  };
  
  const fade = {
    initial: { opacity: 0 },
    animate: { opacity: 1, transition: { duration: 0.6 } },
    exit: { opacity: 0, transition: { duration: 0.4 } }
  };

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-[100] bg-[#fafafa] text-slate-900 overflow-hidden font-sans flex flex-col"
    >
      {/* 3D Background */}
      <div className="absolute inset-0 z-0 opacity-80 pointer-events-none">
        <Suspense fallback={null}>
          <CinematicDataCore phase={phase} />
        </Suspense>
      </div>

      {/* Top Controls Overlay */}
      <div className="absolute top-0 left-0 w-full p-8 flex justify-between items-center z-50">
        <div className="flex items-center gap-4 text-slate-500 font-mono text-sm font-semibold">
          <span>{String(phase).padStart(2, '0')} / 09</span>
          <div className="w-32 h-1 bg-slate-200 rounded-full overflow-hidden">
            <motion.div 
              className="h-full bg-slate-500"
              initial={{ width: "0%" }}
              animate={{ width: `${(elapsed / 30) * 100}%` }}
              transition={{ ease: "linear", duration: 1 }}
            />
          </div>
          <span>0:{String(elapsed).padStart(2, '0')}</span>
        </div>
        
        <div className="flex items-center gap-4">
          <button 
            onClick={() => setIsPlaying(!isPlaying)}
            className="p-3 bg-white border border-slate-200 rounded-full hover:bg-slate-50 transition-colors text-slate-700 shadow-sm"
          >
            {isPlaying ? <Pause size={18} /> : <Play size={18} />}
          </button>
          <button 
            onClick={reset}
            className="p-3 bg-white border border-slate-200 rounded-full hover:bg-slate-50 transition-colors text-slate-700 shadow-sm"
          >
            <RotateCcw size={18} />
          </button>
          <button 
            onClick={onClose}
            className="p-3 bg-white border border-slate-200 rounded-full hover:bg-red-50 hover:text-red-500 hover:border-red-100 transition-colors text-slate-700 shadow-sm"
          >
            <X size={18} />
          </button>
        </div>
      </div>

      {/* Main Cinematic Text Overlay */}
      <div className="flex-1 relative z-10 flex items-center px-12 md:px-24">
        <AnimatePresence mode="wait">
          
          {/* PHASE 1: 0-3s */}
          {phase === 1 && (
            <motion.div key="p1" variants={fadeUp} initial="initial" animate="animate" exit="exit" className="max-w-4xl">
              <h1 className="text-6xl md:text-8xl font-black tracking-tighter leading-[0.95]">
                <motion.span 
                  initial={{ opacity: 1 }} 
                  animate={{ opacity: 0.2 }} 
                  transition={{ duration: 1.5, delay: 1 }}
                >
                  STATIC
                </motion.span><br />
                DASHBOARDS<br />
                ARE DEAD.
              </h1>
              <p className="mt-8 text-2xl text-slate-500 font-medium max-w-lg">
                Public data changes.<br/>Dashboards don't.
              </p>
            </motion.div>
          )}

          {/* PHASE 2: 3-6s */}
          {phase === 2 && (
            <motion.div key="p2" variants={fadeUp} initial="initial" animate="animate" exit="exit" className="max-w-4xl z-10 relative">
              <h2 className="text-5xl md:text-7xl font-black tracking-tighter leading-[0.95] text-white mix-blend-difference">
                WHAT IF THE DATASET<br />WATCHED ITSELF?
              </h2>
            </motion.div>
          )}

          {/* PHASE 3: 6-10s */}
          {phase === 3 && (
            <motion.div key="p3" variants={fade} initial="initial" animate="animate" exit="exit" className="absolute left-12 md:left-24 bottom-24">
              <h3 className="text-3xl font-bold tracking-tight">PUBLIC SOURCES</h3>
              <div className="flex gap-8 mt-4">
                <div className="flex flex-col">
                  <span className="text-4xl font-mono text-emerald-500">8</span>
                  <span className="text-sm font-semibold tracking-widest text-slate-500 uppercase mt-1">Sources</span>
                </div>
                <div className="flex flex-col">
                  <span className="text-4xl font-mono text-blue-500">8</span>
                  <span className="text-sm font-semibold tracking-widest text-slate-500 uppercase mt-1">Owner Agents</span>
                </div>
              </div>
              <motion.div 
                animate={{ opacity: [0.5, 1, 0.5] }} 
                transition={{ repeat: Infinity, duration: 2 }}
                className="mt-8 flex items-center gap-2 text-slate-500 text-sm tracking-widest uppercase font-bold"
              >
                <Activity size={14} /> Watching reality...
              </motion.div>
            </motion.div>
          )}

          {/* PHASE 4: 10-14s */}
          {phase === 4 && (
            <motion.div key="p4" variants={fadeUp} initial="initial" animate="animate" exit="exit" className="absolute left-12 md:left-24 top-1/3">
              <div className="bg-white border border-amber-200 shadow-sm px-6 py-4 rounded-xl backdrop-blur-sm">
                <h3 className="text-amber-500 font-bold tracking-widest uppercase text-sm mb-4 flex items-center gap-2">
                  <div className="w-2 h-2 bg-amber-500 rounded-full animate-ping" />
                  Source Reality Changed
                </h3>
                <div className="font-mono text-slate-700 font-semibold">
                  <div className="flex gap-4">
                    <span className="text-slate-400">Eligibility Limit:</span>
                    <span className="line-through text-slate-400">₹3,00,000</span>
                    <span className="text-amber-500">₹5,00,000</span>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* PHASE 5: 14-18s */}
          {phase === 5 && (
            <motion.div key="p5" variants={fadeUp} initial="initial" animate="animate" exit="exit" className="absolute left-12 md:left-24 top-1/3">
              <h2 className="text-4xl font-bold tracking-tight text-slate-900 mb-2">AGENT 04</h2>
              <h3 className="text-2xl text-blue-600 font-bold mb-6">CHANGE DETECTED</h3>
              
              <motion.div 
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 1 }}
                className="bg-white border border-blue-200 shadow-sm px-6 py-4 rounded-xl backdrop-blur-sm flex items-center gap-4"
              >
                <Activity className="text-blue-500" />
                <span className="font-mono text-blue-700 font-bold tracking-widest">DATA PR CREATED</span>
              </motion.div>
            </motion.div>
          )}

          {/* PHASE 6: 18-22s */}
          {phase === 6 && (
            <motion.div key="p6" variants={fadeUp} initial="initial" animate="animate" exit="exit" className="absolute right-12 md:right-24 top-1/3 text-right">
              <h2 className="text-4xl font-bold tracking-tight text-slate-900 mb-6">VERIFIER AGENT</h2>
              
              <div className="space-y-4 font-mono text-lg font-bold flex flex-col items-end">
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }} className="flex items-center gap-3">
                  <span className="text-slate-600">SOURCE MATCH</span>
                  <span className="text-emerald-500">✓</span>
                </motion.div>
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.5 }} className="flex items-center gap-3">
                  <span className="text-slate-600">SCHEMA VALID</span>
                  <span className="text-emerald-500">✓</span>
                </motion.div>
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 2.5 }} className="flex items-center gap-3">
                  <span className="text-slate-600">PROVENANCE</span>
                  <span className="text-emerald-500">✓</span>
                </motion.div>
              </div>
            </motion.div>
          )}

          {/* PHASE 7: 22-25s */}
          {phase === 7 && (
            <motion.div key="p7" variants={fade} initial="initial" animate="animate" exit="exit" className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div className="text-center z-10">
                <motion.h2 
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  className="text-7xl font-black text-emerald-500 tracking-tighter"
                  style={{ textShadow: "0 4px 40px rgba(250,250,250,1), 0 0 20px rgba(250,250,250,1), 0 0 10px rgba(250,250,250,1)" }}
                >
                  VERIFIED
                </motion.h2>
                <motion.h3 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 1 }}
                  className="text-4xl font-black text-slate-900 mt-4"
                  style={{ textShadow: "0 4px 40px rgba(250,250,250,1), 0 0 20px rgba(250,250,250,1), 0 0 10px rgba(250,250,250,1)" }}
                >
                  MERGED
                </motion.h3>
              </div>
            </motion.div>
          )}

          {/* PHASE 8: 25-28s */}
          {phase === 8 && (
            <motion.div key="p8" variants={fadeUp} initial="initial" animate="animate" exit="exit" className="absolute right-12 md:right-24 bottom-24 text-right">
              <h2 className="text-4xl font-bold tracking-tight text-slate-900 mb-2">LIVE DATA UPDATED</h2>
              <div className="font-mono font-bold text-2xl mt-4">
                <span className="text-slate-500">DATASET </span>
                <span className="text-slate-400 line-through mr-2">v1.08</span>
                <span className="text-emerald-500">v1.09</span>
              </div>
            </motion.div>
          )}

          {/* PHASE 9: 28-30s */}
          {phase === 9 && (
            <motion.div key="p9" variants={fade} initial="initial" animate="animate" exit="exit" className="absolute inset-0 flex items-center justify-center bg-[#fafafa] z-20">
              <div className="text-center max-w-2xl">
                <h1 className="text-6xl md:text-8xl font-black tracking-tighter text-slate-900">
                  REALITY CHANGED.
                </h1>
                <motion.h1 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 1 }}
                  className="text-6xl md:text-8xl font-black tracking-tighter text-slate-400 mt-4"
                >
                  CIVICOS NOTICED.
                </motion.h1>
                <motion.p 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 2 }}
                  className="mt-12 text-xl text-slate-500 font-serif font-medium"
                >
                  The civic dataset that refuses to go stale.
                </motion.p>
              </div>
            </motion.div>
          )}

        </AnimatePresence>
      </div>
    </motion.div>
  );
}
