import { create } from 'zustand'

export const useUi3dStore = create((set) => ({
  activeInputTab: 'method',
  activeOutputTab: 'summary',
  selectedColumnId: null,
  featureFlags: {
    terrainMeshEnabled: true,
    userSlipMeshEnabled: true,
    columnLinesEnabled: true,
    columnPrismsEnabled: true,
    morphologyEnabled: true,
    fsHeatmapEnabled: true,
  },
  setActiveInputTab: (activeInputTab) => set({ activeInputTab }),
  setActiveOutputTab: (activeOutputTab) => set({ activeOutputTab }),
  setSelectedColumnId: (selectedColumnId) => set({ selectedColumnId }),
  setFeatureFlags: (patch) => set((state) => ({ featureFlags: { ...state.featureFlags, ...patch } })),
}))

