import { z } from 'zod'

const pointSchema = z.object({
  x: z.number().finite(),
  y: z.number().finite(),
  z: z.number().finite(),
})

const methodSchema = z.object({
  methodId: z.number().int().min(1).max(7),
  solver: z.object({
    maxIterations: z.number().int().positive(),
    tolFs: z.number().positive(),
    damping: z.number().positive().max(1),
  }),
  direction: z.object({
    spacingDeg: z.number().positive(),
    toleranceDeg: z.number().min(0),
    userDirectionDeg: z.number().min(0).max(360).nullable(),
  }),
})

const gridSchema = z
  .object({
    xMin: z.number(),
    xMax: z.number(),
    yMin: z.number(),
    yMax: z.number(),
    zMin: z.number(),
    zMax: z.number(),
    colXMax: z.number().int().positive().max(5000),
    colYMax: z.number().int().positive().max(5000),
  })
  .refine((v) => v.xMin < v.xMax, { path: ['xMax'], message: 'xMin must be < xMax' })
  .refine((v) => v.yMin < v.yMax, { path: ['yMax'], message: 'yMin must be < yMax' })
  .refine((v) => v.zMin < v.zMax, { path: ['zMax'], message: 'zMin must be < zMax' })

const topSurfaceSchema = z.object({
  label: z.string().min(1),
  path: z.string().min(1),
  interpolationMode: z.string().min(1),
  points: z.array(pointSchema).min(1),
})

const materialSchema = z.object({
  name: z.string().min(1),
  modelType: z.number().int().min(1).max(5),
  unitWeight: z.number().positive(),
  params: z.record(z.string(), z.number()),
})

const reinforcementSchema = z.object({
  enabled: z.boolean(),
  diameter: z.number().positive(),
  lengthEmbed: z.number().positive(),
  spacingX: z.number().positive(),
  spacingY: z.number().positive(),
  steelArea: z.number().positive(),
  yieldStrength: z.number().positive(),
  bondStrength: z.number().positive(),
  inclinationDeg: z.number().min(-90).max(90),
  includeVerticalComponent: z.boolean(),
})

export const form3dSchema = z.object({
  methodConfig: methodSchema,
  gridConfig: gridSchema,
  slipSurfaceConfig: z.object({
    mode: z.enum(['ellipsoid', 'user_defined']),
    ellipsoidCenter: z.array(z.number()).length(3),
    ellipsoidRadii: z.array(z.number()).length(3),
    userDefinedSurfacePath: z.string(),
    userDefinedInterpolation: z.string(),
  }),
  surfaces: z.object({
    topSurface: topSurfaceSchema,
  }),
  materials: z.array(materialSchema).min(1),
  hydro: z.object({ waterLevelZ: z.number().nullable() }),
  advanced: z.object({ includeAnalysisRows: z.boolean() }),
  reinforcement: reinforcementSchema,
})

function toPathString(pathParts) {
  return pathParts.join('.')
}

function tabForPath(path) {
  if (path.startsWith('methodConfig')) return 'method'
  if (path.startsWith('gridConfig')) return 'grid'
  if (path.startsWith('slipSurfaceConfig')) return 'slip'
  if (path.startsWith('surfaces')) return 'surfaces'
  if (path.startsWith('materials')) return 'materials'
  if (path.startsWith('hydro')) return 'hydro'
  return 'advanced'
}

export function validate3dForm(state) {
  const parsed = form3dSchema.safeParse(state)
  if (parsed.success) return { isValid: true, fieldErrors: {}, tabErrors: {} }

  const fieldErrors = {}
  const tabErrors = {}
  for (const issue of parsed.error.issues) {
    const path = toPathString(issue.path)
    fieldErrors[path] = issue.message
    tabErrors[tabForPath(path)] = true
  }
  return { isValid: false, fieldErrors, tabErrors }
}

function mapMaterialParams(material) {
  if (material.modelType === 1) return [material.params.phi ?? 30, material.params.cohesion ?? 5]
  if (material.modelType === 2)
    return [
      material.params.shearMax ?? 80,
      material.params.shearMin ?? 20,
      material.params.suTop ?? 40,
      material.params.diffSu ?? 10,
    ]
  if (material.modelType === 3)
    return [
      material.params.shearMax ?? 80,
      material.params.shearMin ?? 20,
      material.params.suTop ?? 40,
      material.params.diffSu ?? 10,
      material.params.datum ?? 0,
    ]
  if (material.modelType === 4)
    return [material.params.k ?? 1, material.params.exponent ?? 1.2, material.params.suTop ?? 40]
  return [material.params.suTop ?? 40]
}

export function build3dPayload(state) {
  const top = state.surfaces.topSurface
  return {
    method_config: {
      method_id: state.methodConfig.methodId,
      solver: {
        max_iterations: state.methodConfig.solver.maxIterations,
        tol_fs: state.methodConfig.solver.tolFs,
        damping: state.methodConfig.solver.damping,
      },
      direction: {
        spacing_deg: state.methodConfig.direction.spacingDeg,
        tolerance_deg: state.methodConfig.direction.toleranceDeg,
        user_direction_deg: state.methodConfig.direction.userDirectionDeg,
      },
      use_side_resistance: state.methodConfig.useSideResistance,
    },
    grid_config: {
      x_min: state.gridConfig.xMin,
      x_max: state.gridConfig.xMax,
      y_min: state.gridConfig.yMin,
      y_max: state.gridConfig.yMax,
      z_min: state.gridConfig.zMin,
      z_max: state.gridConfig.zMax,
      col_x_max: state.gridConfig.colXMax,
      col_y_max: state.gridConfig.colYMax,
    },
    slip_surface_config: {
      mode: state.slipSurfaceConfig.mode,
      ellipsoid_center: state.slipSurfaceConfig.ellipsoidCenter,
      ellipsoid_radii: state.slipSurfaceConfig.ellipsoidRadii,
      user_defined_surface_path: state.slipSurfaceConfig.userDefinedSurfacePath || null,
      user_defined_interpolation: state.slipSurfaceConfig.userDefinedInterpolation,
    },
    materials: Object.fromEntries(
      state.materials.map((m) => [
        m.key,
        {
          name: m.name,
          model_type: m.modelType,
          model_parameters: mapMaterialParams(m),
          unit_weight: m.unitWeight,
        },
      ]),
    ),
    top_surface: {
      label: top.label,
      path: top.path,
      interpolation_mode: top.interpolationMode,
      points: top.points,
    },
    user_slip_surface: null,
    surface_paths: null,
    surface_types: null,
    interpolation_modes: null,
    water_level_z: state.hydro.waterLevelZ,
    reinforcement: {
      enabled: state.reinforcement.enabled,
      diameter: state.reinforcement.diameter,
      length_embed: state.reinforcement.lengthEmbed,
      spacing_x: state.reinforcement.spacingX,
      spacing_y: state.reinforcement.spacingY,
      steel_area: state.reinforcement.steelArea,
      yield_strength: state.reinforcement.yieldStrength,
      bond_strength: state.reinforcement.bondStrength,
      inclination_deg: state.reinforcement.inclinationDeg,
      include_vertical_component: state.reinforcement.includeVerticalComponent,
    },
    debug: {
      include_analysis_rows: state.advanced.includeAnalysisRows,
    },
  }
}

