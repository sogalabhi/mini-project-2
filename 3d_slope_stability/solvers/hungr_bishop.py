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


def _evaluate_direction_fs(
    rows: Sequence[AnalysisRow],
    direction_rad: float,
    config: MethodRunConfig,
) -> DirectionResult:
    fs_prev = 1.5
    iterations = 0
    total_drive = 0.0
    drive_x = 0.0
    drive_y = 0.0
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
                math.cos(alpha),
                math.tan(phi),
                max(0.2, abs(math.cos(delta))),
            )
        )

    for iteration in range(config.solver.max_iterations):
        iterations = iteration + 1
        resisting_sum = 0.0
        driving_sum = 0.0
        total_drive = 0.0

        for weight, cohesion_term, normal_force, sin_alpha, cos_alpha, tan_phi, alignment in precomputed:
            drive_i = weight * sin_alpha * alignment
            m_alpha = cos_alpha + safe_divide(sin_alpha * tan_phi, fs_prev, 0.0)
            m_alpha = max(1e-9, m_alpha)
            resist_i = (cohesion_term + normal_force * tan_phi) / m_alpha

            driving_sum += drive_i
            resisting_sum += resist_i
            total_drive += drive_i

        fs_new_raw = safe_divide(resisting_sum, driving_sum, default=0.0)
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
        },
        failure_reason="max_iterations_exceeded",
    )


def run_hungr_bishop(
    rows: Sequence[AnalysisRow],
    config: MethodRunConfig,
) -> MethodComputationResult:
    if config.method_id != MethodId.HUNGR_BISHOP.value:
        raise ValueError("run_hungr_bishop requires method_id = 1")
    if not rows:
        return MethodComputationResult(
            method_id=MethodId.HUNGR_BISHOP,
            fs_min=None,
            critical_direction_rad=None,
            converged=False,
            direction_results=[],
            diagnostics={"message": "No analysis rows provided"},
        )

    initial = estimate_initial_direction(rows)
    candidates = build_direction_candidates(initial, config.direction)
    direction_results: List[DirectionResult] = [
        _evaluate_direction_fs(rows, theta, config) for theta in candidates
    ]
    return aggregate_method_result(MethodId.HUNGR_BISHOP, direction_results)

