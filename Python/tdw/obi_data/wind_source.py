from random import randint, uniform
from typing import Tuple, List
from tdw.tdw_utils import TDWUtils
from tdw.obi_data.fluids.fluid import Fluid
from tdw.obi_data.fluids.emitter_shape import EmitterShape


class WindSource:
    """
    A source of wind: An invisible Obi fluid that can dynamically adjust its rotation, speed, etc.
    """

    def __init__(self, wind_id: int, fluid: Fluid):
        """
        :param wind_id: The ID of this wind source.
        :param fluid: The wind's fluid data.
        """

        self.wind_id: int = wind_id
        self.fluid: Fluid = fluid
        self.capacities: Tuple[int, int] = (1000, 2000)
        self._capacity_range: Tuple[int, int] = self._get_capacity_range()
        self._capacity_t: float = 0
        self._capacity_dt: float = 0

    def set_gustiness(self, ):

    def update(self) -> List[dict]:
        commands = []
        # Increment the capacity time.
        self._capacity_t += self._capacity_dt
        # Reverse the lerp.
        if self._capacity_t >= 1 and self._capacity_dt > 0:
            self._capacity_t = 1
            self._capacity_dt *= -1
        elif self._capacity_t <= 0 and self._capacity_dt < 0:
            self._capacity_t = 0
            self._capacity_dt *= -1
        # Get the lerped capacity.
        capacity: int = int(TDWUtils.lerp(self._capacity_range[0], self._capacity_range[1], self._capacity_t))
        commands.append({"$type": "set_obi_fluid_capacity",
                         "id": self.wind_id,
                         "capacity": capacity})
        return commands

    def _get_capacity_range(self) -> Tuple[int, int]:
        c0: float = uniform(0, 0.3)
        c1: float = uniform(c0, 1)
        a = int(TDWUtils.lerp(self.capacities[0], self.capacities[1], c0))
        b = int(TDWUtils.lerp(self.capacities[0], self.capacities[1], c1))
        return a, b