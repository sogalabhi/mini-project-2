# Known Limitations (v0.1.0-rc1)

- The current Cheng-Yip and corrected branches prioritize deterministic stability for
  rewrite closure and may differ from alternative literature implementations.
- The interpolation adapter currently focuses on deterministic IDW-style behavior for
  core coverage; additional interpolation families can be expanded later.
- API is frozen for `v0.1.0-rc1` public interfaces only; private internals may evolve.
- Benchmark thresholds are validated on synthetic fixtures; field-specific calibration
  and dataset qualification remain required for deployment-critical decisions.
- Legacy compatibility is provided at method-ID and output-schema levels with
  tolerance-based acceptance, not exact legacy replica behavior.

