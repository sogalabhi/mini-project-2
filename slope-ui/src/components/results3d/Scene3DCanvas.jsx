import { useMemo, useRef } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import * as THREE from 'three'
import { triangulateStructuredGrid } from '../../utils/terrainTriangulation.js'
import { triangulateUserSlip } from '../../utils/slipTriangulation.js'
import { scalarToHeatColor } from '../../utils/heatmapScale.js'

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

function SlipWireframe({ slipSurface, color, opacity }) {
  if (slipSurface.mode !== 'ellipsoid') return null
  const [cx, cy, cz] = slipSurface.center
  const [rx, ry, rz] = slipSurface.radii
  return (
    <mesh position={[cx, cy, cz]} scale={[rx, ry, rz]}>
      <sphereGeometry args={[1, 24, 16]} />
      <meshBasicMaterial color={color} wireframe transparent opacity={opacity} />
    </mesh>
  )
}

function TerrainMesh({ points, opacity }) {
  const { vertices, indices } = useMemo(() => triangulateStructuredGrid(points), [points])
  if (!vertices.length || !indices.length) return null
  const geometry = useMemo(() => {
    const g = new THREE.BufferGeometry()
    g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(vertices), 3))
    g.setIndex(indices)
    g.computeVertexNormals()
    return g
  }, [vertices, indices])
  return (
    <mesh geometry={geometry}>
      <meshStandardMaterial color="#5d8a5a" transparent opacity={opacity} side={THREE.DoubleSide} />
    </mesh>
  )
}

function SlipMesh({ slipSurface, opacity }) {
  const meshData = useMemo(() => {
    if (slipSurface.mode === 'ellipsoid') {
      const sphere = new THREE.SphereGeometry(1, 20, 14)
      return { geometry: sphere, transform: { position: slipSurface.center, scale: slipSurface.radii } }
    }
    const { vertices, indices } = triangulateUserSlip(slipSurface.userDefinedPoints || [])
    if (!vertices.length || !indices.length) return null
    const g = new THREE.BufferGeometry()
    g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(vertices), 3))
    g.setIndex(indices)
    g.computeVertexNormals()
    return { geometry: g, transform: null }
  }, [slipSurface])
  if (!meshData) return null
  if (meshData.transform) {
    return (
      <mesh position={meshData.transform.position} scale={meshData.transform.scale} geometry={meshData.geometry}>
        <meshStandardMaterial color="#e67300" transparent opacity={opacity} side={THREE.DoubleSide} />
      </mesh>
    )
  }
  return (
    <mesh geometry={meshData.geometry}>
      <meshStandardMaterial color="#e67300" transparent opacity={opacity} side={THREE.DoubleSide} />
    </mesh>
  )
}

function ColumnCenters({ centers, pointSize, selectedId, fsField, heatmapEnabled }) {
  const geometry = useMemo(() => {
    const g = new THREE.BufferGeometry()
    const array = new Float32Array(centers.flatMap((p) => [p.x, p.y, p.z]))
    g.setAttribute('position', new THREE.BufferAttribute(array, 3))
    return g
  }, [centers])
  const defaultColor = heatmapEnabled ? '#e67300' : '#32449c'
  const selected = selectedId != null ? centers.find((c) => Number(c.columnId) === Number(selectedId)) : null
  const selectedColor =
    selected && heatmapEnabled
      ? scalarToHeatColor(fsField.scalarByColumnId?.[String(selected.columnId)], fsField.min, fsField.max)
      : '#ff00ff'
  return (
    <>
      <points geometry={geometry}>
        <pointsMaterial size={pointSize} color={defaultColor} sizeAttenuation />
      </points>
      {selected && (
        <mesh position={[selected.x, selected.y, selected.z]}>
          <sphereGeometry args={[pointSize * 2, 10, 10]} />
          <meshBasicMaterial color={selectedColor} />
        </mesh>
      )}
    </>
  )
}

function ColumnLines({ lines, selectedId, fsField, heatmapEnabled }) {
  return (
    <>
      {lines.map((line) => {
        const isSelected = selectedId != null && Number(line.columnId) === Number(selectedId)
        const color = heatmapEnabled
          ? scalarToHeatColor(fsField.scalarByColumnId?.[String(line.columnId)], fsField.min, fsField.max)
          : isSelected
            ? '#ff00ff'
            : '#32449c'
        const points = [
          new THREE.Vector3(line.x, line.y, line.zBase),
          new THREE.Vector3(line.x, line.y, line.zTop),
        ]
        const geometry = new THREE.BufferGeometry().setFromPoints(points)
        return (
          <line key={`col-line-${line.columnId}`} geometry={geometry}>
            <lineBasicMaterial color={color} />
          </line>
        )
      })}
    </>
  )
}

function ColumnPrisms({ columns, opacity, fsField, heatmapEnabled }) {
  return (
    <>
      {columns.map((c) => {
        const h = Math.max(0.01, c.zTop - c.zBase)
        const color = heatmapEnabled
          ? scalarToHeatColor(fsField.scalarByColumnId?.[String(c.columnId)], fsField.min, fsField.max)
          : '#7b8cc4'
        return (
          <mesh key={`prism-${c.columnId}`} position={[c.xCenter, c.yCenter, c.zBase + h / 2]}>
            <boxGeometry args={[0.95, 0.95, h]} />
            <meshStandardMaterial color={color} transparent opacity={opacity} wireframe={h > 2.5} />
          </mesh>
        )
      })}
    </>
  )
}

function MorphologyOverlay({ morphology, points }) {
  if (!morphology || !points?.length) return null
  const crest = (morphology.crest_ids || []).map((i) => points[i]).filter(Boolean)
  const face = (morphology.face_ids || []).map((i) => points[i]).filter(Boolean)
  const toe = (morphology.toe_ids || []).map((i) => points[i]).filter(Boolean)
  return (
    <>
      <PointCloud points={crest} pointSize={0.08} color="#cc0000" />
      <PointCloud points={face} pointSize={0.06} color="#e67300" />
      <PointCloud points={toe} pointSize={0.08} color="#008800" />
    </>
  )
}

export default function Scene3DCanvas({ model, controls, cameraResetToken, selectedColumnId }) {
  const orbitRef = useRef(null)

  if (!model) return null
  const overlayColor =
    controls.overlayMode === 'convergence' ? (model.analysisMeta.converged ? '#008800' : '#cc0000') : '#32449c'
  const heatmapEnabled = controls.overlayMode === 'fs_heatmap' && Number.isFinite(model.fsField?.min) && Number.isFinite(model.fsField?.max)
  const prismCap = Math.max(100, Number(controls.prismMaxColumns) || 1500)
  const columns = model.columnGeometry?.columns || []
  const prismAllowed = columns.length <= prismCap

  return (
    <Canvas camera={{ position: [6, 6, 6], fov: 50 }}>
      <ambientLight intensity={0.8} />
      <directionalLight position={[5, 10, 7]} intensity={0.8} />
      {controls.showAxes && <axesHelper args={[3]} />}
      {controls.showGrid && <GridBounds bounds={model.gridBounds} />}
      {controls.showSurface && <PointCloud points={model.topSurfacePoints} pointSize={controls.pointSize} color={overlayColor} />}
      {controls.showTerrainMesh && <TerrainMesh points={model.terrainMesh.points} opacity={controls.meshOpacity} />}
      {controls.showSlip && <SlipWireframe slipSurface={model.slipSurface} color="#e67300" opacity={controls.meshOpacity} />}
      {controls.showSlipMesh && <SlipMesh slipSurface={model.slipSurface} opacity={controls.meshOpacity} />}
      {controls.showColumnCenters && (
        <ColumnCenters
          centers={model.columnGeometry?.centers || []}
          pointSize={controls.pointSize}
          selectedId={selectedColumnId}
          fsField={model.fsField}
          heatmapEnabled={heatmapEnabled}
        />
      )}
      {controls.showColumnLines && (
        <ColumnLines
          lines={model.columnGeometry?.lines || []}
          selectedId={selectedColumnId}
          fsField={model.fsField}
          heatmapEnabled={heatmapEnabled}
        />
      )}
      {controls.showColumnPrisms && prismAllowed && (
        <ColumnPrisms columns={columns} opacity={controls.meshOpacity} fsField={model.fsField} heatmapEnabled={heatmapEnabled} />
      )}
      {controls.showMorphology && <MorphologyOverlay morphology={model.morphology} points={model.topSurfacePoints} />}
      <OrbitControls
        ref={orbitRef}
        makeDefault
        key={cameraResetToken}
      />
    </Canvas>
  )
}

