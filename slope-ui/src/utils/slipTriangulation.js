function centroid(points) {
  if (!points.length) return { x: 0, y: 0, z: 0 }
  const sum = points.reduce((acc, p) => ({ x: acc.x + p.x, y: acc.y + p.y, z: acc.z + p.z }), {
    x: 0,
    y: 0,
    z: 0,
  })
  return { x: sum.x / points.length, y: sum.y / points.length, z: sum.z / points.length }
}

export function triangulateUserSlip(points) {
  if (!Array.isArray(points) || points.length < 3) {
    return { vertices: [], indices: [], quality: 'failed', warnings: ['insufficient_points'] }
  }
  const c = centroid(points)
  const ordered = [...points].sort(
    (a, b) => Math.atan2(a.y - c.y, a.x - c.x) - Math.atan2(b.y - c.y, b.x - c.x),
  )
  const vertices = ordered.flatMap((p) => [Number(p.x), Number(p.y), Number(p.z)])
  const indices = []
  for (let i = 1; i < ordered.length - 1; i += 1) {
    indices.push(0, i, i + 1)
  }
  return {
    vertices,
    indices,
    quality: indices.length > 0 ? 'ok' : 'degraded',
    warnings: indices.length > 0 ? [] : ['degenerate_surface'],
  }
}

