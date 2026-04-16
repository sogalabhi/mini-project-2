import { create } from 'zustand'

export const useUi3dStore = create((set) => ({
  activeInputTab: 'method',
  activeOutputTab: 'summary',
  selectedColumnId: null,
  setActiveInputTab: (activeInputTab) => set({ activeInputTab }),
  setActiveOutputTab: (activeOutputTab) => set({ activeOutputTab }),
  setSelectedColumnId: (selectedColumnId) => set({ selectedColumnId }),
}))

