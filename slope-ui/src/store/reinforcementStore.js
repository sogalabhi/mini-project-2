import { create } from 'zustand'

export const useReinforcementStore = create((set) => ({
  enabled: true,
  targetFos: 1.5,
  steelYieldStrength: 415,
  soilGroutBondFriction: 100,

  setEnabled: (value) => set({ enabled: value }),
  setTargetFos: (value) => set({ targetFos: value }),
  setSteelYieldStrength: (value) => set({ steelYieldStrength: value }),
  setSoilGroutBondFriction: (value) => set({ soilGroutBondFriction: value }),
}))
