import React from 'react'
import { Group, Rect, Text } from 'react-konva'
import {
  getSlopePolygonWorld,
  worldPointsToKonva,
} from './canvasGeometry.js'

export default function SoilLayerBands({ coords, layers, height, length }) {
  const { worldW, toPixel } = coords

  if (!layers || layers.length === 0) return null

  const clipPoints = worldPointsToKonva(
    getSlopePolygonWorld(height, length),
    toPixel,
  )

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
    </Group>
  )
}

