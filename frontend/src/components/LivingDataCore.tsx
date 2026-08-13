"use client";

import { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Icosahedron, Sphere, Line } from '@react-three/drei';
import * as THREE from 'three';

const CORE_COLOR = "#f8fafc"; // slate-50 (warm white)
const CORE_WIREFRAME = "#94a3b8"; // slate-400
const AGENT_COLOR = "#0ea5e9"; // sky-500 (accent)
const SOURCE_COLOR = "#475569"; // slate-600
const CONNECTION_COLOR = "#cbd5e1"; // slate-300

function Core() {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.002;
      meshRef.current.rotation.x += 0.001;
    }
  });

  return (
    <group>
      <Icosahedron ref={meshRef} args={[2, 1]}>
        <meshStandardMaterial color={CORE_COLOR} roughness={0.2} metalness={0.8} />
      </Icosahedron>
    </group>
  );
}

function OrbitingNodes() {
  const groupRef = useRef<THREE.Group>(null);

  const nodes = useMemo(() => {
    const items = [];
    // 8 Sources (outer orbit) and 8 Agents (inner orbit)
    for (let i = 0; i < 8; i++) {
      const angle = (i / 8) * Math.PI * 2;

      // Source position
      const sourceRadius = 5.5;
      const sx = Math.cos(angle) * sourceRadius;
      const sz = Math.sin(angle) * sourceRadius;
      const sy = Math.sin(angle * 3) * 1.5;

      // Agent position
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
  });

  return (
    <group ref={groupRef}>
      {nodes.map((node) => (
        <group key={node.id}>
          {/* Source */}
          <Sphere position={node.sourcePos} args={[0.15, 16, 16]}>
            <meshStandardMaterial color={SOURCE_COLOR} roughness={0.7} />
          </Sphere>

          {/* Agent */}
          <Sphere position={node.agentPos} args={[0.1, 16, 16]}>
            <meshStandardMaterial color={AGENT_COLOR} emissive={AGENT_COLOR} emissiveIntensity={0.5} />
          </Sphere>

          {/* Connection: Source -> Agent */}
          <Line
            points={[node.sourcePos, node.agentPos]}
            color={CONNECTION_COLOR}
            transparent
            opacity={0.3}
            lineWidth={1}
          />

          {/* Connection: Agent -> Core */}
          <Line
            points={[node.agentPos, new THREE.Vector3(0, 0, 0)]}
            color={AGENT_COLOR}
            transparent
            opacity={0.4}
            lineWidth={1.5}
          />
        </group>
      ))}
    </group>
  );
}

function Scene() {
  useFrame((state) => {
    // Subtle camera parallax based on mouse
    state.camera.position.x = THREE.MathUtils.lerp(state.camera.position.x, (state.mouse.x * 2), 0.05);
    state.camera.position.y = THREE.MathUtils.lerp(state.camera.position.y, (state.mouse.y * 2) + 2, 0.05);
    state.camera.lookAt(0, 0, 0);
  });

  return (
    <>
      <ambientLight intensity={0.4} />
      <directionalLight position={[10, 10, 5]} intensity={1.5} color="#ffffff" />
      <directionalLight position={[-10, -10, -5]} intensity={0.5} color="#94a3b8" />
      <pointLight position={[0, 0, 0]} intensity={2} color={AGENT_COLOR} distance={8} />

      <Core />
      <OrbitingNodes />
    </>
  );
}

export default function LivingDataCore() {
  return (
    <div className="w-full h-full relative cursor-crosshair">
      <Canvas camera={{ position: [0, 2, 16], fov: 45 }} dpr={[1, 2]} performance={{ min: 0.5 }}>
        <Scene />
      </Canvas>
    </div>
  );
}
