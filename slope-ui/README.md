# Slope Stability Analyzer — Frontend

React + Vite frontend for the Slope Stability Analyzer. Connects to the FastAPI backend for analysis and diagram generation.

## Tech Stack

| Role        | Library              |
|------------|----------------------|
| Build      | Vite 5               |
| UI         | React 18             |
| Canvas     | react-konva + konva  |
| State      | Zustand              |
| Server     | TanStack Query v5    |
| HTTP       | axios                |
| Styling    | CSS (ui.html theme)  |

## Setup

```bash
npm install
npm run dev
```

The app runs at **http://localhost:5173** (or the port Vite shows).

**Backend required:** The FastAPI backend must be running at **http://localhost:8000**. The Vite dev server proxies `/analyze` and `/analyze-image` to it.

## Project Structure

```
src/
├── api/
│   └── slopeApi.js       # axios calls to /analyze and /analyze-image
├── store/                # Zustand state slices
│   ├── geometryStore.js
│   ├── materialsStore.js
│   ├── loadsStore.js
│   ├── waterStore.js
│   ├── settingsStore.js
│   └── resultsStore.js
├── hooks/
│   ├── useAnalysis.js    # TanStack mutation for analysis
│   └── useCanvasCoords.js # metres ↔ pixels transform
└── components/
    ├── canvas/           # Konva layers (grid, slope, loads, water, labels)
    ├── panels/           # Geometry, Materials, Loads, Water, Settings
    ├── results/          # FOS display, DiagramViewer
    └── layout/           # AppShell, TabPanel, ViewerTabs
```

## Features

- **Visualizer tab** — Interactive Konva canvas: slope geometry, soil layers, loads, water table
- **Image tab** — Backend-generated PNG diagram (enabled after running analysis)
- **Right sidebar** — Tabbed forms for geometry, materials, loads, water, settings
- **Results strip** — Factor of Safety, status badge, method info

## API Contract

### POST /analyze

**Request body:** See main project README for full payload format.

**Response:**
```json
{
  "factor_of_safety": 1.423,
  "status": "stable",
  "stability_status": "stable",
  "method": "Bishop Simplified",
  "warnings": []
}
```

### POST /analyze-image

Same request body. Returns a PNG image (slope diagram with failure circle).

## Customizing the API URL

Edit `vite.config.js`:

```js
server: {
  proxy: {
    '/analyze': { target: 'http://localhost:8000' },
    '/analyze-image': { target: 'http://localhost:8000' }
  }
}
```

For production, set `VITE_API_BASE` and update `src/api/slopeApi.js` to use it.

## Scripts

| Command       | Description              |
|---------------|--------------------------|
| `npm run dev` | Start dev server         |
| `npm run build` | Production build       |
| `npm run preview` | Preview production build |
