import math
from typing import List, Sequence

from ..config.method_options import DirectionSearchConfig
from ..domain.models import AnalysisRow


def estimate_initial_direction(rows: Sequence[AnalysisRow]) -> float:
    """
    Estimate initial sliding direction from average base dip direction.
    Returns radians in [0, 2*pi).
    """
    if not rows:
        return 0.0
    sin_sum = 0.0
    cos_sum = 0.0
    for row in rows:
        theta = row.column_state.base_dip_direction_rad
        sin_sum += math.sin(theta)
        cos_sum += math.cos(theta)
    if abs(sin_sum) < 1e-12 and abs(cos_sum) < 1e-12:
        return 0.0
    return math.atan2(sin_sum, cos_sum) % (2.0 * math.pi)


def build_direction_candidates(
    initial_direction_rad: float,
    config: DirectionSearchConfig,
) -> List[float]:
    if config.user_direction_deg is not None:
        return [math.radians(config.user_direction_deg)]

    spacing_rad = math.radians(config.spacing_deg)
    tol_rad = math.radians(config.tolerance_deg)

    if tol_rad == 0:
        return [initial_direction_rad % (2.0 * math.pi)]

    steps = int(round((2.0 * tol_rad) / spacing_rad))
    candidates = []
    for step in range(steps + 1):
        offset = -tol_rad + step * spacing_rad
        candidates.append((initial_direction_rad + offset) % (2.0 * math.pi))

    # keep deterministic unique ordering
    unique = []
    seen = set()
    for value in candidates:
        key = round(value, 12)
        if key in seen:
            continue
        seen.add(key)
        unique.append(value)
    return unique

