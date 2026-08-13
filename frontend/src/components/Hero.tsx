"use client";

import { motion } from "framer-motion";
import { Suspense, lazy } from "react";
import { ArrowRight, Sparkles, Activity } from "lucide-react";

// Lazy load the 3D core so it doesn't block initial render
const LivingDataCore = lazy(() => import("./LivingDataCore"));

export function Hero({ onExperienceClick }: { onExperienceClick: () => void }) {
  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.2, delayChildren: 0.1 }
    }
  };

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { duration: 0.8 } }
  };

  return (
    <div className="w-full min-h-[90vh] flex flex-col relative overflow-hidden bg-[#fafafa]">
      
      {/* Top Navigation */}
      <nav className="w-full max-w-7xl mx-auto px-6 py-8 flex justify-between items-center z-20">
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 1, delay: 0.5 }}
          className="text-xl font-bold tracking-tight text-slate-900"
        >
          CivicOS
        </motion.div>
        
        <motion.div 
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.7 }}
          className="hidden md:flex gap-8 text-sm font-medium text-slate-600"
        >
          <a href="#data" className="hover:text-slate-900 transition-colors">Data</a>
          <a href="#how-it-works" className="hover:text-slate-900 transition-colors">How it Works</a>
          <a href="#sources" className="hover:text-slate-900 transition-colors">Sources</a>
          <a href="#activity" className="hover:text-slate-900 transition-colors">Activity</a>
        </motion.div>
        
        <motion.div 
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 1, delay: 0.5 }}
          className="flex items-center gap-3 bg-white px-4 py-2 rounded-full shadow-sm border border-slate-200"
        >
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
          <span className="text-xs font-semibold tracking-wide text-slate-700">8 AGENTS WATCHING</span>
        </motion.div>
      </nav>

      {/* Main Hero Content */}
      <div className="flex-1 w-full max-w-7xl mx-auto px-6 grid grid-cols-1 lg:grid-cols-2 gap-12 items-center relative z-10 pb-12">
        
        {/* Left: Typography & CTAs */}
        <motion.div 
          variants={container}
          initial="hidden"
          animate="show"
          className="max-w-2xl mt-12 lg:mt-0"
        >
          <motion.h1 
            variants={item}
            className="text-6xl sm:text-7xl lg:text-8xl font-black font-sans text-slate-900 tracking-tighter leading-[0.95]"
          >
            STATIC<br />
            DASHBOARDS<br />
            ARE DEAD.
          </motion.h1>

          <motion.p 
            variants={item}
            className="mt-6 text-xl sm:text-2xl font-serif text-slate-900 font-semibold max-w-lg leading-snug"
          >
            The civic dataset that refuses to go stale.
          </motion.p>
          
          <motion.p 
            variants={item}
            className="mt-4 text-sm sm:text-base text-slate-500 max-w-lg leading-relaxed font-medium"
          >
            Public data changes every day. CivicOS watches, verifies, and publishes the change.
          </motion.p>
          
          <motion.div variants={item} className="mt-10 flex flex-col sm:flex-row gap-4">
            <button 
              onClick={onExperienceClick}
              className="bg-slate-900 text-white px-8 py-4 font-bold tracking-widest text-xs uppercase flex items-center justify-center gap-3 hover:bg-emerald-600 transition-colors group"
            >
              EXPERIENCE CIVICOS IN 30s 
              <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
            </button>
            <a 
              href="#data"
              className="bg-white text-slate-900 border-2 border-slate-900 px-8 py-4 font-bold tracking-widest text-xs uppercase flex items-center justify-center hover:bg-slate-50 transition-colors"
            >
              EXPLORE LIVE DATA
            </a>
          </motion.div>
        </motion.div>

        {/* Right: 3D Visualization */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1.5, delay: 0.8, ease: "easeOut" }}
          className="h-[400px] lg:h-[700px] w-full relative -mt-6 lg:mt-0 order-first lg:order-last"
        >
          {/* Decorative Labels */}
          <div className="absolute top-1/4 left-12 translate-x-0 z-20 hidden lg:flex items-center gap-2 text-xs font-semibold text-slate-400 uppercase tracking-widest rotate-90 origin-left">
            <div className="w-8 h-px bg-slate-300"></div>
            8 SOURCES
          </div>
          
          <div className="absolute bottom-1/4 right-12 translate-x-0 z-20 hidden lg:flex items-center gap-2 text-xs font-semibold text-slate-400 uppercase tracking-widest -rotate-90 origin-right">
            8 AGENTS
            <div className="w-8 h-px bg-slate-300"></div>
          </div>
          
          <div className="absolute top-8 right-8 z-20 bg-white/80 backdrop-blur-sm px-4 py-2 border border-slate-100 rounded text-xs font-semibold text-slate-500 uppercase tracking-widest shadow-sm">
            1 LIVING DATASET
          </div>

          <Suspense fallback={
            <div className="w-full h-full flex items-center justify-center">
              <div className="w-32 h-32 rounded-full border border-slate-200 animate-pulse flex items-center justify-center">
                <Activity className="text-slate-300" size={32} />
              </div>
            </div>
          }>
            <LivingDataCore />
          </Suspense>
        </motion.div>
      </div>
      
    </div>
  );
}
