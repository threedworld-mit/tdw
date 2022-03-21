from enum import Enum


class EmitterSamplingMethod(Enum):
    """
    The sampling type for the shape of an Obi fluid emitter.
    """

    surface = 1  # Particles are distributed on the surface of the shape.
    volume = 2  # Particles are distributed on the surface of the shape and within the shape.
