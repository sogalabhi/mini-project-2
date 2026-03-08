import { create } from 'zustand'
import { v4 as uuid } from 'uuid'

export const useLoadsStore = create((set) => ({
  udls: [],
  lineLoads: [],

  addUdl: () =>
    set((state) => ({
      udls: [
        ...state.udls,
        {
          id: uuid(),
          magnitude: 10,
          offset: 1,
          length: 3,
        },
      ],
    })),

  updateUdl: (id, patch) =>
    set((state) => ({
      udls: state.udls.map((l) => (l.id === id ? { ...l, ...patch } : l)),
    })),

  removeUdl: (id) =>
    set((state) => ({
      udls: state.udls.filter((l) => l.id !== id),
    })),

  addLineLoad: () =>
    set((state) => ({
      lineLoads: [
        ...state.lineLoads,
        {
          id: uuid(),
          magnitude: 20,
          offset: 2,
        },
      ],
    })),

  updateLineLoad: (id, patch) =>
    set((state) => ({
      lineLoads: state.lineLoads.map((l) =>
        l.id === id ? { ...l, ...patch } : l,
      ),
    })),

  removeLineLoad: (id) =>
    set((state) => ({
      lineLoads: state.lineLoads.filter((l) => l.id !== id),
    })),
}))

