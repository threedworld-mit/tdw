from abc import ABC, abstractmethod
from copy import copy
from typing import Dict, List, Generic, TypeVar
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.obi_data.fluids.fluid import Fluid
from tdw.obi_data.fluids.disk_emitter import DiskEmitter
from tdw.type_aliases import POSITION, ROTATION


T = TypeVar("T")


class _Lerpable(Generic[T], ABC):
    def __init__(self, value: T, dt: T = 0):
        self.v: T = self._copy(value)
        self._a: T = self._copy(value)
        self._b: T = self._copy(value)
        self._dt: float = self._get_dt(dt=dt)
        self.is_at_target: bool = True
        self._t: float = 0
        self._increase: bool = True

    def update(self) -> None:
        # Increment the t value.
        if self._increase:
            self._t += self._dt
            if self._t >= 1:
                self._t = 1
                self.is_at_target = True
        else:
            self._t -= self._dt
            if self._t <= 0:
                self._t = 0
                self.is_at_target = True
        # Lerp.
        self.v = self._lerp()

    def set_target(self, target: T, dt: float) -> None:
        self._a = self.v
        self._b = target
        if self._a < self._b:
            self._increase = True
            self._t = 0
        else:
            self._increase = False
            self._t = 1
        self._dt = self._get_dt(dt=dt)
        self.is_at_target = False

    def _get_dt(self, dt: float) -> float:
        return abs(dt) / np.linalg.norm(self._b - self._a)

    @abstractmethod
    def _lerp(self) -> T:
        raise Exception()

    @abstractmethod
    def _copy(self, v: T) -> T:
        raise Exception()


class _LerpableFloat(_Lerpable[float]):
    def _lerp(self) -> float:
        return TDWUtils.lerp(self._a, self._b, self._t)

    def _copy(self, v: float) -> float:
        return copy(v)


class _LerpableVector(_Lerpable[np.ndarray]):
    def _lerp(self) -> np.ndarray:
        return TDWUtils.lerp_array(self._a, self._b, self._t)

    def _copy(self, v: np.ndarray) -> np.ndarray:
        return np.copy(v)


class _LerpableQuaternion(_Lerpable[np.ndarray]):
    def _lerp(self) -> np.ndarray:
        return TDWUtils.slerp(self._a, self._b, self._t)

    def _copy(self, v: np.ndarray) -> np.ndarray:
        return np.copy(v)


class WindSource:
    """
    A source of wind: An invisible Obi fluid that can dynamically adjust its rotation, speed, etc.
    """

    def __init__(self, wind_id: int, position: POSITION, rotation: ROTATION, capacity: int = 2000, speed: float = 1,
                 lifespan: float = 0.5, smoothing: float = 0.5, resolution: float = 1, vorticity: float = 0.5,
                 random_velocity: float = 0.125, minimum_pool_size: float = 0.5, visible: bool = False,
                 emitter_radius: float = 0.25, solver_id: int = 0):
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
                                  radius_scale=1,
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
        self._capacity: _LerpableFloat = _LerpableFloat(value=capacity)
        self._lifespan: _LerpableFloat = _LerpableFloat(value=lifespan)
        self._speed: _LerpableFloat = _LerpableFloat(value=speed)
        self._smoothing: _LerpableFloat = _LerpableFloat(value=smoothing)
        self._resolution: _LerpableFloat = _LerpableFloat(value=resolution)
        self._vorticity: _LerpableFloat = _LerpableFloat(value=vorticity)
        self._random_velocity: _LerpableFloat = _LerpableFloat(value=random_velocity)
        if isinstance(position, np.ndarray):
            self._position_dict: Dict[str, float] = TDWUtils.array_to_vector3(position)
            self._position: _LerpableVector = _LerpableVector(value=position)
        elif isinstance(position, dict):
            self._position_dict = position
            self._position = _LerpableVector(value=TDWUtils.vector3_to_array(position))
        else:
            raise Exception(f"Invalid position: {position}")
        if isinstance(rotation, np.ndarray):
            self._rotation_dict: Dict[str, float] = TDWUtils.array_to_vector3(rotation)
            self._rotation: _LerpableQuaternion = _LerpableQuaternion(value=rotation)
        elif isinstance(rotation, dict):
            self._rotation_dict = rotation
            self._rotation = _LerpableQuaternion(value=TDWUtils.vector3_to_array(rotation))
        else:
            raise Exception(f"Invalid rotation: {rotation}")
        self._minimum_pool_size: float = minimum_pool_size
        self._solver_id: int = solver_id
        self._created: bool = False

    def set_gustiness(self, capacity: int, dc: float, lifespan: float, dl: float) -> None:
        self._capacity.set_target(target=capacity, dt=dc)
        self._lifespan.set_target(target=lifespan, dt=dl)

    def set_speed(self, speed: float, ds: float) -> None:
        self._speed.set_target(target=speed, dt=ds)

    def set_spread(self, smoothing: float, ds: float, resolution: float, dr: float) -> None:
        self._smoothing.set_target(target=smoothing, dt=ds)
        self._resolution.set_target(target=resolution, dt=dr)

    def set_turbulence(self, vorticity: float, dv: float, random_velocity: float, drv: float) -> None:
        self._vorticity.set_target(target=vorticity, dt=dv)
        self._random_velocity.set_target(target=random_velocity, dt=drv)

    def update(self) -> List[dict]:
        # Update an existing fluid.
        if self._created:
            commands = []
            if not self._capacity.is_at_target:
                self._capacity.update()
                commands.append({"$type": "set_obi_fluid_capacity",
                                 "id": self.wind_id,
                                 "capacity": int(self._capacity.v)})
            if not self._lifespan.is_at_target:
                self._lifespan.update()
                commands.append({"$type": "set_obi_fluid_lifespan",
                                 "id": self.wind_id,
                                 "lifespan": self._lifespan.v})
            if not self._speed.is_at_target:
                self._speed.update()
                commands.append({"$type": "set_obi_fluid_emission_speed",
                                 "id": self.wind_id,
                                 "speed": self._speed.v})
            if not self._smoothing.is_at_target:
                self._smoothing.update()
                commands.append({"$type": "set_obi_fluid_smoothing",
                                 "id": self.wind_id,
                                 "smoothing": self._smoothing.v})
            if not self._resolution.is_at_target:
                self._resolution.update()
                commands.append({"$type": "set_obi_fluid_resolution",
                                 "id": self.wind_id,
                                 "resolution": self._resolution.v})
            if not self._vorticity.is_at_target:
                self._vorticity.update()
                commands.append({"$type": "set_obi_fluid_vorticity",
                                 "id": self.wind_id,
                                 "vorticity": self._vorticity.v})
            if not self._random_velocity.is_at_target:
                self._random_velocity.update()
                commands.append({"$type": "set_obi_fluid_random_velocity",
                                 "id": self.wind_id,
                                 "random_velocity": self._random_velocity.v})
            return commands
        # Create a new fluid.
        else:
            self._created = True
            return [{"$type": "create_obi_fluid",
                     "id": self.wind_id,
                     "fluid": self.fluid.to_dict(),
                     "shape": self.emitter.to_dict(),
                     "position": self._position_dict,
                     "rotation": self._rotation_dict,
                     "lifespan": self._lifespan.v,
                     "minimum_pool_size": self._minimum_pool_size,
                     "solver_id": self._solver_id,
                     "speed": self._speed.v}]
