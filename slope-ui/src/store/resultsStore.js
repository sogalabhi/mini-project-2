import { create } from 'zustand'

export const useResultsStore = create((set) => ({
  latest: null,
  history: [],

  setLatest: (result) =>
    set((state) => ({
      latest: result,
      history: [{ id: Date.now(), ...result }, ...state.history].slice(0, 10),
    })),
}))

