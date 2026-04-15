import { useMutation } from '@tanstack/react-query'
import { analyzeSlope, buildAnalysisPayload } from '../api/slopeApi.js'
import { useGeometryStore } from '../store/geometryStore.js'
import { useMaterialsStore } from '../store/materialsStore.js'
import { useLoadsStore } from '../store/loadsStore.js'
import { useWaterStore } from '../store/waterStore.js'
import { useSettingsStore } from '../store/settingsStore.js'
import { useReinforcementStore } from '../store/reinforcementStore.js'
import { useResultsStore } from '../store/resultsStore.js'

function getPayloadFromStores() {
  return buildAnalysisPayload({
    geometry: useGeometryStore.getState(),
    layers: useMaterialsStore.getState().layers,
    udls: useLoadsStore.getState().udls,
    lineLoads: useLoadsStore.getState().lineLoads,
    water: useWaterStore.getState(),
    settings: useSettingsStore.getState(),
    reinforcement: useReinforcementStore.getState(),
  })
}

export function useAnalysis() {
  const setLatest = useResultsStore((s) => s.setLatest)

  return useMutation({
    mutationFn: async () => {
      const payload = getPayloadFromStores()
      return analyzeSlope(payload)
    },
    onSuccess: (data) => {
      setLatest(data)
    },
  })
}

