import math
from typing import Dict, List, Sequence, Tuple

from ..config.method_options import MethodRunConfig
from ..domain.enums import MethodId
from ..domain.models import AnalysisRow, DirectionResult, MethodComputationResult
from .common import apply_damping, decompose_force_2d, has_converged, safe_divide
from .direction_search import build_direction_candidates, estimate_initial_direction
from .lambda_update import update_lambda_bidirectional
from .results import aggregate_method_result


def _wrap_to_pi(value: float) -> float:
    return (value + math.pi) % (2.0 * math.pi) - math.pi


def _method_variant(method_id: int) -> str:
    if method_id == MethodId.CHENG_YIP_BISHOP.value:
        return "bishop_like"
    if method_id in (MethodId.CHENG_YIP_JANBU_SIMPLIFIED.value, MethodId.CHENG_YIP_JANBU_CORRECTED.value):
        return "janbu_like"
    if method_id == MethodId.CHENG_YIP_SPENCER.value:
        return "spencer_like"
    raise ValueError("Unsupported Cheng-Yip method id")


def _compute_pair_terms(
    precomputed_rows: Sequence[Tuple[float, float, float, float, float, float, float]],
    direction_rad: float,
    fs_prev: float,
    lambda_value: float,
    corrected_janbu: bool,
    avg_dip: float,
    avg_phi: float,
) -> Dict[str, float]:
    resisting_force = 0.0
    driving_force = 0.0
    resisting_moment = 0.0
    driving_moment = 0.0
    total_drive = 0.0

    for weight, cohesion_term, normal_force, tan_phi, sin_alpha, cos_alpha, alignment in precomputed_rows:
        drive_i = weight * sin_alpha * alignment
        force_resist_i = cohesion_term + normal_force * tan_phi + lambda_value * alignment * 0.1 * drive_i

        # Moment-like pair uses a stabilized bishop-style denominator term.
        m_alpha = cos_alpha + safe_divide(sin_alpha * tan_phi, max(fs_prev, 1e-6), 0.0)
        m_alpha = max(1e-9, m_alpha)
        moment_resist_i = force_resist_i / m_alpha

        driving_force += drive_i
        resisting_force += force_resist_i
        driving_moment += drive_i * (1.0 + 0.15 * sin_alpha)
        resisting_moment += moment_resist_i
        total_drive += drive_i

    fs_force = safe_divide(resisting_force, driving_force, 0.0)
    fs_moment = safe_divide(resisting_moment, driving_moment, 0.0)

    if corrected_janbu:
        correction = max(
            1.0,
            min(
                1.35,
                1.0
                + 0.08 * math.sin(avg_dip)
                + 0.05 * math.tan(avg_phi),
            ),
        )
        fs_force *= correction

    drive_x, drive_y = decompose_force_2d(total_drive, direction_rad)
    return {
        "fs_force": fs_force,
        "fs_moment": fs_moment,
        "driving_x": drive_x,
        "driving_y": drive_y,
        "driving_force": driving_force,
        "driving_moment": driving_moment,
    }


def _evaluate_direction(
    rows: Sequence[AnalysisRow],
    direction_rad: float,
    config: MethodRunConfig,
    method_id: int,
) -> DirectionResult:
    variant = _method_variant(method_id)
    corrected_janbu = method_id == MethodId.CHENG_YIP_JANBU_CORRECTED.value
    fs_prev = 1.5
    lambda_value = 0.0
    lambda_step = 0.2
    prev_mismatch = None
    prev_sign = None
    oscillation_total = 0
    lambda_traj: List[float] = [lambda_value]
    fs_pairs: List[Tuple[float, float]] = []
    mismatch_traj: List[float] = []
    avg_dip = sum(r.column_state.base_dip_rad for r in rows) / len(rows)
    avg_phi = sum(r.column_state.friction_angle_rad for r in rows) / len(rows)
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
                math.tan(phi),
                math.sin(alpha),
                math.cos(alpha),
                max(0.2, abs(math.cos(delta))),
            )
        )

    for iteration in range(config.solver.max_iterations):
        terms = _compute_pair_terms(
            precomputed,
            direction_rad,
            fs_prev,
            lambda_value,
            corrected_janbu,
            avg_dip,
            avg_phi,
        )
        fs_force = terms["fs_force"]
        fs_moment = terms["fs_moment"]
        fs_pairs.append((fs_force, fs_moment))
        mismatch = fs_force - fs_moment
        mismatch_traj.append(mismatch)

        if variant == "bishop_like":
            fs_new_raw = fs_moment
            coupled_ok = True
        elif variant == "janbu_like":
            fs_new_raw = fs_force
            coupled_ok = True
        else:
            # spencer-like: coupled force and moment condition
            fs_new_raw = 0.5 * (fs_force + fs_moment)
            coupled_ok = abs(mismatch) <= max(config.solver.tol_fs * 2.0, 0.2)
            if not coupled_ok:
                update = update_lambda_bidirectional(
                    current_lambda=lambda_value,
                    mismatch=mismatch,
                    prev_mismatch=prev_mismatch,
                    prev_sign=prev_sign,
                    step=lambda_step,
                    min_lambda=-1.0,
                    max_lambda=1.0,
                    min_step=1e-3,
                )
                lambda_value = update.lambda_value
                lambda_step = update.step
                oscillation_total += update.oscillation_count
                lambda_traj.append(lambda_value)
                if update.stalled:
                    return DirectionResult(
                        direction_rad=direction_rad,
                        converged=False,
                        fs_value=fs_prev,
                        iterations=iteration + 1,
                        method_terms={
                            "variant": 3.0,
                            "lambda_final": lambda_value,
                            "oscillation_count": float(oscillation_total),
                            "mismatch_final": mismatch,
                            "driving_x": terms["driving_x"],
                            "driving_y": terms["driving_y"],
                        },
                        failure_reason="lambda_stalled",
                    )
                prev_sign = 1 if mismatch > 0 else (-1 if mismatch < 0 else 0)
                prev_mismatch = mismatch

        fs_new = apply_damping(fs_new_raw, fs_prev, config.solver.damping)
        converged = has_converged(fs_new, fs_prev, config.solver.tol_fs)
        if converged and coupled_ok:
            variant_code = {"bishop_like": 1.0, "janbu_like": 2.0, "spencer_like": 3.0}[variant]
            return DirectionResult(
                direction_rad=direction_rad,
                converged=True,
                fs_value=fs_new,
                iterations=iteration + 1,
                method_terms={
                    "variant": variant_code,
                    "fs_force": fs_force,
                    "fs_moment": fs_moment,
                    "mismatch_final": mismatch,
                    "lambda_final": lambda_value,
                    "oscillation_count": float(oscillation_total),
                    "lambda_iterations": float(len(lambda_traj) - 1),
                    "driving_x": terms["driving_x"],
                    "driving_y": terms["driving_y"],
                    "lambda_traj_len": float(len(lambda_traj)),
                    "fs_pair_len": float(len(fs_pairs)),
                },
                failure_reason=None,
            )
        fs_prev = fs_new

    variant_code = {"bishop_like": 1.0, "janbu_like": 2.0, "spencer_like": 3.0}[variant]
    return DirectionResult(
        direction_rad=direction_rad,
        converged=False,
        fs_value=fs_prev,
        iterations=config.solver.max_iterations,
        method_terms={
            "variant": variant_code,
            "lambda_final": lambda_value,
            "oscillation_count": float(oscillation_total),
            "mismatch_final": mismatch_traj[-1] if mismatch_traj else 0.0,
            "lambda_traj_len": float(len(lambda_traj)),
            "fs_pair_len": float(len(fs_pairs)),
        },
        failure_reason="max_iterations_exceeded",
    )


def run_cheng_yip(
    rows: Sequence[AnalysisRow],
    config: MethodRunConfig,
) -> MethodComputationResult:
    if config.method_id not in {
        MethodId.CHENG_YIP_BISHOP.value,
        MethodId.CHENG_YIP_JANBU_SIMPLIFIED.value,
        MethodId.CHENG_YIP_JANBU_CORRECTED.value,
        MethodId.CHENG_YIP_SPENCER.value,
    }:
        raise ValueError("run_cheng_yip requires method_id in {4,5,6,7}")

    if not rows:
        return MethodComputationResult(
            method_id=MethodId(config.method_id),
            fs_min=None,
            critical_direction_rad=None,
            converged=False,
            direction_results=[],
            diagnostics={"message": "No analysis rows provided"},
        )

    initial = estimate_initial_direction(rows)
    candidates = build_direction_candidates(initial, config.direction)
    direction_results = [
        _evaluate_direction(rows, theta, config, method_id=config.method_id) for theta in candidates
    ]
    result = aggregate_method_result(MethodId(config.method_id), direction_results)
    mismatch_abs = [
        abs(dr.method_terms.get("mismatch_final", 0.0))
        for dr in direction_results
        if dr.method_terms
    ]
    result.diagnostics.update(
        {
            "variant": _method_variant(config.method_id),
            "candidate_count": len(candidates),
            "max_mismatch_abs": max(mismatch_abs) if mismatch_abs else None,
            "avg_mismatch_abs": (
                sum(mismatch_abs) / len(mismatch_abs) if mismatch_abs else None
            ),
        }
    )
    return result

