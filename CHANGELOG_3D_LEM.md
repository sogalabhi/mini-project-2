# Changelog - 3D LEM Rewrite

## v0.1.0-rc1 (2026-04-15)

## Added

- Clean-room 3D LEM package scaffold under `3d_slope_stability`.
- Typed domain contracts, enums, error model, and configuration schemas.
- Validated IO layer for CSV parsing/writing and boundary checks.
- Deterministic geometry/interpolation and slip-surface intersection engines.
- Hydro + strength model modules.
- Canonical analysis row builder.
- Solver core utilities and direction-search infrastructure.
- Method implementations:
  - Hungr-Bishop
  - Hungr-Janbu simplified/corrected
  - Cheng-Yip Bishop-like/Janbu-like/Spencer-like
- Pipeline orchestration, dispatch, and CLI entrypoint.
- Benchmarking matrix and stage-level profiling.
- Multi-layer testing program (unit/integration/regression/property/failure).

## Documentation

- Rewrite spec and risk register.
- Method notes and mathematical model references.
- Developer and operator guides.
- Migration notes.
- API freeze + quality gates + release-candidate validation reports.

## Quality Snapshot

- Tests: `32 passed`
- Compile checks: pass
- Benchmark thresholds: pass

## Known Limitations

- Advanced method equations include controlled deterministic approximations and are
  not guaranteed to be publication-grade parity with all historical formulations.
- Legacy numeric parity is range/tolerance-based, not bitwise exact.
- Current benchmark fixture is synthetic and should be complemented by project-
  specific geotechnical benchmark datasets for production qualification.

