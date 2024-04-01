from enum import Enum


class EyeState(Enum):
    """
    The state of a FOVE eye.
    """

    not_detected = 0
    opened = 1
    closed = 2
    converged = 3
