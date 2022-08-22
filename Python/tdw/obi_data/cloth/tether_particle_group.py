from enum import Enum


class TetherParticleGroup(Enum):
    """
    A group of particles from which an Obi cloth sheet can be tethered to another object.

    All directions are from the vantage point of looking down at a sheet spread out on the floor.
    """

    four_corners = 1
    north_corners = 2
    south_corners = 4
    east_corners = 8
    west_corners = 16
    north_edge = 32
    south_edge = 64
    east_edge = 128
    west_edge = 256
    center = 512
