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

  const renderData = result?.render_data ?? {}
  const topSurfacePoints = decimatePoints(
    (renderData.top_surface_points || rawPoints).map((p) => ({
      x: toNumber(p.x),
      y: toNumber(p.y),
      z: toNumber(p.z),
    })),
  )
  const columns = (renderData.columns || []).map((c) => ({
    columnId: toNumber(c.column_id),
    xCenter: toNumber(c.x_center),
    yCenter: toNumber(c.y_center),
    zTop: toNumber(c.z_top),
    zBase: toNumber(c.z_base),
    thickness: toNumber(c.thickness),
    isActive: Boolean(c.is_active ?? true),
  }))
  const fsField = renderData.fs_field || {}
  const warnings = []
  if (slip.mode === 'user_defined' && !(payload?.user_slip_surface?.points || []).length) {
    warnings.push('User-defined slip surface has no points; slip mesh fallback may apply.')
  }
  if (!fsField || fsField.min == null || fsField.max == null) {
    warnings.push('Per-column FS field unavailable; heatmap overlay disabled.')
  }

  return {
    topSurfacePoints,
    terrainMesh: {
      points: topSurfacePoints,
    },
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
      userDefinedPoints: (
        payload?.user_slip_surface?.points ||
        fallbackFormState?.userSlipSurface?.points ||
        []
      ).map((p) => ({ x: toNumber(p.x), y: toNumber(p.y), z: toNumber(p.z) })),
      userDefinedMeta: {
        path: slip.userDefinedSurfacePath || slip.user_defined_surface_path || '',
        interpolation: slip.userDefinedInterpolation || slip.user_defined_interpolation || 'a1',
      },
    },
    columnGeometry: {
      columns,
      centers: columns.map((c) => ({ x: c.xCenter, y: c.yCenter, z: (c.zTop + c.zBase) / 2, columnId: c.columnId })),
      lines: columns.map((c) => ({ x: c.xCenter, y: c.yCenter, zTop: c.zTop, zBase: c.zBase, columnId: c.columnId })),
    },
    fsField: {
      scalarByColumnId: fsField.scalar_by_column_id || {},
      min: toNumber(fsField.min, NaN),
      max: toNumber(fsField.max, NaN),
      units: fsField.units || 'proxy',
      mappingMode: fsField.mapping_mode || 'none',
    },
    morphology: renderData.morphology || null,
    renderDiagnostics: {
      warnings,
      activeColumns: columns.length,
      topPointCount: topSurfacePoints.length,
    },
    analysisMeta: {
      methodId: result?.method_id ?? null,
      fsMin: result?.fs_min ?? null,
      converged: result?.converged ?? null,
    },
  }
}

