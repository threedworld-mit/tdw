from enum import IntFlag


class CardinalDirection(IntFlag):
    """
    Enum for cardinal directions.
    """

    north = 1
    east = 2
    south = 4
    west = 8
