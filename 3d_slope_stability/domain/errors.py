class ThreeDLEMError(Exception):
    """Base exception for rewritten 3D LEM module."""


class InputValidationError(ThreeDLEMError):
    """Raised when input data/schema is invalid."""


class InterpolationError(ThreeDLEMError):
    """Raised for interpolation backend failures."""


class GeometryError(ThreeDLEMError):
    """Raised for invalid or inconsistent geometric states."""


class ConvergenceError(ThreeDLEMError):
    """Raised when an iterative solver fails to converge."""


class MethodNotSupportedError(ThreeDLEMError):
    """Raised when a requested method is not implemented/supported."""

