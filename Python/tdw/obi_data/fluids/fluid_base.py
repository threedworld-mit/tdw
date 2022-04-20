from abc import ABC, abstractmethod
from overrides import final
from typing import Dict


class FluidBase(ABC):
    """
    Abstract base class for Obi fluids.
    """

    def __init__(self, capacity: int, resolution: float, color: Dict[str, float], rest_density: float,
                 radius_scale: float = 1.7, random_velocity: float = 0):
        """
        :param capacity: The maximum amount of emitted particles.
        :param resolution: The size and amount of particles in 1 cubic meter.
        :param color: The visual color of the fluid.
        :param rest_density: The fluid density in kg/m3.
        :param radius_scale: This scales the size at which particles are drawn.
        :param random_velocity: Random velocity of emitted particles.
        """

        """:field
        The maximum amount of emitted particles.
        """
        self.capacity: int = capacity
        """:field
        The size and amount of particles in 1 cubic meter.
        """
        self.resolution: float = resolution
        """:field
        The visual color of the fluid.
        """
        self.color: Dict[str, float] = color
        """:field
        The fluid density in kg/m3.
        """
        self.rest_density: float = rest_density
        """:field
        This scales the size at which particles are drawn.
        """
        self.radius_scale: float = radius_scale
        """:field
        Random velocity of emitted particles.
        """
        self.random_velocity: float = random_velocity

    @final
    def to_dict(self) -> dict:
        """
        :return: A JSON dictionary of this object.
        """

        d = {"$type": self._get_type()}
        d.update({k: v for k, v in self.__dict__.items()})
        return d

    @abstractmethod
    def _get_type(self) -> str:
        """
        :return: The serializable type name
        """

        raise Exception()
