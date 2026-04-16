from typing import Iterable

from ..domain.enums import MethodId
from ..domain.models import DirectionResult, MethodComputationResult


def aggregate_method_result(
    method_id: MethodId,
    direction_results: Iterable[DirectionResult],
) -> MethodComputationResult:
    results = list(direction_results)
    converged = [r for r in results if r.converged and r.fs_value is not None]
    if not converged:
        return MethodComputationResult(
            method_id=method_id,
            fs_min=None,
            critical_direction_rad=None,
            converged=False,
            direction_results=results,
            diagnostics={"converged_count": 0, "total_count": len(results)},
        )

    best = min(converged, key=lambda item: float(item.fs_value))
    return MethodComputationResult(
        method_id=method_id,
        fs_min=float(best.fs_value),
        critical_direction_rad=best.direction_rad,
        converged=True,
        direction_results=results,
        diagnostics={"converged_count": len(converged), "total_count": len(results)},
    )

