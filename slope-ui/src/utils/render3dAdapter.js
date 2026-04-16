const MAX_PREVIEW_POINTS = 1200

function toNumber(value, fallback = 0) {
  const n = Number(value)
  return Number.isFinite(n) ? n : fallback
}

export function decimatePoints(points, limit = MAX_PREVIEW_POINTS) {
  if (!Array.isArray(points) || points.length <= limit) return points || []
  const step = Math.ceil(points.length / limit)
  const reduced = []
  for (let i = 0; i < points.length; i += step) reduced.push(points[i])
  return reduced
}

export function buildRender3dModel({ payload, fallbackFormState, result }) {
  const topPayload = payload?.top_surface
  const topFallback = fallbackFormState?.surfaces?.topSurface
  const rawTopPoints = topPayload?.points || topFallback?.points || []
  const rawPoints = rawTopPoints.map((p) => ({
    x: toNumber(p.x),
    y: toNumber(p.y),
    z: toNumber(p.z),
  }))

  const gridPayload = payload?.grid_config
  const gridFallback = fallbackFormState?.gridConfig
  const grid = gridPayload || gridFallback || {}
  const slipPayload = payload?.slip_surface_config
  const slipFallback = fallbackFormState?.slipSurfaceConfig
  const slip = slipPayload || slipFallback || {}

  return {
    topSurfacePoints: decimatePoints(rawPoints),
    gridBounds: {
      xMin: toNumber(grid.xMin ?? grid.x_min),
      xMax: toNumber(grid.xMax ?? grid.x_max, 1),
      yMin: toNumber(grid.yMin ?? grid.y_min),
      yMax: toNumber(grid.yMax ?? grid.y_max, 1),
      zMin: toNumber(grid.zMin ?? grid.z_min),
      zMax: toNumber(grid.zMax ?? grid.z_max, 1),
    },
    slipSurface: {
      mode: slip.mode || 'ellipsoid',
      center: (slip.ellipsoidCenter || slip.ellipsoid_center || [0, 0, 0]).map((v) => toNumber(v)),
      radii: (slip.ellipsoidRadii || slip.ellipsoid_radii || [1, 1, 1]).map((v) => Math.max(0.01, toNumber(v, 1))),
      userDefinedMeta: {
        path: slip.userDefinedSurfacePath || slip.user_defined_surface_path || '',
        interpolation: slip.userDefinedInterpolation || slip.user_defined_interpolation || 'a1',
      },
    },
    analysisMeta: {
      methodId: result?.method_id ?? null,
      fsMin: result?.fs_min ?? null,
      converged: result?.converged ?? null,
    },
  }
}

