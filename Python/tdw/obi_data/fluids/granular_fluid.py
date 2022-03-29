from pkg_resources import resource_filename
from pathlib import Path
from json import loads
from typing import Dict
from tdw.obi_data.fluids.fluid_base import FluidBase


class GranularFluid(FluidBase):
    """
    Data for an Obi granular fluid. For more information, [read this](http://obi.virtualmethodstudio.com/tutorials/emittermaterials.html).
    """

    def __init__(self, randomness: float, capacity: int, resolution: float, color: Dict[str, float],
                 rest_density: float, radius_scale: float = 1.7, random_velocity: float = 0):
        """
        :param randomness: The variation in particle size.
        :param capacity: The maximum amount of emitted particles.
        :param resolution: The size and amount of particles in 1 cubic meter.
        :param color: The visual color of the fluid.
        :param rest_density: The fluid density in kg/m3.
        :param radius_scale: This scales the size at which particles are drawn.
        :param random_velocity: Random velocity of emitted particles.
        """

        super().__init__(capacity=capacity, resolution=resolution, color=color, rest_density=rest_density,
                         radius_scale=radius_scale, random_velocity=random_velocity)
        """:field
        The variation in particle size.
        """
        self.randomness: float = randomness

    def _get_type(self) -> str:
        return "granular_fluid"


def __get() -> Dict[str, GranularFluid]:
    data = loads(Path(resource_filename(__name__, "data/granular_fluids.json")).read_text())
    materials = dict()
    for k in data:
        materials[k] = GranularFluid(**data[k])
    return materials


GRANULAR_FLUIDS: Dict[str, GranularFluid] = __get()
