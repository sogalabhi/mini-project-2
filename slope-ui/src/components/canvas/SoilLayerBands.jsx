import React from 'react'
import { Rect, Text } from 'react-konva'

export default function SoilLayerBands({ coords, layers, height }) {
  const { worldW, toPixel } = coords

  if (!layers || layers.length === 0) return null

  return (
    <>
      {layers.map((layer, index) => {
        const topDepth = index === 0 ? 0 : layers[index - 1].depthToBottom || 0
        const bottomDepth = layer.depthToBottom || height
        const visibleTop = Math.min(topDepth, height)
        const visibleBottom = Math.min(bottomDepth, height)

        const top = toPixel({ x: 0, y: height - visibleTop })
        const bottom = toPixel({ x: worldW, y: height - visibleBottom })

        const rectHeight = bottom.y - top.y

        return (
          <React.Fragment key={layer.id}>
            <Rect
              x={top.x}
              y={top.y}
              width={bottom.x - top.x}
              height={rectHeight}
              fill={layer.color}
              opacity={0.18}
            />
            <Text
              x={top.x + 8}
              y={top.y + 4}
              text={layer.name}
              fontSize={11}
              fill="#cbd5f5"
            />
          </React.Fragment>
        )
      })}
    </>
  )
}

