import { create } from 'zustand'

export const useWaterStore = create((set) => ({
  enabled: false,
  depth: 5,
  unitWeight: 9.81,

  setEnabled: (value) => set({ enabled: value }),
  setDepth: (value) => set({ depth: value }),
  setUnitWeight: (value) => set({ unitWeight: value }),
}))

