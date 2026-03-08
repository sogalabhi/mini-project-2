import { useEffect, useRef, useState } from 'react'
import { Stage, Layer } from 'react-konva'
import { useGeometryStore } from '../../store/geometryStore.js'
import { useMaterialsStore } from '../../store/materialsStore.js'
import { useLoadsStore } from '../../store/loadsStore.js'
import { useWaterStore } from '../../store/waterStore.js'
import { useCanvasCoords } from '../../hooks/useCanvasCoords.js'
import GridBackground from './GridBackground.jsx'
import SoilLayerBands from './SoilLayerBands.jsx'
import WaterTableLine from './WaterTableLine.jsx'
import SlopeShape from './SlopeShape.jsx'
import LoadArrows from './LoadArrows.jsx'
import DimensionLabels from './DimensionLabels.jsx'

export default function SlopeCanvas() {
  const containerRef = useRef(null)
  const [size, setSize] = useState({ w: 800, h: 480 })

  useEffect(() => {
    if (!containerRef.current) return
    const ro = new ResizeObserver((entries) => {
      const { width, height } = entries[0].contentRect
      setSize({ w: Math.floor(width), h: Math.floor(height) })
    })
    ro.observe(containerRef.current)
    return () => ro.disconnect()
  }, [])

  const { height, angle, length } = useGeometryStore()
  const { layers } = useMaterialsStore()
  const { udls, lineLoads } = useLoadsStore()
  const water = useWaterStore()

  const H = height || 10
  const A = angle || 30
  const L =
    length != null
      ? length
      : Number((H / Math.tan((A * Math.PI) / 180 || 1)).toFixed(2))

  const coords = useCanvasCoords(size.w, size.h, H, L)

  return (
    <div
      ref={containerRef}
      className="h-full w-full"
    >
      <Stage width={size.w} height={size.h}>
        <Layer>
          <GridBackground coords={coords} />
        </Layer>
        <Layer>
          <SoilLayerBands
            coords={coords}
            layers={layers}
            height={H}
          />
        </Layer>
        <Layer>
          <WaterTableLine
            coords={coords}
            water={water}
            height={H}
          />
        </Layer>
        <Layer>
          <SlopeShape
            coords={coords}
            height={H}
            length={L}
          />
        </Layer>
        <Layer>
          <LoadArrows
            coords={coords}
            udls={udls}
            lineLoads={lineLoads}
            height={H}
          />
        </Layer>
        <Layer>
          <DimensionLabels
            coords={coords}
            height={H}
            angle={A}
            length={L}
          />
        </Layer>
      </Stage>
    </div>
  )
}

