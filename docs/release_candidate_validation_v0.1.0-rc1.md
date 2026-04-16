# Release Candidate Validation (v0.1.0-rc1)

## Purpose

Phase 15.3 release-candidate validation artifact:

- end-to-end scenario suite outcome,
- sign-off report for equation and engineering validation.

## End-to-End Scenario Suite

## Scenario A - Ellipsoid + Bishop

- Method: `1` (Hungr-Bishop)
- Surface mode: `ellipsoid`
- Expected: positive converged `fs_min`, deterministic repeatability
- Outcome: PASS

## Scenario B - Ellipsoid + Janbu Pair

- Methods: `2`, `3`
- Expected: corrected (`3`) not lower than simplified (`2`) on controlled fixture
- Outcome: PASS

## Scenario C - Cheng-Yip Variants

- Methods: `4`, `5`, `6`, `7`
- Expected: convergence diagnostics available, coupled mismatch diagnostics for `7`
- Outcome: PASS

## Scenario D - Pipeline Integration

- Full preprocess -> rows -> dispatch -> method result
- Expected: non-empty canonical rows, valid method result object
- Outcome: PASS

## Scenario E - Failure/Validation Paths

- Invalid config and schema edge cases
- Expected: explicit domain/input validation errors
- Outcome: PASS

## Evidence Summary

- Unit/integration/regression/failure/property tests passed (32 total tests).
- Compile checks passed.
- Benchmarks passed threshold policy.

## Equation Validation Sign-off

- Equation contract reference: `docs/3D_LEM_REWRITE_SPEC_PHASE0.md`
- Method references:
  - `docs/method_notes_hungr.md`
  - `docs/method_notes_cheng_yip.md`
  - `docs/mathematical_model.md`
- Result: **Signed off for release candidate scope**.

## Engineering Validation Sign-off

- API freeze documented: `docs/api_freeze_v0.1.0.md`
- Quality gates documented: `docs/quality_gates_phase15.md`
- Diagnostics and deterministic behavior validated in tests.
- Result: **Signed off for release candidate scope**.

## RC Decision

Release candidate `v0.1.0-rc1` approved for baseline tagging and internal consumption.

