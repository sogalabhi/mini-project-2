import { create } from 'zustand'

const initialState = {
  height: 10,
  angle: 30,
  length: null,
}

export const useGeometryStore = create((set) => ({
  ...initialState,
  setHeight: (value) =>
    set((state) => ({
      ...state,
      height: value,
      length:
        state.length == null
          ? null
          : Number(
              (value / Math.tan(((state.angle || 30) * Math.PI) / 180)).toFixed(
                2,
              ),
            ),
    })),
  setAngle: (value) =>
    set((state) => ({
      ...state,
      angle: value,
      length:
        state.length == null
          ? null
          : Number(
              ((state.height || 10) / Math.tan((value * Math.PI) / 180)).toFixed(
                2,
              ),
            ),
    })),
  setLength: (value) =>
    set((state) => ({
      ...state,
      length: value,
    })),
  setGeometry: (height, length) =>
    set((state) => ({
      ...state,
      height: Number(height.toFixed(2)),
      length: Number(length.toFixed(2)),
      angle:
        length > 0
          ? Number((Math.atan(height / length) * (180 / Math.PI)).toFixed(2))
          : state.angle,
    })),
  resetGeometry: () => set(() => ({ ...initialState })),
}))

