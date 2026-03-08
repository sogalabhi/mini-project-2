import { Text } from 'react-konva'

export default function DimensionLabels({ coords, height, angle, length }) {
  const { toPixel } = coords

  const origin = toPixel({ x: 0, y: 0 })
  const crest = toPixel({ x: length, y: height })

  const label = `H = ${height.toFixed(1)} m   L = ${length.toFixed(
    1,
  )} m   θ = ${angle.toFixed(1)}°`

  return (
    <Text
      x={origin.x}
      y={crest.y - 24}
      text={label}
      fontSize={12}
      fill="#9ca3af"
    />
  )
}

