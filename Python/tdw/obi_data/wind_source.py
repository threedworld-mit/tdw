from copy import copy
from random import randint, uniform
from typing import Tuple, List
from tdw.tdw_utils import TDWUtils
from tdw.obi_data.fluids.fluid import Fluid
from tdw.obi_data.fluids.disk_emitter import DiskEmitter


class _LerpableRange:
    def __init__(self, value: float, speed: float):
        self.lerp_range: Tuple[float, float] = (value, value * 2)
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


class _LerpableFloat:
    def __init__(self, a: float, b: float, speed: float):
        self._v: float = a
        self._target: float = b
        self._speed: float = abs(speed)
        self._increase: bool = b > a

    def update(self) -> float:
        if self._v < self._target and self._increase:
            self._v += self._speed
        elif self._v > self._target and not self._increase:
            self._v -= self._speed
        return self._v

    def set_target(self, target: float, speed: float) -> None:
        self._target = target
        self._speed = abs(speed)
        self._increase = self._v < self._target



class WindSource:
    """
    A source of wind: An invisible Obi fluid that can dynamically adjust its rotation, speed, etc.
    """

    def __init__(self, wind_id: int, capacity: int = 2000, speed: float = 1, lifespan: float = 0.5, smoothing: float = 0.5,
                 resolution: float = 1, radius_scale: float = 20, vorticity: float = 10, random_velocity: float = 0.125,
                 visible: bool = False, emitter_radius: float = 0.25):
        """
        :param wind_id: The ID of this wind source.
        """

        self.wind_id: int = wind_id
        self.fluid: Fluid = Fluid(capacity=capacity,
                                  smoothing=smoothing,
                                  resolution=resolution,
                                  color={"r": 0, "g": 0, "b": 1, "a": 1},
                                  transparency=1 if visible else 0,
                                  thickness_cutoff=1 if visible else 100,
                                  viscosity=0,
                                  rest_density=1.293,
                                  atmospheric_drag=0,
                                  atmospheric_pressure=0,
                                  particle_z_write=False,
                                  thickness_downsample=2,
                                  radius_scale=radius_scale,
                                  surface_tension=0,
                                  vorticity=vorticity,
                                  random_velocity=random_velocity,
                                  buoyancy=0,
                                  diffusion=0,
                                  diffusion_data=None,
                                  blur_radius=0.02,
                                  surface_downsample=1,
                                  render_smoothness=0.8,
                                  metalness=0,
                                  absorption=0,
                                  ambient_multiplier=0,
                                  reflection=0,
                                  refraction=0,
                                  foam_downsample=1)
        self.emitter: DiskEmitter = DiskEmitter(radius=emitter_radius)
        self._capacity: _LerpableRange = _LerpableRange(value=capacity, speed=0)
        self._lifespan: _LerpableRange = _LerpableRange(value=lifespan, speed=0)
        self._speed: _LerpableFloat = _LerpableFloat(a=speed, b=speed, speed=0)

    def set_gustiness(self, capacity: Tuple[int, int], capacity_dt: float,
                      lifespan: Tuple[float, float], lifespan_dt: float) -> None:
        self._capacity.lerp_range = copy(capacity)
        self._capacity.speed = capacity_dt
        self._lifespan.lerp_range = copy(lifespan)
        self._lifespan.speed = lifespan_dt

    def set_speed(self, target: float, speed_dt: float):


    def update(self) -> List[dict]:
        return [{"$type": "set_obi_fluid_capacity",
                 "id": self.wind_id,
                 "capacity": int(self._capacity.update())},
                {"$type": "set_obi_fluid_lifespan",
                 "id": self.wind_id,
                 "lifespan": self._lifespan.update()}]
