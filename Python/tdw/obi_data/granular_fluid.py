from pkg_resources import resource_filename
from pathlib import Path
from json import loads
from typing import Dict


class GranularFluid:
    """
    Data for an Obi granular fluid. For more information, [read this](http://obi.virtualmethodstudio.com/manual/6.3/emittermaterials.html).
    """

    def __init__(self, capacity: int, color: Dict[str, float], randomness: float, resolution: float, rest_density: float):
        """
        :param capacity: The maximum amount of emitted particles.
        :param color: The visual color of the fluid.
        :param randomness: The variation in particle size.
        :param resolution: The size and amount of particles in 1 cubic meter.
        :param rest_density: The fluid density in kg/m3.
        """

        """:field
        The maximum amount of emitted particles.
        """
        self.capacity: int = capacity
        """:field
        The visual color of the fluid.
        """
        self.color: Dict[str, float] = color
        """:field
        The variation in particle size.
        """
        self.randomness: float = randomness
        """:field
        The size and amount of particles in 1 cubic meter.
        """
        self.resolution: float = resolution
        """:field
        The fluid density in kg/m3.
        """
        self.rest_density: float = rest_density

    def to_dict(self) -> dict:
        """
        :return: A JSON dictionary of this object.
        """

        d = {"$type": "granular_fluid"}
        d.update({k: v for k, v in self.__dict__.items()})
        return d


def __get() -> Dict[str, GranularFluid]:
    data = loads(Path(resource_filename(__name__, "data/granular_fluids.json")).read_text())
    materials = dict()
    for k in data:
        materials[k] = GranularFluid(**data[k])
    return materials


GRANULAR_FLUIDS: Dict[str, GranularFluid] = __get()
