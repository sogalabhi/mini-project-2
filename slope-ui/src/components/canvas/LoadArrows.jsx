import { Line, Rect } from 'react-konva'

export default function LoadArrows({ coords, udls, lineLoads, height }) {
  const { toPixel } = coords

  const shapes = []

  udls.forEach((load) => {
    const yWorld = height
    const start = toPixel({ x: load.offset, y: yWorld })
    const end = toPixel({ x: load.offset + load.length, y: yWorld })

    const blockHeight = 20 + load.magnitude * 0.5

    shapes.push(
      <Rect
        key={`udl-${load.id}`}
        x={start.x}
        y={start.y - blockHeight}
        width={end.x - start.x}
        height={blockHeight}
        fill="rgba(248, 250, 252, 0.08)"
        stroke="#fde68a"
        strokeWidth={1}
      />,
    )
  })

  lineLoads.forEach((load) => {
    const yWorld = height
    const base = toPixel({ x: load.offset, y: yWorld })
    const top = { x: base.x, y: base.y - (25 + load.magnitude * 0.5) }

    shapes.push(
      <Line
        key={`ll-${load.id}`}
        points={[top.x, top.y, base.x, base.y]}
        stroke="#fb923c"
        strokeWidth={2}
        pointerLength={6}
        pointerWidth={6}
      />,
    )
  })

  return <>{shapes}</>
}

