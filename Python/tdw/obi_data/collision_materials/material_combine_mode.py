from enum import Enum


class MaterialCombineMode(Enum):
    """
    Modes for combining Obi collision materials.
    """

    average = 0
    minimum = 1
    multiply = 2
    maximum = 3
