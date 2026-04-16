# 3D Backend API Handoff for UI Integration

## Base

- Prefix: `/api/v1/3d`
- Legacy 2D routes remain unchanged (`/analyze`, `/analyze-image`).

## Endpoints

- `GET /api/v1/3d/methods`
  - returns frozen method ids/labels (`1..7`).
- `POST /api/v1/3d/validate`
  - validates payload without solver execution.
- `POST /api/v1/3d/analyze`
  - executes one method run.
- `POST /api/v1/3d/analyze/multi`
  - executes multiple methods and returns per-method status.

## Analyze Request Shape

Top-level fields:

- `method_config`
- `grid_config`
- `slip_surface_config`
- `materials`
- `top_surface` or `surface_paths/surface_types/interpolation_modes`
- optional `user_slip_surface`
- optional `water_level_z`
- optional `reinforcement`
- `debug.include_analysis_rows` (default false)

Reinforcement object shape:

- `enabled` (bool)
- `diameter`
- `length_embed`
- `spacing_x`, `spacing_y`
- `steel_area`
- `yield_strength`
- `bond_strength`
- `inclination_deg`
- `include_vertical_component`

## Analyze Response Shape

- `column_count`
- `fs_min`
- `critical_direction_rad`
- `converged`
- `method_id`
- `direction_results[]`
- `diagnostics.pipeline`
- `diagnostics.method`
- optional `render_data` (when `debug.include_render_geometry=true`)
- method diagnostics include reinforcement metrics when enabled:
  - `t_y`, `t_bond`, `t_max`, `q_nail`, `total_added_resistance`
- `generated_files[]`
- optional `analysis_rows[]` when debug flag is enabled and within row limits

`render_data` shape (preview contract):

- `top_surface_points[]`: normalized `{x,y,z}` points used by terrain layer
- `columns[]`: `{column_id, x_center, y_center, z_top, z_base, thickness, is_active}`
- `fs_field`:
  - `scalar_by_column_id` (local proxy values)
  - `min`, `max`
  - `units`, `mapping_mode`
- `morphology`:
  - `method`, `confidence`
  - `crest_ids[]`, `face_ids[]`, `toe_ids[]`

## Error Envelope

On backend validation/domain errors (`400`):

```json
{
  "detail": {
    "code": "invalid_3d_payload",
    "message": "human-readable reason"
  }
}
```

On payload too large (`413`):

```json
{
  "detail": {
    "code": "payload_too_large",
    "message": "request payload exceeds 2MB limit"
  }
}
```

## UI Integration Notes

- Keep existing 2D flow untouched.
- Add 3D mode branch in client hook:
  - 2D -> existing `analyzeSlope`
  - 3D -> `POST /api/v1/3d/analyze`
- Render stable fields first (`fs_min`, `critical_direction_rad`, `converged`, diagnostics summary).
- Keep `analysis_rows` opt-in only; payload may be large.
- `debug.include_render_geometry` defaults true for preview layers.
- For heavy scenes, frontend should cap prism rendering and auto-fallback to lines/centers.
- Recommended reinforcement disclaimer string:
  - "Simplified phase-2 uniform column-based reinforcement approximation; full direction-aware intersection is deferred."

