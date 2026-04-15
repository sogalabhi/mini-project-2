import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || ''

const client = axios.create({
  baseURL: API_BASE,
})

export function buildAnalysisPayload({
  geometry,
  layers,
  udls,
  lineLoads,
  water,
  settings,
}) {
  return {
    geometry: {
      height: geometry.height,
      angle: geometry.angle,
      length: geometry.length,
    },
    layers: layers.map((layer) => ({
      name: layer.name,
      unit_weight: layer.unitWeight,
      friction_angle: layer.frictionAngle,
      cohesion: layer.cohesion,
      depth_to_bottom: layer.depthToBottom,
    })),
    udls: udls.map((load) => ({
      magnitude: load.magnitude,
      offset: load.offset,
      length: load.length,
    })),
    line_loads: lineLoads.map((load) => ({
      magnitude: load.magnitude,
      offset: load.offset,
    })),
    water_table_depth: water.enabled ? water.depth : null,
    water_unit_weight: water.unitWeight,
    settings: {
      num_slices: settings.numSlices,
      num_iterations: settings.numIterations,
      tolerance: settings.tolerance,
    },
  }
}

export async function analyzeSlope(payload) {
  const [resultsSettled, imageSettled] = await Promise.allSettled([
    client.post('/analyze', payload),
    client.post('/analyze-image', payload, { responseType: 'blob' }),
  ])

  if (resultsSettled.status === 'rejected') {
    throw resultsSettled.reason
  }

  const resultsRes = resultsSettled.value
  let imageUrl = null

  if (imageSettled.status === 'fulfilled') {
    const imageBlob = imageSettled.value.data
    imageUrl = URL.createObjectURL(imageBlob)
  }

  return {
    factorOfSafety: resultsRes.data.factor_of_safety,
    status: resultsRes.data.stability_status || resultsRes.data.status,
    method: resultsRes.data.method,
    warnings: resultsRes.data.warnings || [],
    comparison: resultsRes.data.comparison || null,
    imageUrl,
  }
}

