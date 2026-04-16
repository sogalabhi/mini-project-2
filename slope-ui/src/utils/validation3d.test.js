import test from 'node:test'
import assert from 'node:assert/strict'
import { build3dPayload, validate3dForm } from './validation3d.js'

const validState = {
  methodConfig: {
    methodId: 1,
    useSideResistance: true,
    solver: { maxIterations: 200, tolFs: 0.001, damping: 1.0 },
    direction: { spacingDeg: 0.5, toleranceDeg: 10, userDirectionDeg: null },
    comparisonMode: false,
    comparisonMethodIds: [1, 2],
  },
  gridConfig: { xMin: 0, xMax: 2, yMin: 0, yMax: 2, zMin: 0, zMax: 20, colXMax: 8, colYMax: 8 },
  slipSurfaceConfig: {
    mode: 'ellipsoid',
    ellipsoidCenter: [1, 1, 9],
    ellipsoidRadii: [2, 2, 3],
    userDefinedSurfacePath: '',
    userDefinedInterpolation: 'a1',
  },
  surfaces: {
    topSurface: {
      label: 'tt',
      path: 'synthetic_top.csv',
      interpolationMode: 'a1',
      points: [
        { x: 0, y: 0, z: 10 },
        { x: 2, y: 0, z: 10 },
      ],
    },
  },
  materials: [{ key: 'default', name: 'default', modelType: 1, unitWeight: 18, params: { phi: 30, cohesion: 5 } }],
  hydro: { waterLevelZ: null },
  advanced: { includeAnalysisRows: false },
}

test('validate3dForm succeeds for valid state', () => {
  const out = validate3dForm(validState)
  assert.equal(out.isValid, true)
})

test('validate3dForm catches bad grid bounds', () => {
  const out = validate3dForm({
    ...validState,
    gridConfig: { ...validState.gridConfig, xMin: 3, xMax: 2 },
  })
  assert.equal(out.isValid, false)
  assert.ok(out.fieldErrors['gridConfig.xMax'])
})

test('build3dPayload maps keys correctly', () => {
  const payload = build3dPayload(validState)
  assert.equal(payload.method_config.method_id, 1)
  assert.equal(payload.grid_config.col_x_max, 8)
  assert.equal(payload.top_surface.interpolation_mode, 'a1')
  assert.deepEqual(payload.materials.default.model_parameters, [30, 5])
})

