export function useCanvasCoords(width, height, worldHeight, worldLength) {
  const padding = 40
  const worldW = worldLength || 20
  const worldH = worldHeight || 10

  const scaleX = (width - padding * 2) / worldW
  const scaleY = (height - padding * 2) / worldH
  const scale = Math.min(scaleX, scaleY)

  function toPixel({ x, y }) {
    return {
      x: padding + x * scale,
      y: height - padding - y * scale,
    }
  }

  function toWorld({ x, y }) {
    return {
      x: (x - padding) / scale,
      y: (height - padding - y) / scale,
    }
  }

  return { toPixel, toWorld, worldW, worldH, scale }
}

