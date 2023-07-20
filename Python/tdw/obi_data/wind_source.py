from typing import Dict, List
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.obi_data.fluids.fluid import Fluid
from tdw.obi_data.fluids.disk_emitter import DiskEmitter
from tdw.type_aliases import POSITION, ROTATION
from tdw.lerp.lerpable_float import LerpableFloat
from tdw.lerp.lerpable_vector import LerpableVector
from tdw.lerp.lerpable_quaternion import LerpableQuaternion


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
        :param position: The position of the wind source.
        :param rotation: The rotation of the wind source as a quaternion.
        :param capacity: The maximum amount of emitted particles.
        :param speed: The emission speed in meters per second.
        :param lifespan: The particle lifespan in seconds. A higher lifespan will result in "gustier" wind because particles will linger in the scene and prevent new particles from being created.
        :param smoothing: A percentage of the particle radius used to define the radius of the zone around each particle when calculating fluid density. A lower value will create a more scattered fluid.
        :param resolution: The size and amount of particles in 1 cubic meter. A value of 1 will use 1000 particles per cubic meter. For larger wind sources, consider lowering this value.
        :param vorticity: Amount of vorticity confinement, it will contribute to maintain vortical details in the fluid. This value should always be between approximately 0 and 0.5. This will increase turbulence, although the difference is relatively minor.
        :param random_velocity: The maximum random speed in meters per second that can be applied to a particle. This will increase turbulence.
        :param minimum_pool_size: The minimum amount of inactive particles available before the emitter is allowed to resume emission.
        :param visible: If True, make the fluid visible. This is useful for debugging.
        :param emitter_radius: The radius of the wind source.
        :param solver_id: The ID of the Obi solver.
        """

        """:field
        The ID of this wind source.
        """
        self.wind_id: int = wind_id
        """:field
        The wind's [`Fluid`](fluids/fluid.md).
        """
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
                                  radius_scale=10,
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
        """:field
        The fluid's [`DiskEmitter`](fluids/disk_emitter.md).
        """
        self.emitter: DiskEmitter = DiskEmitter(radius=emitter_radius)
        self._capacity: LerpableFloat = LerpableFloat(value=capacity)
        self._lifespan: LerpableFloat = LerpableFloat(value=lifespan)
        self._speed: LerpableFloat = LerpableFloat(value=speed)
        self._smoothing: LerpableFloat = LerpableFloat(value=smoothing)
        self._resolution: LerpableFloat = LerpableFloat(value=resolution)
        self._vorticity: LerpableFloat = LerpableFloat(value=vorticity)
        self._random_velocity: LerpableFloat = LerpableFloat(value=random_velocity)
        if isinstance(position, np.ndarray):
            self._position_dict: Dict[str, float] = TDWUtils.array_to_vector3(position)
            self._position: LerpableVector = LerpableVector(value=position)
        elif isinstance(position, dict):
            self._position_dict = position
            self._position = LerpableVector(value=TDWUtils.vector3_to_array(position))
        else:
            raise Exception(f"Invalid position: {position}")
        if isinstance(rotation, np.ndarray):
            self._rotation_dict: Dict[str, float] = TDWUtils.array_to_vector3(rotation)
            self._rotation: LerpableQuaternion = LerpableQuaternion(value=rotation)
        elif isinstance(rotation, dict):
            self._rotation_dict = rotation
            self._rotation = LerpableQuaternion(value=TDWUtils.vector3_to_array(rotation))
        else:
            raise Exception(f"Invalid rotation: {rotation}")
        self._minimum_pool_size: float = minimum_pool_size
        self._solver_id: int = solver_id
        self._created: bool = False

    def set_gustiness(self, capacity: int, dc: int, lifespan: float, dl: float) -> None:
        """
        Set the "gustiness" of the wind.

        If the gustiness is high, then there will be pauses between emitted particles. The pauses *won't* vary in duration, nor will the parameters of each "gust"; if  you want to vary the gusts, you can repeatedly call this function.

        If the gustiness is low, there will be a steady stream of emitted particles.

        The two values controlling gustiness are `capacity` and `lifespan` and are not immediately set: The current values will be lerped (linearly interpolated) to the new values.

        :param capacity: The maximum number of particles. A higher particle count will create a steadier stream of particles but can significantly impact simulation performance.
        :param dc: The capacity lerp rate per `communicate()` call. i.e. if this is set to 10, then current capacity will be incremented by 10 per `communicate()` call.
        :param lifespan: The particle lifespan in seconds. A higher lifespan will result in "gustier" wind because particles will linger in the scene and prevent new particles from being created.
        :param dl: The lifespan lerp rate per `communicate()` call. i.e. if this is set to 0.1, then current lifespan will be incremented by 0.1 per `communicate()` call.
        """

        self._capacity.set_target(target=capacity, dt=dc)
        self._lifespan.set_target(target=lifespan, dt=dl)

    def set_speed(self, speed: float, ds: float) -> None:
        """
        Set a new wind speed.

        The current speed will be linearly interpolated (lerped) to the new speed per `communicate()` call.

        :param speed: The speed in meters per second.
        :param ds: The speed lerp rate per `communicate()` call. i.e. if this is set to 0.1, then current speed will be incremented by 0.1 per `communicate()` call.
        """

        self._speed.set_target(target=speed, dt=ds)

    def set_spread(self, smoothing: float, ds: float, resolution: float, dr: float) -> None:
        """
        Set how far the wind fluid can spread.

        The two values controlling wind spread are `smoothing` and `resolution` and are not immediately set: The current values will be lerped (linearly interpolated) to the new values.

        :param smoothing: A percentage of the particle radius used to define the radius of the zone around each particle when calculating fluid density. A lower value will create a more scattered fluid.
        :param ds: The smoothing lerp rate per `communicate()` call. i.e. if this is set to 0.01, then current smoothing value will be incremented by 0.01 per `communicate()` call.
        :param resolution: The size and amount of particles in 1 cubic meter. A value of 1 will use 1000 particles per cubic meter. For larger wind sources, consider lowering this value.
        :param dr: The resolution lerp rate per `communicate()` call. i.e. if this is set to 0.01, then current resolution value will be incremented by 0.01 per `communicate()` call.
        """

        self._smoothing.set_target(target=smoothing, dt=ds)
        self._resolution.set_target(target=resolution, dt=dr)

    def set_turbulence(self, vorticity: float, dv: float, random_velocity: float, dr: float) -> None:
        """
        Set the wind turbulence.

        The two values controlling turbulence are `vorticity` and `random_velocity` and are not immediately set: The current values will be lerped (linearly interpolated) to the new values.

        :param vorticity: Amount of vorticity confinement, it will contribute to maintain vortical details in the fluid. This value should always be between approximately 0 and 0.5. This will increase turbulence, although the difference is relatively minor.
        :param dv: The vorticity lerp rate per `communicate()` call. i.e. if this is set to 0.01, then current vorticity value will be incremented by 0.01 per `communicate()` call.
        :param random_velocity: The maximum random speed in meters per second that can be applied to a particle. This will increase turbulence.
        :param dr: The random_velocity lerp rate per `communicate()` call. i.e. if this is set to 0.01, then current random_velocity value will be incremented by 0.01 per `communicate()` call.
        """

        self._vorticity.set_target(target=vorticity, dt=dv)
        self._random_velocity.set_target(target=random_velocity, dt=dr)

    def set_position(self, position: POSITION, dp: float) -> None:
        """
        Set the position of the wind fluid emitter.

        The current position will be linearly interpolated (lerped) to the new position per `communicate()` call.

        :param position: The new position.
        :param dp: The lerp rate in meters per `communicate()` call.
        """

        if isinstance(position, np.ndarray):
            pos = position
        elif isinstance(position, dict):
            pos = TDWUtils.vector3_to_array(position)
        else:
            raise Exception(f"Invalid position: {position}")
        self._position.set_target(target=pos, dt=dp)

    def set_rotation(self, rotation: ROTATION, dr: float) -> None:
        """
        Set the rotation of the wind fluid emitter.

        The current rotation will be linearly interpolated (lerped) to the new rotation per `communicate()` call.

        :param rotation: The new position.
        :param dr: The lerp rate in radians per `communicate()` call.
        """

        if isinstance(rotation, np.ndarray):
            rot = rotation
        elif isinstance(rotation, dict):
            rot = TDWUtils.vector4_to_array(rotation)
        else:
            raise Exception(f"Invalid rotation: {rotation}")
        self._rotation.set_target(target=rot, dt=dr)

    def update(self) -> List[dict]:
        """
        Update the wind. Create the fluid actor if it doesn't exist. Lerp all values that need lerping.

        :return: A list of commands.
        """

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
            if not self._position.is_at_target:
                self._position.update()
                commands.append({"$type": "set_obi_fluid_emitter_position",
                                 "id": self.wind_id,
                                 "position": TDWUtils.array_to_vector3(self._position.v)})
            if not self._rotation.is_at_target:
                self._rotation.update()
                commands.append({"$type": "set_obi_fluid_emitter_rotation",
                                 "id": self.wind_id,
                                 "position": TDWUtils.array_to_vector4(self._rotation.v)})
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
