from typing import Dict, List, Tuple
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.obi_data.fluids.fluid import Fluid
from tdw.obi_data.fluids.disk_emitter import DiskEmitter
from tdw.type_aliases import POSITION, ROTATION
from tdw.lerp.lerpable_float import LerpableFloat
from tdw.lerp.lerpable_vector import LerpableVector


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
        :param rotation: The rotation of the wind in Euler angles.
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
        # The wind's fluid.
        self._fluid: Fluid = Fluid(capacity=capacity,
                                   smoothing=smoothing,
                                   resolution=resolution,
                                   vorticity=vorticity,
                                   random_velocity=random_velocity,
                                   color={"r": 0, "g": 0, "b": 1, "a": 1},
                                   transparency=0 if visible else 1,
                                   thickness_cutoff=1 if visible else 100,
                                   absorption=0,
                                   ambient_multiplier=1,
                                   atmospheric_drag=0,
                                   atmospheric_pressure=0,
                                   blur_radius=0.02,
                                   buoyancy=0,
                                   diffusion=0,
                                   diffusion_data=None,
                                   foam_downsample=1,
                                   metalness=0,
                                   particle_z_write=False,
                                   radius_scale=4 if visible else 1,
                                   reflection=0.25 if visible else 0,
                                   refraction=-0.034 if visible else 0,
                                   refraction_downsample=1,
                                   render_smoothness=0.8 if visible else 0,
                                   rest_density=1.293,
                                   surface_downsample=1,
                                   surface_tension=0,
                                   thickness_downsample=2,
                                   viscosity=0)
        # The fluid's disk emitter.
        self._emitter: DiskEmitter = DiskEmitter(radius=emitter_radius)
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
            self._rotation_eulers: Dict[str, float] = TDWUtils.array_to_vector3(rotation)
        elif isinstance(rotation, dict):
            self._rotation_eulers = rotation
        else:
            raise Exception(f"Invalid rotation: {rotation}")
        self._rotation: LerpableFloat = LerpableFloat(value=0)
        self._rotation_axis: str = "yaw"
        self._minimum_pool_size: float = minimum_pool_size
        self._solver_id: int = solver_id
        self._created: bool = False

    def set_speed(self, speed: float, ds: float) -> None:
        """
        Set a target wind speed.

        :param speed: The target speed in meters per second.
        :param ds: The current speed will increase/decrease by this delta per `communicate()` call until it is at the target.
        """

        self._speed.set_target(target=speed, dt=ds)

    def get_speed(self) -> float:
        """
        :return: The current wind speed.
        """

        return self._speed.value

    def is_accelerating(self) -> bool:
        """
        :return: True if the speed is accelerating or decelerating.
        """

        return not self._speed.is_at_target

    def set_gustiness(self, capacity: int, dc: int, lifespan: float, dl: float) -> None:
        """
        Set the "gustiness" of the wind i.e. the duration of pauses between emitted particles.

        This tends to "override" the wind speed, which merely controls the velocity of particles in the scene.

        The resulting gusts will always be periodic. If you want gusts to be more random, call this function with different values every *n* `communicate()` calls.

        :param capacity: The target maximum number of particles. A higher particle count will create a steadier stream of particles but can significantly impact simulation performance.
        :param dc: The current capacity will increase/decrease by this delta per `communicate()` call until it is at the target.
        :param lifespan: The particle lifespan in seconds. A higher lifespan will result in "gustier" wind because particles will linger in the scene and prevent new particles from being created.
        :param dl: The current lifespan will increase/decrease by this delta per `communicate()` call until it is at the target.
        """

        self._capacity.set_target(target=capacity, dt=dc)
        self._lifespan.set_target(target=lifespan, dt=dl)

    def is_gusting(self) -> Tuple[bool, bool]:
        """
        :return: Tuple: True if we're at the target capacity, True if we're at the target lifespan.
        """

        return not self._capacity.is_at_target, not self._lifespan.is_at_target

    def set_spread(self, smoothing: float, ds: float, resolution: float, dr: float) -> None:
        """
        Set how far the wind fluid can spread.

        :param smoothing: A percentage of the particle radius used to define the radius of the zone around each particle when calculating fluid density. A lower value will create a more scattered fluid.
        :param ds: The current smoothing will increase/decrease by this delta per `communicate()` call until it is at the target.
        :param resolution: The size and amount of particles in 1 cubic meter. A value of 1 will use 1000 particles per cubic meter. For larger wind sources, consider lowering this value.
        :param dr: The current resolution will increase/decrease by this delta per `communicate()` call until it is at the target.
        """

        self._smoothing.set_target(target=smoothing, dt=ds)
        self._resolution.set_target(target=resolution, dt=dr)

    def is_spreading(self) -> Tuple[bool, bool]:
        """
        :return: Tuple: True if the smoothing value is at the target, True if the resolution value is at the target.
        """

        return not self._smoothing.is_at_target, not self._resolution.is_at_target

    def set_turbulence(self, vorticity: float, dv: float, random_velocity: float, dr: float) -> None:
        """
        Set the wind turbulence.

        :param vorticity: Amount of vorticity confinement, it will contribute to maintain vortical details in the fluid. This value should always be between approximately 0 and 0.5. This will increase turbulence, although the difference is relatively minor.
        :param dv: The current vorticity will increase/decrease by this delta per `communicate()` call until it is at the target.
        :param random_velocity: The maximum random speed in meters per second that can be applied to a particle. This will increase turbulence.
        :param dr: The current random velocity will increase/decrease by this delta per `communicate()` call until it is at the target.
        """

        self._vorticity.set_target(target=vorticity, dt=dv)
        self._random_velocity.set_target(target=random_velocity, dt=dr)

    def is_turbulating(self) -> Tuple[bool, bool]:
        """
        :return: Tuple: True if the vorticity value is at the target, True if the random velocity value is at the target.
        """

        return not self._vorticity.is_at_target, not self._random_velocity.is_at_target

    def move_to(self, position: POSITION, dp: float) -> None:
        """
        Start moving to the target position.

        :param position: The new position.
        :param dp: Move this many meters per `communicate()` call.
        """

        if isinstance(position, np.ndarray):
            pos = position
        elif isinstance(position, dict):
            pos = TDWUtils.vector3_to_array(position)
        else:
            raise Exception(f"Invalid position: {position}")
        self._position.set_target(target=pos, dt=dp)

    def get_position(self) -> np.ndarray:
        """
        :return: The position of the wind source.
        """

        return self._position.value

    def is_moving(self) -> bool:
        """
        :return: True if the wind source is moving.
        """

        return not self._position.is_at_target

    def rotate_by(self, angle: float, da: float, axis: str = "yaw") -> None:
        """
        Rotate the wind fluid emitter with an angle and an axis.

        :param angle: The target angle in degrees.
        :param da: Increment `angle` by this many degrees per `communicate()` call.
        :param axis: The axis of rotation: `"pitch"`, `"yaw"`, or `"roll"`.
        """

        self._rotation_axis = axis
        self._rotation.set_target(target=angle, dt=da)

    def get_rotation(self) -> Tuple[float, str]:
        """
        :return: Tuple: The angle of rotation in degrees, the axis of rotation.
        """

        return self._rotation.value, self._rotation_axis

    def is_rotating(self) -> bool:
        """
        :return: True if the wind source is rotating.
        """

        return not self._rotation.is_at_target

    def update(self) -> List[dict]:
        """
        Don't call this in your controller. This is called internally by the `Obi` add-on.

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
                                 "capacity": int(self._capacity.value)})
            if not self._lifespan.is_at_target:
                self._lifespan.update()
                commands.append({"$type": "set_obi_fluid_lifespan",
                                 "id": self.wind_id,
                                 "lifespan": self._lifespan.value})
            if not self._speed.is_at_target:
                self._speed.update()
                commands.append({"$type": "set_obi_fluid_emission_speed",
                                 "id": self.wind_id,
                                 "speed": self._speed.value})
            if not self._smoothing.is_at_target:
                self._smoothing.update()
                commands.append({"$type": "set_obi_fluid_smoothing",
                                 "id": self.wind_id,
                                 "smoothing": self._smoothing.value})
            if not self._resolution.is_at_target:
                self._resolution.update()
                commands.append({"$type": "set_obi_fluid_resolution",
                                 "id": self.wind_id,
                                 "resolution": self._resolution.value})
            if not self._vorticity.is_at_target:
                self._vorticity.update()
                commands.append({"$type": "set_obi_fluid_vorticity",
                                 "id": self.wind_id,
                                 "vorticity": self._vorticity.value})
            if not self._random_velocity.is_at_target:
                self._random_velocity.update()
                commands.append({"$type": "set_obi_fluid_random_velocity",
                                 "id": self.wind_id,
                                 "random_velocity": self._random_velocity.value})
            if not self._position.is_at_target:
                self._position.update()
                commands.append({"$type": "teleport_obi_actor",
                                 "id": self.wind_id,
                                 "position": TDWUtils.array_to_vector3(self._position.value)})
            if not self._rotation.is_at_target:
                self._rotation.update()
                commands.extend([{"$type": "rotate_obi_actor_by",
                                  "id": self.wind_id,
                                  "angle": self._rotation.get_dt(),
                                  "axis": self._rotation_axis}])
            return commands
        # Create a new fluid.
        else:
            self._created = True
            return [{"$type": "create_obi_fluid",
                     "id": self.wind_id,
                     "fluid": self._fluid.to_dict(),
                     "shape": self._emitter.to_dict(),
                     "position": self._position_dict,
                     "rotation": self._rotation_eulers,
                     "lifespan": self._lifespan.value,
                     "minimum_pool_size": self._minimum_pool_size,
                     "solver_id": self._solver_id,
                     "speed": self._speed.value}]
