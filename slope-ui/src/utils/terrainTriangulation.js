function asKey(x, y) {
  return `${x}::${y}`
}

export function triangulateStructuredGrid(points) {
  if (!Array.isArray(points) || points.length < 3) {
    return { vertices: [], indices: [], warnings: ['insufficient_points'] }
  }
  const xVals = [...new Set(points.map((p) => Number(p.x)))].sort((a, b) => a - b)
  const yVals = [...new Set(points.map((p) => Number(p.y)))].sort((a, b) => a - b)
  if (xVals.length < 2 || yVals.length < 2) {
    return { vertices: [], indices: [], warnings: ['not_grid_like'] }
  }

  const pointMap = new Map()
  points.forEach((p) => pointMap.set(asKey(Number(p.x), Number(p.y)), Number(p.z)))

  const vertices = []
  const gridIndex = new Map()
  for (const x of xVals) {
    for (const y of yVals) {
      const z = pointMap.get(asKey(x, y))
      if (z == null) continue
      const idx = vertices.length / 3
      vertices.push(x, y, z)
      gridIndex.set(asKey(x, y), idx)
    }
  }

  const indices = []
  for (let ix = 0; ix < xVals.length - 1; ix += 1) {
    for (let iy = 0; iy < yVals.length - 1; iy += 1) {
      const k00 = gridIndex.get(asKey(xVals[ix], yVals[iy]))
      const k10 = gridIndex.get(asKey(xVals[ix + 1], yVals[iy]))
      const k11 = gridIndex.get(asKey(xVals[ix + 1], yVals[iy + 1]))
      const k01 = gridIndex.get(asKey(xVals[ix], yVals[iy + 1]))
      if ([k00, k10, k11, k01].some((v) => v == null)) continue
      indices.push(k00, k10, k11, k00, k11, k01)
    }
  }
  return { vertices, indices, warnings: [] }
}

