import { create } from 'zustand'

export const useResults3dStore = create((set) => ({
  latestSingle: null,
  latestMulti: null,
  lastPayload: null,
  loading: false,
  error: null,
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  setSingleResult: (latestSingle) => set({ latestSingle, error: null }),
  setMultiResult: (latestMulti) => set({ latestMulti, error: null }),
  setLastPayload: (lastPayload) => set({ lastPayload }),
  clear: () => set({ latestSingle: null, latestMulti: null, lastPayload: null, error: null }),
}))

