import { Line } from 'react-konva'

export default function GridBackground({ coords }) {
  const { worldW, worldH, toPixel } = coords

  const lines = []
  const step = 2

  for (let x = 0; x <= worldW; x += step) {
    const p1 = toPixel({ x, y: 0 })
    const p2 = toPixel({ x, y: worldH })
    lines.push(
      <Line
        key={`vx-${x}`}
        points={[p1.x, p1.y, p2.x, p2.y]}
        stroke="#020617"
        strokeWidth={1}
      />,
    )
  }

  for (let y = 0; y <= worldH; y += step) {
    const p1 = toPixel({ x: 0, y })
    const p2 = toPixel({ x: worldW, y })
    lines.push(
      <Line
        key={`hz-${y}`}
        points={[p1.x, p1.y, p2.x, p2.y]}
        stroke="#020617"
        strokeWidth={1}
      />,
    )
  }

  return <>{lines}</>
}

