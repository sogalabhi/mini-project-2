import { Line } from 'react-konva'

export default function WaterTableLine({ coords, water, height, length }) {
  const { toPixel } = coords

  if (!water.enabled || height <= 0 || length <= 0) return null

  const depth = Math.min(Math.max(water.depth ?? 0, 0), height)
  const yWorld = height - depth
  const xIntersect = Math.max(0, Math.min(length, (yWorld * length) / height))
  const p1 = toPixel({ x: xIntersect, y: yWorld })
  const p2 = toPixel({ x: length, y: yWorld })

  return (
    <Line
      points={[p1.x, p1.y, p2.x, p2.y]}
      stroke="#38bdf8"
      strokeWidth={2}
      dash={[6, 4]}
    />
  )
}

