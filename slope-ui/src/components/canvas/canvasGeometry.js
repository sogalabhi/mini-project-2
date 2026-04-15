export function getSurfaceY(x, height, length) {
  if (length <= 0) return 0
  const xc = Math.max(0, Math.min(length, x))
  return (height / length) * xc
}

export function getSlopePolygonWorld(height, length) {
  return [
    { x: 0, y: 0 },
    { x: length, y: height },
    { x: length, y: 0 },
  ]
}

export function worldPointsToKonva(points, toPixel) {
  return points.flatMap((point) => {
    const pixel = toPixel(point)
    return [pixel.x, pixel.y]
  })
}
