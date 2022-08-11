from enum import Enum


class ForceMode(Enum):
    """
    Force modes for Obi actors.
    """

    force = 0  # Add a continuous force to the object, using its mass.
    impulse = 1  # Add an instant force impulse to the object, using its mass.
    velocity_change = 2  # Add an instant velocity change to the object, ignoring its mass.
    acceleration = 3  # Add a continuous acceleration to the object, ignoring its mass.
