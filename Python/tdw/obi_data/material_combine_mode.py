from enum import IntEnum


class MaterialCombineMode(IntEnum):
    """
    Combine modes for Obi collisions.
    """

    average = 0  # The two friction values are averaged.
    minimum = 1  # The smallest of the two values is used.
    multiply = 2  # The friction values are multiplied with each other.
    maximum = 3  # The largest of the two values is used.
