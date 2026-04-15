import { Arrow, Line } from 'react-konva'
import { getSurfaceY } from './canvasGeometry.js'

export default function LoadArrows({ coords, udls, lineLoads, height, length }) {
  const { toPixel } = coords

  const shapes = []
  const norm = Math.sqrt(length * length + height * height) || 1
  const tx = length / norm
  const ty = height / norm
  const nx = -ty
  const ny = tx

  udls.forEach((load) => {
    const x0 = Math.max(0, Math.min(length, load.offset))
    const y0 = getSurfaceY(x0, height, length)
    const maxAlongSlope = tx > 0 ? (length - x0) / tx : 0
    const alongSlope = Math.max(0, Math.min(load.length, maxAlongSlope))
    const x1 = x0 + tx * alongSlope
    const y1 = y0 + ty * alongSlope
    const blockDepth = Math.max(0.35, load.magnitude * 0.03 + height * 0.04)

    const p0w = { x: x0, y: y0 }
    const p1w = { x: x1, y: y1 }
    const p2w = { x: x1 + nx * blockDepth, y: y1 + ny * blockDepth }
    const p3w = { x: x0 + nx * blockDepth, y: y0 + ny * blockDepth }

    const p0 = toPixel(p0w)
    const p1 = toPixel(p1w)
    const p2 = toPixel(p2w)
    const p3 = toPixel(p3w)

    shapes.push(
      <Line
        key={`udl-${load.id}`}
        points={[p0.x, p0.y, p1.x, p1.y, p2.x, p2.y, p3.x, p3.y]}
        closed
        fill="rgba(248, 250, 252, 0.08)"
        stroke="#fde68a"
        strokeWidth={1}
      />,
    )
  })

  lineLoads.forEach((load) => {
    const x = Math.max(0, Math.min(length, load.offset))
    const y = getSurfaceY(x, height, length)
    const arrowLength = Math.max(0.5, load.magnitude * 0.04 + height * 0.06)

    const baseWorld = { x, y }
    const tipWorld = {
      x: x + nx * arrowLength,
      y: y + ny * arrowLength,
    }
    const base = toPixel(baseWorld)
    const tip = toPixel(tipWorld)

    shapes.push(
      <Arrow
        key={`ll-${load.id}`}
        points={[tip.x, tip.y, base.x, base.y]}
        stroke="#fb923c"
        fill="#fb923c"
        strokeWidth={2}
        pointerLength={6}
        pointerWidth={6}
      />,
    )
  })

  return <>{shapes}</>
}

