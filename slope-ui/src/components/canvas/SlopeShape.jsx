import { Line, Circle } from 'react-konva'
import { useGeometryStore } from '../../store/geometryStore.js'

export default function SlopeShape({ coords, height, length }) {
  const { toPixel } = coords
  const setGeometry = useGeometryStore((s) => s.setGeometry)

  const toeWorld = { x: 0, y: 0 }
  const crestWorld = { x: length, y: height }

  const toe = toPixel(toeWorld)
  const crest = toPixel(crestWorld)

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
        points={[toe.x, toe.y, crest.x, crest.y]}
        stroke="#e5e7eb"
        strokeWidth={3}
      />
      <Line
        points={[toe.x, toe.y, crest.x, toe.y]}
        stroke="#4b5563"
        strokeWidth={2}
      />
      <Line
        points={[crest.x, crest.y, crest.x, toe.y]}
        stroke="#4b5563"
        strokeWidth={2}
      />
      {/* Crest drag handle */}
      <Circle
        x={crest.x}
        y={crest.y}
        radius={7}
        fill="#22c55e"
        stroke="#052e16"
        strokeWidth={1}
        draggable
        onDragMove={handleDragMove()}
      />
    </>
  )
}

