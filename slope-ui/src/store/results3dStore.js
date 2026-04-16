import { create } from 'zustand'

export const useResults3dStore = create((set) => ({
  latestSingle: null,
  latestMulti: null,
  lastPayload: null,
  compareSnapshot: null,
  loading: false,
  error: null,
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  setSingleResult: (latestSingle) => set({ latestSingle, compareSnapshot: null, error: null }),
  setMultiResult: (latestMulti) => set({ latestMulti, error: null }),
  setLastPayload: (lastPayload) => set({ lastPayload }),
  setCompareSnapshot: (compareSnapshot) => set({ compareSnapshot }),
  clear: () =>
    set({ latestSingle: null, latestMulti: null, lastPayload: null, compareSnapshot: null, error: null }),
}))

