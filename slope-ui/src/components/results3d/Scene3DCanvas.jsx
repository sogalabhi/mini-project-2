import { useMemo, useRef } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import * as THREE from 'three'

function PointCloud({ points, pointSize = 0.05, color = '#32449c' }) {
  const geometry = useMemo(() => {
    const g = new THREE.BufferGeometry()
    const array = new Float32Array(points.flatMap((p) => [p.x, p.y, p.z]))
    g.setAttribute('position', new THREE.BufferAttribute(array, 3))
    return g
  }, [points])

  return (
    <points geometry={geometry}>
      <pointsMaterial size={pointSize} color={color} sizeAttenuation />
    </points>
  )
}

function GridBounds({ bounds }) {
  const size = [
    Math.max(0.01, bounds.xMax - bounds.xMin),
    Math.max(0.01, bounds.yMax - bounds.yMin),
    Math.max(0.01, bounds.zMax - bounds.zMin),
  ]
  const center = [(bounds.xMin + bounds.xMax) / 2, (bounds.yMin + bounds.yMax) / 2, (bounds.zMin + bounds.zMax) / 2]
  return (
    <mesh position={center}>
      <boxGeometry args={size} />
      <meshBasicMaterial color="#777" wireframe />
    </mesh>
  )
}

function SlipWireframe({ slipSurface, color }) {
  if (slipSurface.mode !== 'ellipsoid') return null
  const [cx, cy, cz] = slipSurface.center
  const [rx, ry, rz] = slipSurface.radii
  return (
    <mesh position={[cx, cy, cz]} scale={[rx, ry, rz]}>
      <sphereGeometry args={[1, 24, 16]} />
      <meshBasicMaterial color={color} wireframe />
    </mesh>
  )
}

export default function Scene3DCanvas({ model, controls, cameraResetToken }) {
  const orbitRef = useRef(null)

  if (!model) return null
  const overlayColor = controls.overlayMode === 'convergence' ? (model.analysisMeta.converged ? '#008800' : '#cc0000') : '#32449c'

  return (
    <Canvas camera={{ position: [6, 6, 6], fov: 50 }}>
      <ambientLight intensity={0.8} />
      <directionalLight position={[5, 10, 7]} intensity={0.8} />
      {controls.showAxes && <axesHelper args={[3]} />}
      {controls.showGrid && <GridBounds bounds={model.gridBounds} />}
      {controls.showSurface && <PointCloud points={model.topSurfacePoints} pointSize={controls.pointSize} color={overlayColor} />}
      {controls.showSlip && <SlipWireframe slipSurface={model.slipSurface} color="#e67300" />}
      <OrbitControls
        ref={orbitRef}
        makeDefault
        key={cameraResetToken}
      />
    </Canvas>
  )
}

