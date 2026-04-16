import test from 'node:test'
import assert from 'node:assert/strict'
import { buildRender3dModel, decimatePoints } from './render3dAdapter.js'

test('decimatePoints reduces large arrays to limit', () => {
  const points = Array.from({ length: 5000 }, (_, i) => ({ x: i, y: i, z: i }))
  const out = decimatePoints(points, 1000)
  assert.ok(out.length <= 1000)
  assert.ok(out.length > 0)
})

test('buildRender3dModel maps payload snake_case and result meta', () => {
  const model = buildRender3dModel({
    payload: {
      top_surface: { points: [{ x: 0, y: 0, z: 1 }] },
      grid_config: { x_min: 0, x_max: 2, y_min: 0, y_max: 2, z_min: 0, z_max: 3 },
      slip_surface_config: { mode: 'ellipsoid', ellipsoid_center: [1, 1, 1], ellipsoid_radii: [2, 2, 2] },
    },
    fallbackFormState: null,
    result: { method_id: 1, fs_min: 1.2, converged: true },
  })
  assert.equal(model.topSurfacePoints.length, 1)
  assert.equal(model.gridBounds.xMax, 2)
  assert.equal(model.analysisMeta.converged, true)
})

