import { create } from 'zustand'

export const useValidation3dStore = create((set) => ({
  fieldErrors: {},
  tabErrors: {},
  validating: false,
  serverErrors: [],
  setValidationState: ({ fieldErrors = {}, tabErrors = {}, serverErrors = [] }) =>
    set({ fieldErrors, tabErrors, serverErrors }),
  setValidating: (validating) => set({ validating }),
  clearValidation: () => set({ fieldErrors: {}, tabErrors: {}, serverErrors: [] }),
}))

