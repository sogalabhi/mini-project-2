import math
from typing import List, Sequence

from ..config.method_options import MethodRunConfig
from ..domain.enums import MethodId
from ..domain.models import AnalysisRow, DirectionResult, MethodComputationResult
from .common import apply_damping, decompose_force_2d, has_converged, safe_divide
from .direction_search import build_direction_candidates, estimate_initial_direction
from .results import aggregate_method_result


def _wrap_to_pi(value: float) -> float:
    return (value + math.pi) % (2.0 * math.pi) - math.pi


def _janbu_correction_factor(rows: Sequence[AnalysisRow]) -> float:
    """
    Lightweight deterministic correction factor approximation.
    """
    if not rows:
        return 1.0
    avg_dip = sum(row.column_state.base_dip_rad for row in rows) / len(rows)
    avg_phi = sum(row.column_state.friction_angle_rad for row in rows) / len(rows)
    factor = 1.0 + 0.08 * math.sin(max(0.0, avg_dip)) + 0.05 * math.tan(max(0.0, avg_phi))
    return max(1.0, min(1.35, factor))


def _evaluate_direction_fs(
    rows: Sequence[AnalysisRow],
    direction_rad: float,
    config: MethodRunConfig,
    corrected: bool,
) -> DirectionResult:
    fs_prev = 1.5
    iterations = 0
    total_drive = 0.0
    precomputed = []
    for row in rows:
        s = row.column_state
        alpha = max(0.0, s.base_dip_rad)
        phi = max(0.0, s.friction_angle_rad)
        delta = _wrap_to_pi(direction_rad - s.base_dip_direction_rad)
        precomputed.append(
            (
                max(0.0, s.weight),
                max(0.0, s.cohesion) * max(0.0, s.base_area),
                max(0.0, s.effective_normal_stress) * max(0.0, s.base_area),
                math.sin(alpha),
                math.tan(phi),
                max(0.2, abs(math.cos(delta))),
            )
        )

    for iteration in range(config.solver.max_iterations):
        iterations = iteration + 1
        resisting_sum = 0.0
        driving_sum = 0.0
        total_drive = 0.0

        for weight, cohesion_term, normal_force, sin_alpha, tan_phi, alignment in precomputed:
            drive_i = weight * sin_alpha * alignment
            resist_i = cohesion_term + normal_force * tan_phi

            driving_sum += drive_i
            resisting_sum += resist_i
            total_drive += drive_i

        fs_new_raw = safe_divide(resisting_sum, driving_sum, default=0.0)
        if corrected:
            fs_new_raw *= _janbu_correction_factor(rows)
        fs_new = apply_damping(fs_new_raw, fs_prev, config.solver.damping)

        if has_converged(fs_new, fs_prev, config.solver.tol_fs):
            drive_x, drive_y = decompose_force_2d(total_drive, direction_rad)
            return DirectionResult(
                direction_rad=direction_rad,
                converged=True,
                fs_value=fs_new,
                iterations=iterations,
                method_terms={
                    "resisting_sum": resisting_sum,
                    "driving_sum": driving_sum,
                    "driving_x": drive_x,
                    "driving_y": drive_y,
                    "correction_factor": _janbu_correction_factor(rows) if corrected else 1.0,
                },
                failure_reason=None,
            )
        fs_prev = fs_new

    drive_x, drive_y = decompose_force_2d(total_drive, direction_rad)
    return DirectionResult(
        direction_rad=direction_rad,
        converged=False,
        fs_value=fs_prev,
        iterations=iterations,
        method_terms={
            "driving_x": drive_x,
            "driving_y": drive_y,
            "correction_factor": _janbu_correction_factor(rows) if corrected else 1.0,
        },
        failure_reason="max_iterations_exceeded",
    )


def _run_janbu(
    rows: Sequence[AnalysisRow],
    config: MethodRunConfig,
    method_id: MethodId,
    corrected: bool,
) -> MethodComputationResult:
    if not rows:
        return MethodComputationResult(
            method_id=method_id,
            fs_min=None,
            critical_direction_rad=None,
            converged=False,
            direction_results=[],
            diagnostics={"message": "No analysis rows provided"},
        )
    initial = estimate_initial_direction(rows)
    candidates = build_direction_candidates(initial, config.direction)
    direction_results: List[DirectionResult] = [
        _evaluate_direction_fs(rows, theta, config, corrected=corrected) for theta in candidates
    ]
    return aggregate_method_result(method_id, direction_results)


def run_hungr_janbu_simplified(
    rows: Sequence[AnalysisRow],
    config: MethodRunConfig,
) -> MethodComputationResult:
    if config.method_id != MethodId.HUNGR_JANBU_SIMPLIFIED.value:
        raise ValueError("run_hungr_janbu_simplified requires method_id = 2")
    return _run_janbu(rows, config, MethodId.HUNGR_JANBU_SIMPLIFIED, corrected=False)


def run_hungr_janbu_corrected(
    rows: Sequence[AnalysisRow],
    config: MethodRunConfig,
) -> MethodComputationResult:
    if config.method_id != MethodId.HUNGR_JANBU_CORRECTED.value:
        raise ValueError("run_hungr_janbu_corrected requires method_id = 3")
    return _run_janbu(rows, config, MethodId.HUNGR_JANBU_CORRECTED, corrected=True)

