import { create } from 'zustand'
import { v4 as uuid } from 'uuid'

const PALETTE = ['#c8a96e', '#a0785a', '#7a9e7e', '#5b7fa6', '#8c6b4a']

export const useMaterialsStore = create((set, get) => ({
  layers: [
    {
      id: uuid(),
      name: 'Topsoil',
      unitWeight: 18,
      frictionAngle: 30,
      cohesion: 10,
      depthToBottom: 5,
      color: PALETTE[0],
    },
  ],

  addLayer: () => {
    const { layers } = get()
    const color = PALETTE[layers.length % PALETTE.length]
    const newLayer = {
      id: uuid(),
      name: `Layer ${layers.length + 1}`,
      unitWeight: 18,
      frictionAngle: 30,
      cohesion: 10,
      depthToBottom: (layers[layers.length - 1]?.depthToBottom || 5) + 5,
      color,
    }
    set({ layers: [...layers, newLayer] })
  },

  updateLayer: (id, patch) =>
    set((state) => ({
      layers: state.layers.map((layer) =>
        layer.id === id ? { ...layer, ...patch } : layer,
      ),
    })),

  removeLayer: (id) =>
    set((state) => ({
      layers: state.layers.filter((layer) => layer.id !== id),
    })),
}))

