import { create } from 'zustand'

export const useSettingsStore = create((set) => ({
  numSlices: 50,
  numIterations: 2000,
  tolerance: 0.001,

  setNumSlices: (value) => set({ numSlices: value }),
  setNumIterations: (value) => set({ numIterations: value }),
  setTolerance: (value) => set({ tolerance: value }),
}))

