"use client";

import { useRef, useMemo, useEffect, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Icosahedron, Sphere, Line } from '@react-three/drei';
import * as THREE from 'three';

const CORE_COLOR = "#1e293b"; // slate-800 for contrast
const CORE_WIREFRAME = "#94a3b8";
const AGENT_COLOR = "#0ea5e9";
const SOURCE_COLOR = "#475569";
const CONNECTION_COLOR = "#cbd5e1";

const ALERT_COLOR = "#f59e0b"; // amber-500
const SUCCESS_COLOR = "#10b981"; // emerald-500

function Core({ phase }: { phase: number }) {
  const meshRef = useRef<THREE.Mesh>(null);
  const wireframeRef = useRef<THREE.Mesh>(null);
  const materialRef = useRef<THREE.MeshStandardMaterial>(null);

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.002;
      meshRef.current.rotation.x += 0.001;
    }
    if (wireframeRef.current) {
      wireframeRef.current.rotation.y -= 0.001;
      wireframeRef.current.rotation.x -= 0.002;
      
      // Phase 7 (Merged): Large pulse
      let pulse = 0;
      if (phase === 7) {
        pulse = Math.sin(state.clock.elapsedTime * 8) * 0.1;
      } else {
        pulse = Math.sin(state.clock.elapsedTime * 2) * 0.02;
      }
      
      const scale = 1 + pulse;
      wireframeRef.current.scale.set(scale, scale, scale);
    }
    
    // Core turns green briefly on phase 7
    if (materialRef.current) {
      const targetColor = new THREE.Color(phase === 7 ? SUCCESS_COLOR : CORE_COLOR);
      materialRef.current.color.lerp(targetColor, 0.1);
    }
  });

  return (
    <group visible={phase >= 2}>
      <Icosahedron ref={meshRef} args={[2, 1]}>
        <meshStandardMaterial ref={materialRef} color={CORE_COLOR} roughness={0.2} metalness={0.8} />
      </Icosahedron>
      <Icosahedron ref={wireframeRef} args={[2.2, 1]}>
        <meshBasicMaterial color={CORE_WIREFRAME} wireframe transparent opacity={0.2} />
      </Icosahedron>
    </group>
  );
}

function OrbitingNodes({ phase }: { phase: number }) {
  const groupRef = useRef<THREE.Group>(null);
  
  // Track packet position
  const [packetProgress, setPacketProgress] = useState(0);

  const nodes = useMemo(() => {
    const items = [];
    for (let i = 0; i < 8; i++) {
      const angle = (i / 8) * Math.PI * 2;
      const sourceRadius = 5.5;
      const sx = Math.cos(angle) * sourceRadius;
      const sz = Math.sin(angle) * sourceRadius;
      const sy = Math.sin(angle * 3) * 1.5;
      
      const agentRadius = 3.5;
      const ax = Math.cos(angle + 0.2) * agentRadius;
      const az = Math.sin(angle + 0.2) * agentRadius;
      const ay = Math.sin(angle * 2) * 1.0;

      items.push({
        sourcePos: new THREE.Vector3(sx, sy, sz),
        agentPos: new THREE.Vector3(ax, ay, az),
        id: i
      });
    }
    return items;
  }, []);

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = state.clock.elapsedTime * 0.05;
      groupRef.current.rotation.z = Math.sin(state.clock.elapsedTime * 0.2) * 0.1;
    }
    
    // Animate packet in phase 5
    if (phase === 5) {
      setPacketProgress((p) => Math.min(1, p + 0.015));
    } else {
      setPacketProgress(0);
    }
  });

  const demoNodeIndex = 4; // Arbitrarily pick node 4 to be the active one
  const activeNode = nodes[demoNodeIndex];
  
  // Calculate packet position (Source -> Agent -> Core)
  const packetPos = new THREE.Vector3();
  if (phase === 5) {
    if (packetProgress < 0.5) {
      // Source to Agent
      const normalizedP = packetProgress * 2; // 0 to 1
      packetPos.copy(activeNode.sourcePos).lerp(activeNode.agentPos, normalizedP);
    } else {
      // Agent to Core
      const normalizedP = (packetProgress - 0.5) * 2; // 0 to 1
      packetPos.copy(activeNode.agentPos).lerp(new THREE.Vector3(0,0,0), normalizedP);
    }
  }

  return (
    <group ref={groupRef} visible={phase >= 3}>
      {nodes.map((node) => {
        const isDemo = node.id === demoNodeIndex;
        // Node colors based on phase
        const sourceColor = isDemo && (phase === 4 || phase === 5) ? ALERT_COLOR : SOURCE_COLOR;
        const agentColor = isDemo && (phase === 5 || phase === 6) ? ALERT_COLOR : AGENT_COLOR;
        const lineColor = isDemo && phase >= 4 && phase <= 6 ? ALERT_COLOR : CONNECTION_COLOR;

        return (
          <group key={node.id}>
            {/* Source */}
            <Sphere position={node.sourcePos} args={[isDemo && phase === 4 ? 0.25 : 0.15, 16, 16]}>
              <meshStandardMaterial color={sourceColor} roughness={0.7} />
            </Sphere>
            
            {/* Agent */}
            <Sphere position={node.agentPos} args={[isDemo && phase === 5 ? 0.2 : 0.1, 16, 16]}>
              <meshStandardMaterial color={agentColor} emissive={agentColor} emissiveIntensity={0.5} />
            </Sphere>
            
            {/* Connection: Source -> Agent */}
            <Line
              points={[node.sourcePos, node.agentPos]}
              color={lineColor}
              transparent
              opacity={0.3}
              lineWidth={1}
            />
            
            {/* Connection: Agent -> Core */}
            <Line
              points={[node.agentPos, new THREE.Vector3(0, 0, 0)]}
              color={isDemo && phase >= 5 && phase <= 7 ? ALERT_COLOR : AGENT_COLOR}
              transparent
              opacity={0.4}
              lineWidth={1.5}
            />
          </group>
        );
      })}
      
      {/* Moving Packet */}
      {phase === 5 && packetProgress > 0 && packetProgress < 1 && (
        <Sphere position={packetPos} args={[0.08, 16, 16]}>
          <meshBasicMaterial color={ALERT_COLOR} />
        </Sphere>
      )}
    </group>
  );
}

function Scene({ phase }: { phase: number }) {
  useFrame((state) => {
    // Subtle camera parallax
    if (phase < 8) {
      state.camera.position.x = THREE.MathUtils.lerp(state.camera.position.x, (state.mouse.x * 3), 0.05);
      state.camera.position.y = THREE.MathUtils.lerp(state.camera.position.y, (state.mouse.y * 3) + 2, 0.05);
    } else {
      // Zoom in slightly at the end
      state.camera.position.x = THREE.MathUtils.lerp(state.camera.position.x, 0, 0.05);
      state.camera.position.y = THREE.MathUtils.lerp(state.camera.position.y, 1, 0.05);
      state.camera.position.z = THREE.MathUtils.lerp(state.camera.position.z, 6, 0.05);
    }
    state.camera.lookAt(0, 0, 0);
  });

  return (
    <>
      <ambientLight intensity={0.4} />
      <directionalLight position={[10, 10, 5]} intensity={1.5} color="#ffffff" />
      <directionalLight position={[-10, -10, -5]} intensity={0.5} color="#94a3b8" />
      <pointLight position={[0, 0, 0]} intensity={phase === 7 ? 4 : 2} color={phase === 7 ? SUCCESS_COLOR : AGENT_COLOR} distance={8} />
      
      <Core phase={phase} />
      <OrbitingNodes phase={phase} />
    </>
  );
}

export default function CinematicDataCore({ phase }: { phase: number }) {
  return (
    <div className="w-full h-full relative cursor-default">
      <Canvas camera={{ position: [0, 2, 22], fov: 45 }} dpr={[1, 2]} performance={{ min: 0.5 }}>
        <Scene phase={phase} />
      </Canvas>
    </div>
  );
}
