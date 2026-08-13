"use client";

import { useRef, useMemo, useState } from 'react';
import { Canvas, useFrame, ThreeEvent } from '@react-three/fiber';
import { Icosahedron, Sphere, Line, OrbitControls, Html } from '@react-three/drei';
import * as THREE from 'three';
import { X, Activity, Database, CheckCircle, Search, Server } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const CORE_COLOR = "#f8fafc";
const CORE_WIREFRAME = "#94a3b8";
const AGENT_COLOR = "#0ea5e9";
const SOURCE_COLOR = "#475569";
const CONNECTION_COLOR = "#cbd5e1";
const HOVER_COLOR = "#3b82f6";
const VERIFIER_COLOR = "#10b981";

type NodeType = 'source' | 'agent' | 'core' | 'verifier' | null;

interface SelectedNode {
  type: NodeType;
  id: number | null;
}

function Core({ hovered, selected }: { hovered: SelectedNode, selected: SelectedNode }) {
  const meshRef = useRef<THREE.Mesh>(null);
  const wireframeRef = useRef<THREE.Mesh>(null);

  const isHighlighted = hovered.type === 'core' || selected.type === 'core' || hovered.type === 'verifier' || selected.type === 'verifier';
  const opacity = hovered.type && !isHighlighted ? 0.3 : 1;

  useFrame(() => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.002;
      meshRef.current.rotation.x += 0.001;
    }
    if (wireframeRef.current) {
      wireframeRef.current.rotation.y -= 0.001;
      wireframeRef.current.rotation.x -= 0.002;
    }
  });

  return (
    <group>
      <Icosahedron ref={meshRef} args={[2, 1]}>
        <meshStandardMaterial color={CORE_COLOR} roughness={0.2} metalness={0.8} transparent opacity={opacity} />
      </Icosahedron>
      <Icosahedron ref={wireframeRef} args={[2.2, 1]}>
        <meshBasicMaterial color={CORE_WIREFRAME} wireframe transparent opacity={opacity * 0.2} />
      </Icosahedron>
    </group>
  );
}

function OrbitingNodes({ 
  hovered, 
  setHovered, 
  selected, 
  setSelected 
}: { 
  hovered: SelectedNode, 
  setHovered: (n: SelectedNode) => void,
  selected: SelectedNode,
  setSelected: (n: SelectedNode) => void
}) {
  const groupRef = useRef<THREE.Group>(null);
  
  const nodes = useMemo(() => {
    const items = [];
    for (let i = 0; i < 8; i++) {
      const angle = (i / 8) * Math.PI * 2;
      const sourceRadius = 5.5;
      const sx = Math.cos(angle) * sourceRadius;
      const sz = Math.sin(angle) * sourceRadius;
      
      const agentRadius = 3.5;
      const ax = Math.cos(angle) * agentRadius;
      const az = Math.sin(angle) * agentRadius;

      items.push({
        sourcePos: new THREE.Vector3(sx, 0, sz),
        agentPos: new THREE.Vector3(ax, 0, az),
        id: i
      });
    }
    return items;
  }, []);

  // Verifier node between agents and core
  const verifierPos = useMemo(() => new THREE.Vector3(0, 2.5, 0), []);

  useFrame((state) => {
    if (groupRef.current) {
      // Very slow rotation to allow clicking easily
      groupRef.current.rotation.y = state.clock.elapsedTime * 0.02;
    }
  });

  const handlePointerOver = (e: ThreeEvent<MouseEvent>, type: NodeType, id: number | null) => {
    e.stopPropagation();
    document.body.style.cursor = 'pointer';
    setHovered({ type, id });
  };

  const handlePointerOut = (e: ThreeEvent<MouseEvent>) => {
    e.stopPropagation();
    document.body.style.cursor = 'default';
    setHovered({ type: null, id: null });
  };

  const handleClick = (e: ThreeEvent<MouseEvent>, type: NodeType, id: number | null) => {
    e.stopPropagation();
    setSelected({ type, id });
  };

  return (
    <group ref={groupRef}>
      {/* Verifier Node */}
      <group>
        <Sphere 
          position={verifierPos} 
          args={[0.3, 16, 16]}
          onPointerOver={(e) => handlePointerOver(e, 'verifier', null)}
          onPointerOut={handlePointerOut}
          onClick={(e) => handleClick(e, 'verifier', null)}
        >
          <meshStandardMaterial 
            color={VERIFIER_COLOR} 
            emissive={VERIFIER_COLOR} 
            emissiveIntensity={(hovered.type === 'verifier' || selected.type === 'verifier') ? 0.8 : 0.2}
            transparent 
            opacity={hovered.type && hovered.type !== 'verifier' && selected.type !== 'verifier' ? 0.2 : 1}
          />
        </Sphere>
        <Html position={[verifierPos.x, verifierPos.y + 0.5, verifierPos.z]} center className="pointer-events-none">
          <div className="text-[10px] font-mono tracking-widest text-emerald-400 font-bold bg-slate-900/50 px-2 py-1 rounded backdrop-blur whitespace-nowrap">VERIFIER</div>
        </Html>
      </group>

      {nodes.map((node) => {
        const isHoveredSource = hovered.type === 'source' && hovered.id === node.id;
        const isHoveredAgent = hovered.type === 'agent' && hovered.id === node.id;
        const isSelectedSource = selected.type === 'source' && selected.id === node.id;
        const isSelectedAgent = selected.type === 'agent' && selected.id === node.id;
        
        // When hovering/selecting a source, its agent is also highlighted. Same in reverse.
        const isActiveFlow = isHoveredSource || isHoveredAgent || isSelectedSource || isSelectedAgent;
        const opacity = (hovered.type || selected.type) && !isActiveFlow ? 0.1 : 1;

        return (
          <group key={node.id}>
            {/* Source Node */}
            <Sphere 
              position={node.sourcePos} 
              args={[(isHoveredSource || isSelectedSource) ? 0.25 : 0.2, 16, 16]}
              onPointerOver={(e) => handlePointerOver(e, 'source', node.id)}
              onPointerOut={handlePointerOut}
              onClick={(e) => handleClick(e, 'source', node.id)}
            >
              <meshStandardMaterial 
                color={isActiveFlow ? HOVER_COLOR : SOURCE_COLOR} 
                roughness={0.7} 
                transparent 
                opacity={opacity}
              />
            </Sphere>
            {(isActiveFlow) && (
              <Html position={[node.sourcePos.x, node.sourcePos.y + 0.4, node.sourcePos.z]} center className="pointer-events-none">
                <div className="text-[10px] font-mono tracking-widest text-blue-400 font-bold bg-slate-900/50 px-2 py-1 rounded backdrop-blur whitespace-nowrap">SOURCE 0{node.id + 1}</div>
              </Html>
            )}
            
            {/* Agent Node */}
            <Sphere 
              position={node.agentPos} 
              args={[(isHoveredAgent || isSelectedAgent) ? 0.2 : 0.15, 16, 16]}
              onPointerOver={(e) => handlePointerOver(e, 'agent', node.id)}
              onPointerOut={handlePointerOut}
              onClick={(e) => handleClick(e, 'agent', node.id)}
            >
              <meshStandardMaterial 
                color={isActiveFlow ? HOVER_COLOR : AGENT_COLOR} 
                emissive={isActiveFlow ? HOVER_COLOR : AGENT_COLOR} 
                emissiveIntensity={isActiveFlow ? 0.8 : 0.4} 
                transparent 
                opacity={opacity}
              />
            </Sphere>
            {(isActiveFlow) && (
              <Html position={[node.agentPos.x, node.agentPos.y - 0.4, node.agentPos.z]} center className="pointer-events-none">
                <div className="text-[10px] font-mono tracking-widest text-blue-400 font-bold bg-slate-900/50 px-2 py-1 rounded backdrop-blur whitespace-nowrap">AGENT 0{node.id + 1}</div>
              </Html>
            )}
            
            {/* Connection: Source -> Agent */}
            <Line
              points={[node.sourcePos, node.agentPos]}
              color={isActiveFlow ? HOVER_COLOR : CONNECTION_COLOR}
              transparent
              opacity={isActiveFlow ? 0.8 : opacity * 0.3}
              lineWidth={isActiveFlow ? 2 : 1}
            />
            
            {/* Connection: Agent -> Verifier/Core */}
            <Line
              points={[node.agentPos, isActiveFlow ? verifierPos : new THREE.Vector3(0, 0, 0)]}
              color={isActiveFlow ? HOVER_COLOR : AGENT_COLOR}
              transparent
              opacity={isActiveFlow ? 0.8 : opacity * 0.4}
              lineWidth={isActiveFlow ? 2 : 1}
            />
          </group>
        );
      })}
    </group>
  );
}

function SidePanel({ selected, onClose }: { selected: SelectedNode, onClose: () => void }) {
  if (!selected.type) return null;

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      className="absolute top-4 right-4 bottom-4 w-80 bg-white/90 backdrop-blur shadow-2xl rounded-xl border border-slate-200 p-6 overflow-y-auto z-10"
    >
      <button onClick={onClose} className="absolute top-4 right-4 text-slate-400 hover:text-slate-600">
        <X size={20} />
      </button>

      {selected.type === 'source' && (
        <div className="mt-4">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 bg-slate-100 rounded-lg text-slate-600"><Server size={24} /></div>
            <div>
              <h3 className="font-bold text-slate-900">PUBLIC SOURCE 0{selected.id! + 1}</h3>
              <p className="text-xs font-mono text-slate-500">api.example.gov/dataset</p>
            </div>
          </div>
          <div className="space-y-4 text-sm">
            <div className="flex justify-between border-b border-slate-100 pb-2">
              <span className="text-slate-500">Status</span>
              <span className="font-semibold text-emerald-600 flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-emerald-500" /> ACTIVE</span>
            </div>
            <div className="flex justify-between border-b border-slate-100 pb-2">
              <span className="text-slate-500">Owner Agent</span>
              <span className="font-semibold text-blue-600 font-mono">AGENT 0{selected.id! + 1}</span>
            </div>
            <div className="flex justify-between border-b border-slate-100 pb-2">
              <span className="text-slate-500">Last Checked</span>
              <span className="font-semibold text-slate-700">12s ago</span>
            </div>
            <div className="flex justify-between border-b border-slate-100 pb-2">
              <span className="text-slate-500">Last Changed</span>
              <span className="font-semibold text-slate-700">2h ago</span>
            </div>
            <div className="flex justify-between border-b border-slate-100 pb-2">
              <span className="text-slate-500">Records</span>
              <span className="font-semibold text-slate-700">14,204</span>
            </div>
          </div>
        </div>
      )}

      {selected.type === 'agent' && (
        <div className="mt-4">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 bg-blue-50 rounded-lg text-blue-600"><Search size={24} /></div>
            <div>
              <h3 className="font-bold text-slate-900">AGENT 0{selected.id! + 1}</h3>
              <p className="text-xs font-mono text-blue-600">Autonomous Observer</p>
            </div>
          </div>
          <div className="space-y-4 text-sm">
            <div className="flex justify-between border-b border-slate-100 pb-2">
              <span className="text-slate-500">State</span>
              <span className="font-semibold text-emerald-600 flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" /> WATCHING</span>
            </div>
            <div className="flex justify-between border-b border-slate-100 pb-2">
              <span className="text-slate-500">Target Source</span>
              <span className="font-semibold text-slate-700 font-mono">SOURCE 0{selected.id! + 1}</span>
            </div>
            <div className="flex justify-between border-b border-slate-100 pb-2">
              <span className="text-slate-500">Last Run</span>
              <span className="font-semibold text-slate-700">12s ago</span>
            </div>
            <div className="flex flex-col gap-2 pt-2">
              <span className="text-slate-500 font-semibold text-xs tracking-wider uppercase">Recent Activity</span>
              <div className="bg-slate-50 p-3 rounded font-mono text-xs text-slate-600 space-y-2">
                <div>[10:42:01] No change detected.</div>
                <div>[10:41:01] No change detected.</div>
                <div className="text-blue-600">[08:21:04] Change detected! PR #104 opened.</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {selected.type === 'verifier' && (
        <div className="mt-4">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 bg-emerald-50 rounded-lg text-emerald-600"><CheckCircle size={24} /></div>
            <div>
              <h3 className="font-bold text-slate-900">VERIFIER AGENT</h3>
              <p className="text-xs font-mono text-emerald-600">Gatekeeper</p>
            </div>
          </div>
          <p className="text-sm text-slate-600 mb-6">
            Independently verifies all Data PRs proposed by Owner Agents before they are merged into the Canonical Dataset.
          </p>
          <div className="space-y-4 text-sm font-mono bg-slate-900 text-emerald-400 p-4 rounded-lg">
            <div className="flex justify-between items-center">
              <span>Source Match</span>
              <span>✓</span>
            </div>
            <div className="flex justify-between items-center">
              <span>Schema Valid</span>
              <span>✓</span>
            </div>
            <div className="flex justify-between items-center">
              <span>Provenance</span>
              <span>✓</span>
            </div>
            <div className="flex justify-between items-center text-slate-500">
              <span>Semantic Check</span>
              <span>...</span>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  );
}

export function InteractiveArchitecture() {
  const [hovered, setHovered] = useState<SelectedNode>({ type: null, id: null });
  const [selected, setSelected] = useState<SelectedNode>({ type: null, id: null });

  return (
    <div className="w-full h-[600px] relative bg-slate-50 rounded-3xl border border-slate-200 overflow-hidden shadow-inner hidden md:block">
      
      {/* Instructional Overlay */}
      <div className="absolute top-6 left-6 pointer-events-none z-10">
        <h3 className="text-sm font-bold tracking-widest text-slate-400 uppercase flex items-center gap-2">
          <Activity size={16} /> Interactive Architecture
        </h3>
        <p className="text-slate-500 text-sm mt-2 max-w-xs">
          Hover or click on sources, agents, or the verifier to inspect the data pipeline.
        </p>
      </div>

      <Canvas camera={{ position: [0, 4, 12], fov: 45 }} dpr={[1, 2]} performance={{ min: 0.5 }}>
        <ambientLight intensity={0.4} />
        <directionalLight position={[10, 10, 5]} intensity={1.5} color="#ffffff" />
        <directionalLight position={[-10, -10, -5]} intensity={0.5} color="#94a3b8" />
        <pointLight position={[0, 0, 0]} intensity={2} color={AGENT_COLOR} distance={8} />

        <OrbitControls 
          enablePan={false} 
          minDistance={8} 
          maxDistance={20}
          minPolarAngle={Math.PI / 4}
          maxPolarAngle={Math.PI / 2.5}
        />
        
        <Core hovered={hovered} selected={selected} />
        <OrbitingNodes hovered={hovered} setHovered={setHovered} selected={selected} setSelected={setSelected} />
      </Canvas>

      {/* HTML Overlay Panel */}
      <AnimatePresence>
        {selected.type && (
          <SidePanel selected={selected} onClose={() => setSelected({ type: null, id: null })} />
        )}
      </AnimatePresence>
    </div>
  );
}
