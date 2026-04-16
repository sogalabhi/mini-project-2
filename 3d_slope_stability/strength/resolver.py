import math
from typing import Dict, Optional, Sequence, Tuple

from ..domain.enums import ShearModelType
from ..domain.errors import InputValidationError
from ..domain.models import MaterialDefinition, StrengthState
from .models import (
    mohr_coulomb_shear_strength,
    power_curve_shear_strength,
    undrained_datum_cohesion,
    undrained_depth_cohesion,
    user_curve_shear_strength,
)
from .unsaturated import unsaturated_shear_increment


def resolve_strength_state(
    material: MaterialDefinition,
    z: float,
    z_top: float,
    effective_normal_stress: float,
    *,
    matric_suction: float = 0.0,
    unsaturated_params: Optional[Tuple[float, float, float]] = None,
    user_curve_points: Optional[Sequence[Tuple[float, float]]] = None,
) -> StrengthState:
    """
    Resolve equivalent strength state from configured material model.
    """
    params = material.model_parameters
    diagnostics: Dict[str, float] = {}

    if material.model_type == ShearModelType.MOHR_COULOMB.value:
        if len(params) < 2:
            raise InputValidationError("Mohr-Coulomb model requires (phi_deg, cohesion)")
        phi_deg, cohesion = params[0], params[1]
        phi_rad = math.radians(phi_deg)
        shear = mohr_coulomb_shear_strength(effective_normal_stress, phi_rad, cohesion)
        model_name = "mohr_coulomb"

    elif material.model_type == ShearModelType.UNDRAINED_DEPTH.value:
        if len(params) < 4:
            raise InputValidationError(
                "Undrained depth model requires (su_max, su_min, su_top, su_gradient)"
            )
        su_max, su_min, su_top, su_gradient = params[0], params[1], params[2], params[3]
        cohesion = undrained_depth_cohesion(z, z_top, su_top, su_gradient, su_min, su_max)
        phi_rad = 0.0
        shear = cohesion
        model_name = "undrained_depth"

    elif material.model_type == ShearModelType.UNDRAINED_DATUM.value:
        if len(params) < 5:
            raise InputValidationError(
                "Undrained datum model requires (su_max, su_min, su_datum, su_gradient, z_datum)"
            )
        su_max, su_min, su_datum, su_gradient, z_datum = (
            params[0],
            params[1],
            params[2],
            params[3],
            params[4],
        )
        cohesion = undrained_datum_cohesion(z, z_datum, su_datum, su_gradient, su_min, su_max)
        phi_rad = 0.0
        shear = cohesion
        model_name = "undrained_datum"

    elif material.model_type == ShearModelType.POWER_CURVE.value:
        if len(params) < 3:
            raise InputValidationError("Power curve model requires (p_atm, a, b)")
        p_atm, a_param, b_param = params[0], params[1], params[2]
        shear = power_curve_shear_strength(effective_normal_stress, p_atm, a_param, b_param)
        # approximate equivalent cohesion as shear at zero normal stress
        cohesion = power_curve_shear_strength(1e-9, p_atm, a_param, b_param)
        phi_rad = 0.0
        model_name = "power_curve"

    elif material.model_type == ShearModelType.USER_DEFINED_CURVE.value:
        if not user_curve_points:
            raise InputValidationError("User curve model requires user_curve_points")
        shear = user_curve_shear_strength(effective_normal_stress, user_curve_points)
        cohesion = user_curve_shear_strength(0.0, user_curve_points)
        phi_rad = 0.0
        model_name = "user_curve"

    else:
        raise InputValidationError(f"Unsupported shear model type: {material.model_type}")

    if unsaturated_params is not None:
        phi_b_deg, aev, suction_cap = unsaturated_params
        increment = unsaturated_shear_increment(
            phi_b_rad=math.radians(phi_b_deg),
            air_entry_value=aev,
            matric_suction=matric_suction,
            suction_cap=suction_cap,
        )
        shear += increment
        diagnostics["unsat_increment"] = increment

    diagnostics["effective_normal_stress"] = float(effective_normal_stress)
    return StrengthState(
        friction_angle_rad=float(phi_rad),
        cohesion=float(cohesion),
        shear_strength=float(shear),
        model_name=model_name,
        diagnostics=diagnostics,
    )

