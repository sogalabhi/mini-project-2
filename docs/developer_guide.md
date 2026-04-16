# Developer Guide: 3D LEM Rewrite

## Architecture Guide

Top-level package: `3d_slope_stability`

- `config/`: runtime/config schemas and method options.
- `domain/`: typed models, enums, and error taxonomy.
- `io/`: validated CSV readers/writers/parsers.
- `geometry/`: deterministic grid/interpolation/surface intersection/primitives.
- `hydro/`: pore-pressure and groundwater calculations.
- `strength/`: strength models and resolver.
- `analysis/`: canonical analysis row builder and compatibility exports.
- `solvers/`: method implementations and solver-core utilities.
- `pipeline/`: orchestration, dispatcher, public APIs, CLI.
- `benchmarks/`: benchmark matrix and stage-level timers.

## Module Responsibilities

- Keep business logic in dedicated modules (no mixed concerns).
- Keep import side effects out of all modules.
- Use typed `domain.models` objects between layers.
- Validate all external input at IO boundary.
- Keep solver diagnostics explicit in result objects.

## Extension Instructions (Adding a New Method)

1. Create a new solver module under `solvers/`.
2. Reuse:
   - `solvers/common.py` for convergence/math helpers,
   - `solvers/direction_search.py` for candidate generation,
   - `solvers/results.py` for result aggregation.
3. Return `MethodComputationResult` with populated diagnostics.
4. Register method dispatch in `pipeline/dispatcher.py`.
5. Add:
   - unit tests for convergence + trend behavior,
   - integration test through `run_pipeline(...)`.
6. Document equations/assumptions in method notes under `docs/`.

## Coding Conventions

- Internal angles are radians.
- Canonical objects are immutable dataclasses where practical.
- Avoid positional magic-column usage in core logic.
- Prefer deterministic implementations for test reproducibility.

## Testing Workflow

- Unit tests: module-level correctness.
- Integration tests: preprocess + solver chain.
- Regression tests: bounded output envelopes.
- Failure tests: input and convergence edge cases.
- Benchmark tests: performance instrumentation validity.

Run all tests:

- `python -m pytest -q`

