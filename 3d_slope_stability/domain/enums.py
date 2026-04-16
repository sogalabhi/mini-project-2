from enum import Enum


class MethodId(int, Enum):
    HUNGR_BISHOP = 1
    HUNGR_JANBU_SIMPLIFIED = 2
    HUNGR_JANBU_CORRECTED = 3
    CHENG_YIP_BISHOP = 4
    CHENG_YIP_JANBU_SIMPLIFIED = 5
    CHENG_YIP_JANBU_CORRECTED = 6
    CHENG_YIP_SPENCER = 7


class InterpolationType(str, Enum):
    A1 = "a1"
    B1 = "b1"
    B2 = "b2"
    B3 = "b3"
    B4 = "b4"
    B5 = "b5"
    B6 = "b6"
    C1 = "c1"
    C2 = "c2"
    C3 = "c3"
    C4 = "c4"
    C5 = "c5"
    C6 = "c6"


class SlipSurfaceType(str, Enum):
    ELLIPSOID = "ellipsoid"
    USER_DEFINED = "user_defined"


class ShearModelType(int, Enum):
    MOHR_COULOMB = 1
    UNDRAINED_DEPTH = 2
    UNDRAINED_DATUM = 3
    POWER_CURVE = 4
    USER_DEFINED_CURVE = 5

