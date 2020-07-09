import pkg_resources
import json
from typing import Dict
from pathlib import Path


class FluidType:
    """
    Metadata for a single fluid type. Specifies values for Flex fluid containers.
    """

    def __init__(self, fluid_type: str, viscosity: float, adhesion: float, cohesion: float):
        """
        :param fluid_type: Name of the fluid type.
        :param viscosity: The viscosity value of the fluid.
        :param adhesion: The adhesion value of the fluid.
        :param cohesion: The cohesion value of the fluid.
        """

        self.fluid_type = fluid_type
        self.viscosity = viscosity
        self.adhesion = adhesion
        self.cohesion = cohesion


class FluidTypes:
    """
    Manage data for available fluid types, as defined in JSON data file.

    Usage:

    ```python
    from tdw.flex.fluid_types import FluidTypes

    ft = FluidTypes()

    print(ft.fluid_type_names) # ["water", "ink", ... ]

    water = ft.fluid_types["water"]
    print(water.fluid_type) # "water"
    ```
    """

    def __init__(self):
        self.fluid_type_names = []
        self.fluid_types: Dict[str, FluidType] = {}

        fluid_type_data = {}

        json_path = pkg_resources.resource_filename(__name__, "fluid_types.json")
        if Path(json_path).exists():
            with open(json_path, "rt") as f:
                fluid_type_data = json.load(f)

        for ft in fluid_type_data:
            combo = FluidType(fluid_type=ft,
                              viscosity=fluid_type_data[ft]["viscosity"],
                              adhesion=fluid_type_data[ft]["adhesion"],
                              cohesion=fluid_type_data[ft]["cohesion"])
            self.fluid_types[ft] = combo

        # Create the list of fluid type names (e.g. for randomly-selecting types per trial).
        self.fluid_type_names = list(self.fluid_types.keys())
