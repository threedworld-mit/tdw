from enum import Enum


class ClothVolumeType(Enum):
    """
    Enum values for cloth volumes.
    """

    ball = 1  # Spherical cloth volume.
    cube = 2  # Cubic cloth volume.
    block = 3  # Rectangular cubic cloth volume.
