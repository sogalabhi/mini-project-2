import { Group, Line, Text } from 'react-konva'
import {
  getSlopePolygonWorld,
  worldPointsToKonva,
} from './canvasGeometry.js'

export default function NailVisuals({ coords, reinforcement, height, length }) {
  const { toPixel } = coords

  if (!reinforcement?.required) return null

  const spacingV = Math.max(0.5, Number(reinforcement.spacing_v_m) || 1.5)
  const nailLength = Math.max(0.5, Number(reinforcement.recommended_length_m) || 3)
  const angleDeg = Number(reinforcement.nail_angle_deg) || 15
  const angleRad = (angleDeg * Math.PI) / 180

  const clipPoints = worldPointsToKonva(
    getSlopePolygonWorld(height, length),
    toPixel,
  )

  const nails = []
  for (let y = spacingV * 0.5; y < height; y += spacingV) {
    const xOnFace = (y / height) * length
    const start = { x: xOnFace, y }
    const end = {
      x: start.x + nailLength * Math.cos(angleRad),
      y: start.y - nailLength * Math.sin(angleRad),
    }
    nails.push({ start, end })
  }

  return (
    <Group
      clipFunc={(ctx) => {
        ctx.beginPath()
        ctx.moveTo(clipPoints[0], clipPoints[1])
        for (let i = 2; i < clipPoints.length; i += 2) {
          ctx.lineTo(clipPoints[i], clipPoints[i + 1])
        }
        ctx.closePath()
      }}
    >
      {nails.map((nail, index) => {
        const p1 = toPixel(nail.start)
        const p2 = toPixel(nail.end)
        return (
          <Line
            key={`nail-${index}`}
            points={[p1.x, p1.y, p2.x, p2.y]}
            stroke="#2563eb"
            strokeWidth={2}
            opacity={0.85}
          />
        )
      })}
      <Text
        x={toPixel({ x: Math.max(0.1, length * 0.05), y: Math.max(0.2, height * 0.95) }).x}
        y={toPixel({ x: Math.max(0.1, length * 0.05), y: Math.max(0.2, height * 0.95) }).y}
        text={`Nails: d${reinforcement.recommended_diameter_mm}mm  L${reinforcement.recommended_length_m}m  Sv ${reinforcement.spacing_v_m}m  Sh ${reinforcement.spacing_h_m}m`}
        fontSize={11}
        fill="#1d4ed8"
      />
    </Group>
  )
}
