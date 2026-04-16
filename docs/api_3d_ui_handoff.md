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
- `debug.include_analysis_rows` (default false)

## Analyze Response Shape

- `column_count`
- `fs_min`
- `critical_direction_rad`
- `converged`
- `method_id`
- `direction_results[]`
- `diagnostics.pipeline`
- `diagnostics.method`
- `generated_files[]`
- optional `analysis_rows[]` when debug flag is enabled and within row limits

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

