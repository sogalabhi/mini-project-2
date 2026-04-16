from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class LambdaUpdateResult:
    lambda_value: float
    step: float
    oscillation_count: int
    diverged: bool
    stalled: bool


def update_lambda_bidirectional(
    current_lambda: float,
    mismatch: float,
    prev_mismatch: Optional[float],
    prev_sign: Optional[int],
    step: float,
    *,
    min_lambda: float = -1.0,
    max_lambda: float = 1.0,
    min_step: float = 1e-3,
    max_oscillation: int = 6,
) -> LambdaUpdateResult:
    """
    Bidirectional lambda update with oscillation/divergence safeguards.
    """
    sign = 0
    if mismatch > 0:
        sign = 1
    elif mismatch < 0:
        sign = -1

    oscillation_count = 0
    if prev_sign is not None and sign != 0 and prev_sign != 0 and sign != prev_sign:
        oscillation_count = 1
        step *= 0.5

    if prev_mismatch is not None and abs(mismatch) > abs(prev_mismatch) and sign != 0:
        step *= 0.5

    stalled = step < min_step
    if stalled:
        return LambdaUpdateResult(
            lambda_value=current_lambda,
            step=step,
            oscillation_count=oscillation_count,
            diverged=False,
            stalled=True,
        )

    candidate = current_lambda - sign * step
    diverged = candidate < min_lambda or candidate > max_lambda
    if diverged:
        candidate = max(min_lambda, min(max_lambda, candidate))

    return LambdaUpdateResult(
        lambda_value=candidate,
        step=step,
        oscillation_count=min(max_oscillation, oscillation_count),
        diverged=diverged,
        stalled=False,
    )

