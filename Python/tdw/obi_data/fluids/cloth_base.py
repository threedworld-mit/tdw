from abc import ABC, abstractmethod
from overrides import final
from typing import Dict


class ClothBase(ABC):
    """
    Abstract base class for Obi cloth materials.
    """

    def __init__(self, 
                 distance_constraints_enabled: bool, 
                 bend_constraints_enabled: bool, 
                 #volume_constraints_enabled: bool, 
                 aerodynamics_constraints_enabled: bool,
                 tether_constraints_enabled: float = bool, 
                 stretching_scale: float = 1.0,
                 stretch_compliance: float = 0,
                 max_compression: float = 0,
                 max_bending: float = 0.05,
                 bend_compliance: float = 0,
                 drag: float = 0.05,
                 lift: float = 0.05,
                 tether_compliance: float = 0,
                 tether_scale: float = 1.0,
                ):
        """
        :param distance_constraints_enabled: Are distance constraints enabled?
        :param bend_constraints_enabled: Are bend constraints enabled?
        :param aerodynamics_constraints_enabled: Are aerodynamics constraints enabled?
        :param tether_constraints_enabled: Are tether constraints enabled?


        :param stretching_scale: The size and amount of particles in 1 cubic meter.
        :param stretch_compliance: The visual color of the fluid.
        :param max_compression: The fluid density in kg/m3.

        :param max_bending: This scales the size at which particles are drawn.
        :param bend_compliance: Random velocity of emitted particles.

        :param drag: This scales the size at which particles are drawn.
        :param lift: Random velocity of emitted particles.

        :param tether_compliance: This scales the size at which particles are drawn.
        :param tether_scale: Random velocity of emitted particles.
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
