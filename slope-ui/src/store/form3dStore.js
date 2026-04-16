import { create } from 'zustand'

const defaultTopSurfacePoints = [
  { x: 0, y: 0, z: 10 },
  { x: 2, y: 0, z: 10 },
  { x: 0, y: 2, z: 9.5 },
  { x: 2, y: 2, z: 9.5 },
]

const defaultMaterial = {
  key: 'default',
  name: 'default',
  modelType: 1,
  unitWeight: 18,
  params: {
    phi: 30,
    cohesion: 5,
    shearMax: 80,
    shearMin: 20,
    suTop: 40,
    diffSu: 10,
    datum: 0,
    exponent: 1.2,
    k: 1.0,
  },
}

export const useForm3dStore = create((set) => ({
  methodConfig: {
    methodId: 1,
    useSideResistance: true,
    solver: { maxIterations: 200, tolFs: 0.001, damping: 1.0 },
    direction: { spacingDeg: 0.5, toleranceDeg: 10.0, userDirectionDeg: null },
    comparisonMode: false,
    comparisonMethodIds: [1, 2, 3],
  },
  gridConfig: {
    xMin: 0,
    xMax: 2,
    yMin: 0,
    yMax: 2,
    zMin: 0,
    zMax: 20,
    colXMax: 8,
    colYMax: 8,
  },
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
      points: defaultTopSurfacePoints,
    },
  },
  materials: [defaultMaterial],
  hydro: { waterLevelZ: null },
  advanced: { includeAnalysisRows: false },
  reinforcement: {
    enabled: false,
    diameter: 0.1,
    lengthEmbed: 6,
    spacingX: 1.5,
    spacingY: 1.5,
    steelArea: 0.0005,
    yieldStrength: 500,
    bondStrength: 120,
    inclinationDeg: 10,
    includeVerticalComponent: false,
  },

  setMethodConfig: (patch) =>
    set((state) => ({ methodConfig: { ...state.methodConfig, ...patch } })),
  setMethodSolver: (patch) =>
    set((state) => ({
      methodConfig: { ...state.methodConfig, solver: { ...state.methodConfig.solver, ...patch } },
    })),
  setMethodDirection: (patch) =>
    set((state) => ({
      methodConfig: {
        ...state.methodConfig,
        direction: { ...state.methodConfig.direction, ...patch },
      },
    })),
  setGridConfig: (patch) => set((state) => ({ gridConfig: { ...state.gridConfig, ...patch } })),
  setSlipSurfaceConfig: (patch) =>
    set((state) => ({ slipSurfaceConfig: { ...state.slipSurfaceConfig, ...patch } })),
  setHydro: (patch) => set((state) => ({ hydro: { ...state.hydro, ...patch } })),
  setAdvanced: (patch) => set((state) => ({ advanced: { ...state.advanced, ...patch } })),
  setReinforcement: (patch) =>
    set((state) => ({ reinforcement: { ...state.reinforcement, ...patch } })),
  setTopSurfaceMeta: (patch) =>
    set((state) => ({ surfaces: { topSurface: { ...state.surfaces.topSurface, ...patch } } })),
  addTopSurfacePoint: () =>
    set((state) => ({
      surfaces: {
        topSurface: {
          ...state.surfaces.topSurface,
          points: [...state.surfaces.topSurface.points, { x: 0, y: 0, z: 0 }],
        },
      },
    })),
  updateTopSurfacePoint: (index, patch) =>
    set((state) => {
      const points = [...state.surfaces.topSurface.points]
      points[index] = { ...points[index], ...patch }
      return { surfaces: { topSurface: { ...state.surfaces.topSurface, points } } }
    }),
  removeTopSurfacePoint: (index) =>
    set((state) => ({
      surfaces: {
        topSurface: {
          ...state.surfaces.topSurface,
          points: state.surfaces.topSurface.points.filter((_, i) => i !== index),
        },
      },
    })),
  useDemoSurface: () =>
    set((state) => ({
      surfaces: { topSurface: { ...state.surfaces.topSurface, points: defaultTopSurfacePoints } },
    })),

  addMaterial: () =>
    set((state) => ({
      materials: [
        ...state.materials,
        {
          ...defaultMaterial,
          key: `material_${Date.now()}`,
          name: `material_${state.materials.length + 1}`,
        },
      ],
    })),
  updateMaterial: (key, patch) =>
    set((state) => ({
      materials: state.materials.map((m) => (m.key === key ? { ...m, ...patch } : m)),
    })),
  updateMaterialParams: (key, patch) =>
    set((state) => ({
      materials: state.materials.map((m) =>
        m.key === key ? { ...m, params: { ...m.params, ...patch } } : m,
      ),
    })),
  removeMaterial: (key) =>
    set((state) => ({ materials: state.materials.filter((m) => m.key !== key) })),
}))

