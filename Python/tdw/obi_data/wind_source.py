from copy import copy
from random import randint, uniform
from typing import Tuple, List
from tdw.tdw_utils import TDWUtils
from tdw.obi_data.fluids.fluid import Fluid
from tdw.obi_data.fluids.emitter_shape import EmitterShape


class _LerpableRange:
    def __init__(self, lerp_range: Tuple[float, float], speed: float):
        self.lerp_range: Tuple[float, float] = lerp_range
        self.speed: float = abs(speed)
        self._target: float = 0
        self._v: float = 0
        self._set_target()

    def update(self) -> float:
        if self._v < self._target:
            self._v += self.speed
            if self._v >= self._target:
                self._set_target()
        else:
            self._v -= self.speed
            if self._v <= self._target:
                self._set_target()
        return self._v

    def _set_target(self) -> None:
        self._target = TDWUtils.lerp(self.lerp_range[0], self.lerp_range[1], uniform(0, 1))


class WindSource:
    """
    A source of wind: An invisible Obi fluid that can dynamically adjust its rotation, speed, etc.
    """

    INITIAL_CAPACITY: int = 1000

    def __init__(self, wind_id: int, fluid: Fluid):
        """
        :param wind_id: The ID of this wind source.
        :param fluid: The wind's fluid data.
        """

        self.wind_id: int = wind_id
        self.fluid: Fluid = fluid
        self._capacity: _LerpableRange = _LerpableRange(lerp_range=(WindSource.INITIAL_CAPACITY,
                                                                    WindSource.INITIAL_CAPACITY * 2),
                                                        speed=0)

    def set_gustiness(self, capacity_range: Tuple[int, int], speed: float) -> None:
        self._capacity.lerp_range = capacity_range
        self._capacity.speed = speed

    def update(self) -> List[dict]:
        commands = []
        # Set the capacity.
        commands.append({"$type": "set_obi_fluid_capacity",
                         "id": self.wind_id,
                         "capacity": int(self._capacity.update())})
        return commands
