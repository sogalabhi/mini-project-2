import { Line } from 'react-konva'

export default function WaterTableLine({ coords, water, height }) {
  const { worldW, toPixel } = coords

  if (!water.enabled) return null

  const depth = Math.min(water.depth ?? 0, height)
  const yWorld = height - depth
  const p1 = toPixel({ x: 0, y: yWorld })
  const p2 = toPixel({ x: worldW, y: yWorld })

  return (
    <Line
      points={[p1.x, p1.y, p2.x, p2.y]}
      stroke="#38bdf8"
      strokeWidth={2}
      dash={[6, 4]}
    />
  )
}

