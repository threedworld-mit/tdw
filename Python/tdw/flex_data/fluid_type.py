import pkg_resources
import json
from typing import Dict


class FluidType:
    """
    Metadata for a single fluid type. Specifies values for Flex fluid containers.
    """

    def __init__(self, fluid_type: str, viscosity: float, adhesion: float, cohesion: float):
        """
        :param fluid_type: The name of the fluid type.
        :param viscosity: The viscosity value of the fluid.
        :param adhesion: The adhesion value of the fluid.
        :param cohesion: The cohesion value of the fluid.
        """

        """:field
        The name of the fluid type.
        """
        self.fluid_type: str = fluid_type
        """:field
        The viscosity value of the fluid.
        """
        self.viscosity: float = viscosity
        """:field
        The adhesion value of the fluid.
        """
        self.adhesion: float = adhesion
        """:field
        The cohesion value of the fluid.
        """
        self.cohesion: float = cohesion


def __load() -> Dict[str, FluidType]:
    """
    :return: The default fluid type data.
    """

    fluid_types: Dict[str, FluidType] = {}
    with open(pkg_resources.resource_filename(__name__, "fluid_types.json"), "rt") as f:
        fluid_type_data = json.load(f)
        for ft in fluid_type_data:
            fluid_types[ft] = FluidType(fluid_type=ft,
                                        viscosity=fluid_type_data[ft]["viscosity"],
                                        adhesion=fluid_type_data[ft]["adhesion"],
                                        cohesion=fluid_type_data[ft]["cohesion"])
    return fluid_types

# The default fluid types. Key = The name of the fluid.
FLUID_TYPES: Dict[str, FluidType] = __load()
