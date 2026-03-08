# Slope Stability Analyzer — React (JavaScript) Architecture

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                   React Frontend                     │
│  Vite + React 18 + Zustand + Konva.js + TanStack    │
└──────────────────────┬──────────────────────────────┘
                       │ REST (axios)
┌──────────────────────▼──────────────────────────────┐
│               FastAPI Backend (existing)             │
│   POST /analyze  ·  POST /analyze-image              │
└─────────────────────────────────────────────────────┘
```

---

## Tech Stack Choices

| Layer | Library | Why |
|-------|---------|-----|
| Build | **Vite** | Fast HMR, zero config |
| UI framework | **React 18** | Component model fits multi-panel layout |
| Canvas | **Konva.js + react-konva** | 2D canvas with drag handles, layers, hit detection |
| State | **Zustand** | Flat, simple slices; no Redux boilerplate |
| Server state | **TanStack Query** | Handles loading/error/caching for `/analyze` calls |
| Forms | **React Hook Form** | For the tabbed detail panels |
| Styling | **Tailwind CSS** | Utility-first, fast iteration |

---

## Folder Structure

```
frontend/
├── src/
│   ├── store/                    # Zustand state slices
│   │   ├── geometryStore.js      # height, angle, length + derived
│   │   ├── materialsStore.js     # layers[]
│   │   ├── loadsStore.js         # udls[], lineLoads[]
│   │   ├── waterStore.js         # depth, enabled
│   │   └── settingsStore.js      # slices, iterations, tolerance
│   │
│   ├── components/
│   │   ├── canvas/
│   │   │   ├── SlopeCanvas.jsx       # Main Konva stage
│   │   │   ├── SlopeShape.jsx        # Draggable slope polygon
│   │   │   ├── SoilLayerBands.jsx     # Colored horizontal bands
│   │   │   ├── LoadArrows.jsx        # UDL blocks + line load arrows
│   │   │   ├── WaterTableLine.jsx    # Draggable blue line
│   │   │   ├── DimensionLabels.jsx   # Live "H=10m, θ=30°" labels
│   │   │   └── GridBackground.jsx   # Meter grid
│   │   │
│   │   ├── panels/
│   │   │   ├── GeometryPanel.jsx     # Height/Angle/Length fields
│   │   │   ├── MaterialsPanel.jsx    # Layer table + add/remove
│   │   │   ├── LoadsPanel.jsx        # UDL + line load table
│   │   │   ├── WaterPanel.jsx        # Depth slider + toggle
│   │   │   └── SettingsPanel.jsx     # Slices, iterations, tolerance
│   │   │
│   │   ├── results/
│   │   │   ├── ResultsPanel.jsx      # FOS badge + status
│   │   │   ├── DiagramViewer.jsx     # Shows backend PNG
│   │   │   └── AnalysisHistory.jsx   # Last N runs dropdown
│   │   │
│   │   └── layout/
│   │       ├── AppShell.jsx          # 3-panel grid layout
│   │       ├── TabPanel.jsx           # Right panel tab switcher
│   │       └── RunButton.jsx          # Sticky "Run Analysis" CTA
│   │
│   ├── hooks/
│   │   ├── useGeometryDrag.js    # Konva drag → store sync
│   │   ├── useAnalysis.js        # TanStack Query wrapper for /analyze
│   │   └── useCanvasSync.js      # Store changes → canvas re-render
│   │
│   ├── api/
│   │   └── slopeApi.js           # axios calls to FastAPI
│   │
│   ├── utils/
│   │   ├── geometry.js          # deriveGeometry, validation
│   │   └── constants.js         # GEO_PALETTE, fosColor, etc.
│   │
│   ├── App.jsx
│   └── main.jsx
│
├── index.html
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
└── package.json
```

---

## Data Shapes (JSDoc for IDE hints)

```javascript
/**
 * @typedef {Object} SlopeGeometry
 * @property {number|null} height - m
 * @property {number|null} angle - degrees
 * @property {number|null} length - m
 * @property {'height'|'angle'|'length'|null} derived - which field is computed
 */

/**
 * @typedef {Object} SoilLayer
 * @property {string} id
 * @property {string} name
 * @property {number} unitWeight - kN/m³
 * @property {number} frictionAngle - degrees
 * @property {number} cohesion - kPa
 * @property {number|null} depthToBottom - m, null = infinite
 * @property {string} color - hex
 */

/**
 * @typedef {Object} UDL
 * @property {string} id
 * @property {number} magnitude - kPa
 * @property {number} offset - m from crest
 * @property {number} length - m
 */

/**
 * @typedef {Object} LineLoad
 * @property {string} id
 * @property {number} magnitude - kN/m
 * @property {number} offset - m from crest
 */

/**
 * @typedef {Object} AnalysisSettings
 * @property {number} numSlices
 * @property {number} numIterations
 * @property {number} tolerance
 */

/**
 * @typedef {Object} AnalysisPayload
 * @property {SlopeGeometry} geometry
 * @property {SoilLayer[]} layers
 * @property {UDL[]} udls
 * @property {LineLoad[]} lineLoads
 * @property {number|null} waterDepth
 * @property {AnalysisSettings} settings
 */
```

---

## Zustand Store Design (JavaScript)

```javascript
// store/geometryStore.js
import { create } from 'zustand';
import { deriveGeometry } from '../utils/geometry';

export const useGeometryStore = create((set) => ({
  height: 10,
  angle: 30,
  length: null,
  derived: 'length',

  setHeight: (h) => set((s) => deriveGeometry({ ...s, height: h })),
  setAngle: (a) => set((s) => deriveGeometry({ ...s, angle: a })),
  setLength: (l) => set((s) => deriveGeometry({ ...s, length: l })),
  setGeometry: (g) => set(deriveGeometry(g)),
}));
```

```javascript
// store/materialsStore.js
import { create } from 'zustand';
import { nanoid } from 'nanoid';
import { GEO_PALETTE } from '../utils/constants';

export const useMaterialsStore = create((set) => ({
  layers: [
    {
      id: nanoid(),
      name: 'Soil Layer',
      unitWeight: 18,
      frictionAngle: 30,
      cohesion: 10,
      depthToBottom: null,
      color: GEO_PALETTE[0],
    },
  ],

  addLayer: (layer) => set((s) => ({
    layers: [...s.layers, { ...layer, id: layer.id || nanoid(), color: layer.color || GEO_PALETTE[s.layers.length % GEO_PALETTE.length] }],
  })),
  updateLayer: (id, updates) => set((s) => ({
    layers: s.layers.map((l) => (l.id === id ? { ...l, ...updates } : l)),
  })),
  removeLayer: (id) => set((s) => ({ layers: s.layers.filter((l) => l.id !== id) })),
}));
```

```javascript
// store/loadsStore.js
import { create } from 'zustand';
import { nanoid } from 'nanoid';

export const useLoadsStore = create((set) => ({
  udls: [],
  lineLoads: [],

  addUDL: (udl) => set((s) => ({ udls: [...s.udls, { ...udl, id: udl.id || nanoid() }] })),
  updateUDL: (id, updates) => set((s) => ({
    udls: s.udls.map((l) => (l.id === id ? { ...l, ...updates } : l)),
  })),
  removeUDL: (id) => set((s) => ({ udls: s.udls.filter((l) => l.id !== id) })),

  addLineLoad: (load) => set((s) => ({ lineLoads: [...s.lineLoads, { ...load, id: load.id || nanoid() }] })),
  updateLineLoad: (id, updates) => set((s) => ({
    lineLoads: s.lineLoads.map((l) => (l.id === id ? { ...l, ...updates } : l)),
  })),
  removeLineLoad: (id) => set((s) => ({ lineLoads: s.lineLoads.filter((l) => l.id !== id) })),
}));
```

```javascript
// store/waterStore.js
import { create } from 'zustand';

export const useWaterStore = create((set) => ({
  enabled: false,
  depth: 6,
  unitWeight: 9.81,

  setEnabled: (enabled) => set({ enabled }),
  setDepth: (depth) => set({ depth }),
  setUnitWeight: (uw) => set({ unitWeight: uw }),
}));
```

```javascript
// store/settingsStore.js
import { create } from 'zustand';

export const useSettingsStore = create((set) => ({
  numSlices: 50,
  numIterations: 2000,
  tolerance: 0.001,

  setNumSlices: (n) => set({ numSlices: n }),
  setNumIterations: (n) => set({ numIterations: n }),
  setTolerance: (t) => set({ tolerance: t }),
}));
```

---

## Utils

```javascript
// utils/geometry.js
export function deriveGeometry(g) {
  const { height, angle, length } = g;
  if (height != null && angle != null) {
    const len = height / Math.tan((angle * Math.PI) / 180);
    return { ...g, length: len, derived: 'length' };
  }
  if (height != null && length != null) {
    const ang = Math.atan(height / length) * (180 / Math.PI);
    return { ...g, angle: ang, derived: 'angle' };
  }
  if (angle != null && length != null) {
    const h = length * Math.tan((angle * Math.PI) / 180);
    return { ...g, height: h, derived: 'height' };
  }
  return g;
}
```

```javascript
// utils/constants.js
export const GEO_PALETTE = ['#c8a96e', '#a0785a', '#7a9e7e', '#5b7fa6', '#8c6b4a'];

export const fosColor = (fos) =>
  fos < 1.0 ? '#ef4444' : fos < 1.25 ? '#f97316' : fos < 1.5 ? '#eab308' : '#22c55e';
```

---

## API Layer

```javascript
// api/slopeApi.js
import axios from 'axios';

export async function analyzeSlope(payload) {
  const [results, image] = await Promise.all([
    axios.post('/analyze', payload),
    axios.post('/analyze-image', payload, { responseType: 'blob' }),
  ]);
  return {
    fos: results.data.factor_of_safety,
    status: results.data.stability_status ?? results.data.status,
    warnings: results.data.warnings ?? [],
    imageUrl: URL.createObjectURL(image.data),
  };
}
```

---

## Hooks

```javascript
// hooks/useAnalysis.js
import { useMutation } from '@tanstack/react-query';
import { analyzeSlope } from '../api/slopeApi';
import { useGeometryStore } from '../store/geometryStore';
import { useMaterialsStore } from '../store/materialsStore';
import { useLoadsStore } from '../store/loadsStore';
import { useWaterStore } from '../store/waterStore';
import { useSettingsStore } from '../store/settingsStore';

function buildPayload() {
  const geo = useGeometryStore.getState();
  const mat = useMaterialsStore.getState();
  const loads = useLoadsStore.getState();
  const water = useWaterStore.getState();
  const settings = useSettingsStore.getState();
  return {
    geometry: { height: geo.height, angle: geo.angle, length: geo.length, derived: geo.derived },
    layers: mat.layers,
    udls: loads.udls,
    lineLoads: loads.lineLoads,
    waterDepth: water.enabled ? water.depth : null,
    settings: {
      numSlices: settings.numSlices,
      numIterations: settings.numIterations,
      tolerance: settings.tolerance,
    },
  };
}

export function useAnalysis() {
  return useMutation({
    mutationFn: () => analyzeSlope(buildPayload()),
  });
}
```

---

## Canvas Architecture (Konva)

```
<Stage>
  <Layer>  ← GridBackground
  <Layer>  ← SoilLayerBands
  <Layer>  ← WaterTableLine (draggable)
  <Layer>  ← SlopeShape (with drag handles)
  <Layer>  ← LoadArrows
  <Layer>  ← DimensionLabels
</Stage>
```

**Coordinate system:**
- World coords in meters
- `scale = canvasWidth / worldWidth`
- `px = meters * scale`

---

## Layout (CSS Grid)

```css
.app-shell {
  display: grid;
  grid-template-rows: 56px 1fr 280px;
  grid-template-columns: 1fr 380px;
}
.canvas { grid-area: 2 / 1; }
.tabs   { grid-area: 2 / 2; }
.results { grid-row: 3; grid-column: 1 / -1; }
```

---

## Build & Dev Setup

```bash
npm create vite@latest frontend -- --template react
cd frontend
npm install zustand @tanstack/react-query react-konva konva react-hook-form axios nanoid
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

**vite.config.js proxy:**
```javascript
export default defineConfig({
  server: {
    proxy: {
      '/analyze': 'http://localhost:8000',
      '/analyze-image': 'http://localhost:8000',
    },
  },
});
```

---

## Recommended Build Sequence

1. **Stores + utils** — geometryStore, materialsStore, loadsStore, waterStore, settingsStore + geometry.js, constants.js
2. **slopeApi.js + useAnalysis** — test against live FastAPI (ensure backend has `/analyze-image`)
3. **AppShell layout** — 3-panel grid, empty panes
4. **GeometryPanel + static canvas** — wire store to form, render static slope polygon
5. **Konva canvas with drag handles** — toe, crest, angle handles → geometryStore
6. **MaterialsPanel + LoadsPanel** — table CRUD
7. **WaterTableLine** on canvas
8. **RunButton + ResultsPanel + DiagramViewer** — full round-trip
9. **Polish** — history, warnings, FOS color coding

---

## Backend Payload Shape (for FastAPI)

Ensure `/analyze` and `/analyze-image` accept:

```json
{
  "geometry": { "height": 10, "angle": 30, "length": 17.32 },
  "layers": [
    { "name": "Soil", "unitWeight": 18, "frictionAngle": 30, "cohesion": 10, "depthToBottom": null }
  ],
  "udls": [{ "magnitude": 50, "offset": 2, "length": 5 }],
  "lineLoads": [],
  "waterDepth": 6,
  "settings": { "numSlices": 50, "numIterations": 2000, "tolerance": 0.001 }
}
```

Backend must map this to `SlopeStabilityAnalyzer` and return `factor_of_safety`, `stability_status`, and PNG bytes for `/analyze-image`.
