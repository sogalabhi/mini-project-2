import { Line, Circle } from 'react-konva'
import { useGeometryStore } from '../../store/geometryStore.js'
import {
  getSlopePolygonWorld,
  worldPointsToKonva,
} from './canvasGeometry.js'

export default function SlopeShape({ coords, height, length }) {
  const { toPixel } = coords
  const setGeometry = useGeometryStore((s) => s.setGeometry)

  const toeWorld = { x: 0, y: 0 }
  const crestWorld = { x: length, y: height }

  const toe = toPixel(toeWorld)
  const crest = toPixel(crestWorld)
  const polygonPoints = worldPointsToKonva(
    getSlopePolygonWorld(height, length),
    toPixel,
  )

  const handleDragMove = () => (e) => {
    const pos = e.target.position()
    const { x, y } = coords.toWorld(pos)
    const newLength = Math.max(1, x)
    const newHeight = Math.max(1, y)
    setGeometry(newHeight, newLength)
  }

  return (
    <>
      <Line
        points={polygonPoints}
        closed
        fill="rgba(240, 240, 240, 0.45)"
        stroke="#000000"
        strokeWidth={2}
      />
      <Line
        points={[toe.x, toe.y, crest.x, crest.y]}
        stroke="#000000"
        strokeWidth={2}
      />
      <Line
        points={[toe.x, toe.y, crest.x, toe.y]}
        stroke="#000000"
        strokeWidth={2}
      />
      <Line
        points={[crest.x, crest.y, crest.x, toe.y]}
        stroke="#000000"
        strokeWidth={2}
      />
      <Circle
        x={crest.x}
        y={crest.y}
        radius={7}
        fill="#ffffff"
        stroke="#000000"
        strokeWidth={1.5}
        draggable
        onDragMove={handleDragMove()}
      />
    </>
  )
}

