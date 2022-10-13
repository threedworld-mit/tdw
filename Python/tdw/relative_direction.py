from enum import Enum


class RelativeDirection(Enum):
    """
    Enum values for a direction relative to a forward vector.
    """

    front = 1
    back = 2
    left = 4
    right = 8
    up = 16
    down = 32
    center = 64
