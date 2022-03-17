from typing import List, Dict, Union, Optional
from tdw.add_ons.add_on import AddOn
from tdw.output_data import OutputData, ImageSensors, StaticRigidbodies, StaticCompositeObjects, StaticRobot
from tdw.obi_data.collision_material import CollisionMaterial, COLLISION_MATERIALS, DEFAULT_MATERIAL
from tdw.obi_data.fluid import Fluid, FLUIDS
from tdw.obi_data.granular_fluid import GranularFluid, GRANULAR_FLUIDS
from tdw.obi_data.sampling_method import SamplingMethod
from tdw.object_data.composite_object.composite_object_static import CompositeObjectStatic


class Obi(AddOn):
    def __init__(self, floor_collision_material: CollisionMaterial = None,
                 collision_material_overrides: Dict[int, Union[str, CollisionMaterial]] = None):
        super().__init__()
        self._initialized_obi: bool = False
        if floor_collision_material is None:
            self._floor_collision_material: CollisionMaterial = DEFAULT_MATERIAL
        else:
            self._floor_collision_material = floor_collision_material
        if collision_material_overrides is None:
            self._collision_material_overrides: Dict[int, CollisionMaterial] = dict()
        else:
            self._collision_material_overrides = collision_material_overrides

    def get_initialization_commands(self) -> List[dict]:
        return [{"$type": "create_obi_solver",
                 "floor_collision_material": self._floor_collision_material.to_dict()},
                {"$type": "set_obi_fluid_rendering"},
                {"$type": "send_image_sensors"},
                {"$type": "send_static_rigidbodies"},
                {"$type": "send_static_robots"},
                {"$type": "send_static_composite_objects"},
                {"$type": "send_static_oculus_touch"}]

    def on_send(self, resp: List[bytes]) -> None:
        if not self._initialized_obi:
            self._initialized_obi = True
            collision_materials = dict()
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                # Enable image sensors for Obi rendering.
                if r_id == "imse":
                    images_sensors = ImageSensors(resp[i])
                    avatar_id = images_sensors.get_avatar_id()
                    for j in range(images_sensors.get_num_sensors()):
                        self.commands.append({"$type": "initialize_avatar_for_obi_fluid_rendering",
                                              "avatar_id": avatar_id,
                                              "sensor_name": images_sensors.get_sensor_name(j)})
                # Add Obi colliders to each object. Convert each object's physic material to an Obi collision material.
                elif r_id == "srig":
                    static_rigidbodies = StaticRigidbodies(resp[i])
                    for j in range(static_rigidbodies.get_num()):
                        object_id = static_rigidbodies.get_id(j)
                        # Get an override material.
                        if object_id in self._collision_material_overrides:
                            if isinstance(self._collision_material_overrides[object_id], str):
                                collision_material = COLLISION_MATERIALS[self._collision_material_overrides[object_id]].to_dict()
                            elif isinstance(self._collision_material_overrides[object_id], CollisionMaterial):
                                collision_material = self._collision_material_overrides[object_id].to_dict()
                            else:
                                raise Exception(self._collision_material_overrides[object_id])
                        else:
                            collision_material = CollisionMaterial(dynamic_friction=static_rigidbodies.get_dynamic_friction(j),
                                                                   static_friction=static_rigidbodies.get_static_friction(j),
                                                                   stickiness=0,
                                                                   stick_distance=0,
                                                                   friction_combine=0,
                                                                   stickiness_combine=0).to_dict()
                        collision_materials[object_id] = collision_material
                        self.commands.append({"$type": "create_obi_colliders",
                                              "id": object_id,
                                              "collision_material": collision_material})
                # Apply the same collision material used in the root object of a composite object to the sub-objects.
                elif r_id == "scom":
                    static_composite_objects = StaticCompositeObjects(resp[i])
                    for j in range(static_composite_objects.get_num()):
                        s = CompositeObjectStatic(static_composite_objects=static_composite_objects, object_index=j)
                        for sub_object_id in s.sub_object_ids:
                            assert sub_object_id not in collision_materials, sub_object_id
                            self.commands.append({"$type": "create_obi_colliders",
                                                  "id": sub_object_id,
                                                  "collision_material": collision_materials[s.object_id]})
                # Add colliders to robots.
                elif r_id == "srob":
                    static_robot = StaticRobot(resp[i])
                    self.commands.append({"$type": "create_obi_colliders",
                                          "id": static_robot.get_id(),
                                          "collision_material": DEFAULT_MATERIAL.to_dict()})
                # Add colliders to an Oculus Touch rig.
                elif r_id == "soct":
                    self.commands.append({"$type": "initialize_vr_rig_for_obi",
                                          "collision_material": DEFAULT_MATERIAL.to_dict()})

    def create_fluid_cube_emitter(self, object_id: int, fluid: Union[str, Fluid, GranularFluid], position: Dict[str, float] = None,
                                  rotation: Dict[str, float] = None, speed: float = 1, lifespan: float = 4,
                                  minimum_pool_size: float = 0.5, solver_id: int = 0, particle_radius_scale: float = 1.7,
                                  random_velocity: float = 0, size: Dict[str, float] = None,
                                  sampling_method: SamplingMethod = SamplingMethod.volume) -> None:
        """
        Create a cube-shaped fluid emitter.

        :param object_id: The unique ID of the emitter.
        :param position: The position of the emitter object. If None, defaults to (0, 0, 0).
        :param rotation: The rotation of the emitter object, in Euler angles.  If None, defaults to (0, 0, 0).
        :param speed: The speed of emission in meters per second. If 0, there is no emission.
        :param lifespan: The particle lifespan in seconds.
        :param minimum_pool_size: The minimum amount of inactive particles available before the emitter is allowed to resume emission.
        :param solver_id: The ID of the Obi solver.
        :param particle_radius_scale: This scales the size at which particles are drawn.
        :param random_velocity: Random velocity of emitted particles.
        :param fluid: Either a [`Fluid`](../obi_data/fluid.md), a [`GranularFluid`](../obi_data/granular_fluid.md), the name of a fluid (see `Fluid.FLUIDS`), or the name of a granular fluid (see `GranularFluid.GRANULAR_FLUIDS`).
        :param size: The size of the cube in meters. If None, defaults to (1, 1, 1).
        :param sampling_method: The [`SamplingMethod`](../obi_data/sampling_method).
        """

        command = {"$type": "create_obi_fluid_cube_emitter",
                   "sampling_method": sampling_method.name,
                   "size": size if size is not None else {"x": 1, "y": 1, "z": 1}}
        command.update(self._get_add_fluid_emitter_command(object_id=object_id, position=position, rotation=rotation,
                                                           speed=speed, lifespan=lifespan,
                                                           minimum_pool_size=minimum_pool_size,
                                                           solver_id=solver_id, particle_radius_scale=particle_radius_scale,
                                                           random_velocity=random_velocity, fluid=fluid))
        self.commands.append(command)

    def create_fluid_edge_emitter(self, object_id: int, fluid: Union[str, Fluid, GranularFluid],
                                  position: Dict[str, float] = None, rotation: Dict[str, float] = None, speed: float = 1,
                                  lifespan: float = 4, minimum_pool_size: float = 0.5, solver_id: int = 0,
                                  particle_radius_scale: float = 1.7, random_velocity: float = 0,
                                  emitter_length: float = 0.25, radial_velocity: float = 1) -> None:
        """
        Create a linear-shaped fluid emitter.

        :param object_id: The unique ID of the emitter.
        :param position: The position of the emitter object. If None, defaults to (0, 0, 0).
        :param rotation: The rotation of the emitter object, in Euler angles.  If None, defaults to (0, 0, 0).
        :param speed: The speed of emission in meters per second. If 0, there is no emission.
        :param lifespan: The particle lifespan in seconds.
        :param minimum_pool_size: The minimum amount of inactive particles available before the emitter is allowed to resume emission.
        :param solver_id: The ID of the Obi solver.
        :param particle_radius_scale: This scales the size at which particles are drawn.
        :param random_velocity: Random velocity of emitted particles.
        :param fluid: Either a [`Fluid`](../obi_data/fluid.md), a [`GranularFluid`](../obi_data/granular_fluid.md), the name of a fluid (see `Fluid.FLUIDS`), or the name of a granular fluid (see `GranularFluid.GRANULAR_FLUIDS`).
        :param emitter_length: The length of the edge in local units.
        :param radial_velocity: The velocity twisting along the length of the edge.
        """

        command = {"$type": "create_obi_fluid_cube_emitter",
                   "emitter_length": emitter_length,
                   "radial_velocity": radial_velocity}
        command.update(self._get_add_fluid_emitter_command(object_id=object_id, position=position, rotation=rotation,
                                                           speed=speed, lifespan=lifespan,
                                                           minimum_pool_size=minimum_pool_size, solver_id=solver_id,
                                                           particle_radius_scale=particle_radius_scale,
                                                           random_velocity=random_velocity, fluid=fluid))
        self.commands.append(command)

    def create_fluid_disk_emitter(self, object_id: int, fluid: Union[str, Fluid, GranularFluid],
                                  position: Dict[str, float] = None, rotation: Dict[str, float] = None, speed: float = 1,
                                  lifespan: float = 4, minimum_pool_size: float = 0.5, solver_id: int = 0,
                                  particle_radius_scale: float = 1.7, random_velocity: float = 0,
                                  emitter_radius: float = 0.5, edge_emission: bool = False) -> None:
        """
        Create a disk-shaped fluid emitter.

        :param object_id: The unique ID of the emitter.
        :param position: The position of the emitter object. If None, defaults to (0, 0, 0).
        :param rotation: The rotation of the emitter object, in Euler angles.  If None, defaults to (0, 0, 0).
        :param speed: The speed of emission in meters per second. If 0, there is no emission.
        :param lifespan: The particle lifespan in seconds.
        :param minimum_pool_size: The minimum amount of inactive particles available before the emitter is allowed to resume emission.
        :param solver_id: The ID of the Obi solver.
        :param particle_radius_scale: This scales the size at which particles are drawn.
        :param random_velocity: Random velocity of emitted particles.
        :param fluid: Either a [`Fluid`](../obi_data/fluid.md), a [`GranularFluid`](../obi_data/granular_fluid.md), the name of a fluid (see `Fluid.FLUIDS`), or the name of a granular fluid (see `GranularFluid.GRANULAR_FLUIDS`).
        :param emitter_radius: The radius of the circle.
        :param edge_emission: If enabled, particles will be emitted from the circle's edges, instead of its interior.
        """

        command = {"$type": "create_obi_fluid_cube_emitter",
                   "emitter_radius": emitter_radius,
                   "edge_emission": edge_emission}
        command.update(self._get_add_fluid_emitter_command(object_id=object_id, position=position, rotation=rotation,
                                                           speed=speed, lifespan=lifespan,
                                                           minimum_pool_size=minimum_pool_size,
                                                           solver_id=solver_id,
                                                           particle_radius_scale=particle_radius_scale,
                                                           random_velocity=random_velocity, fluid=fluid))
        self.commands.append(command)

    def create_fluid_sphere_emitter(self, object_id: int, fluid: Union[str, Fluid, GranularFluid],
                                    position: Dict[str, float] = None, rotation: Dict[str, float] = None,
                                    speed: float = 1, lifespan: float = 4, minimum_pool_size: float = 0.5,
                                    solver_id: int = 0, particle_radius_scale: float = 1.7, random_velocity: float = 0,
                                    radius: float = 0.5, sampling_method: SamplingMethod = SamplingMethod.volume) -> None:
        """
        Create a sphere-shaped fluid emitter.

        :param object_id: The unique ID of the emitter.
        :param position: The position of the emitter object. If None, defaults to (0, 0, 0).
        :param rotation: The rotation of the emitter object, in Euler angles.  If None, defaults to (0, 0, 0).
        :param speed: The speed of emission in meters per second. If 0, there is no emission.
        :param lifespan: The particle lifespan in seconds.
        :param minimum_pool_size: The minimum amount of inactive particles available before the emitter is allowed to resume emission.
        :param solver_id: The ID of the Obi solver.
        :param particle_radius_scale: This scales the size at which particles are drawn.
        :param random_velocity: Random velocity of emitted particles.
        :param fluid: Either a [`Fluid`](../obi_data/fluid.md), a [`GranularFluid`](../obi_data/granular_fluid.md), the name of a fluid (see `Fluid.FLUIDS`), or the name of a granular fluid (see `GranularFluid.GRANULAR_FLUIDS`).
        :param radius: The radius of the sphere.
        :param sampling_method: The [`SamplingMethod`](../obi_data/sampling_method).
        """

        command = {"$type": "create_obi_fluid_cube_emitter",
                   "sampling_method": sampling_method,
                   "radius": radius}
        command.update(self._get_add_fluid_emitter_command(object_id=object_id, position=position, rotation=rotation,
                                                           speed=speed, lifespan=lifespan,
                                                           minimum_pool_size=minimum_pool_size, solver_id=solver_id,
                                                           particle_radius_scale=particle_radius_scale,
                                                           random_velocity=random_velocity, fluid=fluid))
        self.commands.append(command)

    def set_fluid_speed(self, object_id: int, speed: float) -> None:
        """
        Set the speed of a fluid emitter. By default, the speed of an emitter is 0.

        :param object_id: The ID of the fluid emitter.
        :param speed: The speed in meters per second. Set this to 0 to stop emission.
        """

        self.commands.append({"$type": "set_obi_fluid_emission_speed",
                              "id": object_id,
                              "speed": speed})

    def reset(self, floor_collision_material: CollisionMaterial = None,
              collision_material_overrides: Dict[int, Union[str, CollisionMaterial]] = None):
        self.commands.clear()
        self.initialized = False
        self._initialized_obi = False
        if floor_collision_material is None:
            self._floor_collision_material = DEFAULT_MATERIAL
        else:
            self._floor_collision_material = floor_collision_material
        if collision_material_overrides is None:
            self._collision_material_overrides = dict()
        else:
            self._collision_material_overrides = collision_material_overrides

    @staticmethod
    def _get_add_fluid_emitter_command(object_id: int, position: Optional[Dict[str, float]],
                                       rotation: Optional[Dict[str, float]], speed: float,
                                       lifespan: float, minimum_pool_size: float, solver_id: int,
                                       particle_radius_scale: float, random_velocity: float,
                                       fluid: Union[str, Fluid, GranularFluid]) -> dict:
        """
        :param object_id: The unique ID of the emitter.
        :param position: The position of the emitter object.
        :param rotation: The rotation of the emitter object, in Euler angles.
        :param lifespan: The particle lifespan in seconds.
        :param minimum_pool_size: The minimum amount of inactive particles available before the emitter is allowed to resume emission.
        :param solver_id: The ID of the Obi solver.
        :param particle_radius_scale: This scales the size at which particles are drawn.
        :param random_velocity: Random velocity of emitted particles.
        :param speed: The emission speed.
        :param fluid: The fluid.

        :return: A partial fluid emitter command.
        """

        if position is None:
            position = {"x": 0, "y": 0, "z": 0}
        if rotation is None:
            rotation = {"x": 0, "y": 0, "z": 0}
        if isinstance(fluid, str):
            if fluid in FLUIDS:
                f = FLUIDS[fluid]
            elif fluid in GRANULAR_FLUIDS:
                f = GRANULAR_FLUIDS[fluid]
            else:
                raise Exception(f"Fluid not found: {fluid}")
        else:
            f = fluid
        return {"id": object_id, "position": position, "rotation": rotation, "lifespan": lifespan,
                "minimum_pool_size": minimum_pool_size, "solver_id": solver_id,
                "particle_radius_scale": particle_radius_scale, "random_velocity": random_velocity, "speed": speed,
                "fluid": f.to_dict()}
