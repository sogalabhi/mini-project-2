import math
from dataclasses import dataclass
from typing import Dict, Sequence, Tuple

from ..config.method_options import ReinforcementConfig
from ..domain.models import AnalysisRow


@dataclass(frozen=True)
class ReinforcementComputation:
    enabled: bool
    tensile_capacity: float
    bond_capacity: float
    t_max: float
    q_nail: float
    vertical_factor: float
    per_column: Dict[int, float]


def compute_reinforcement_contribution(
    rows: Sequence[AnalysisRow],
    reinforcement: ReinforcementConfig,
) -> ReinforcementComputation:
    if not reinforcement.enabled:
        return ReinforcementComputation(
            enabled=False,
            tensile_capacity=0.0,
            bond_capacity=0.0,
            t_max=0.0,
            q_nail=0.0,
            vertical_factor=0.0,
            per_column={row.column_id: 0.0 for row in rows},
        )

    tensile_capacity = reinforcement.steel_area * reinforcement.yield_strength
    bond_capacity = math.pi * reinforcement.diameter * reinforcement.length_embed * reinforcement.bond_strength
    t_max = min(tensile_capacity, bond_capacity)
    q_nail = t_max / (reinforcement.spacing_x * reinforcement.spacing_y)
    vertical_factor = math.tan(math.radians(reinforcement.inclination_deg)) if reinforcement.include_vertical_component else 0.0
    per_column = {
        row.column_id: q_nail * max(0.0, row.column_state.base_area)
        for row in rows
    }

    return ReinforcementComputation(
        enabled=True,
        tensile_capacity=tensile_capacity,
        bond_capacity=bond_capacity,
        t_max=t_max,
        q_nail=q_nail,
        vertical_factor=vertical_factor,
        per_column=per_column,
    )


def reinforcement_diagnostics(comp: ReinforcementComputation) -> Dict[str, float]:
    total_added = sum(comp.per_column.values())
    return {
        "enabled": 1.0 if comp.enabled else 0.0,
        "t_y": comp.tensile_capacity,
        "t_bond": comp.bond_capacity,
        "t_max": comp.t_max,
        "q_nail": comp.q_nail,
        "total_added_resistance": total_added,
        "vertical_factor": comp.vertical_factor,
    }


def per_column_diagnostics(comp: ReinforcementComputation) -> Dict[str, float]:
    return {str(k): v for k, v in comp.per_column.items()}

