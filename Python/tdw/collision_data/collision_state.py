from enum import IntEnum


class CollisionState(IntEnum):
    """
    Enum values describing a collision state.
    """

    none = 0
    enter = 1
    stay = 2
    exit = 4
