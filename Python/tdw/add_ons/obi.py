from typing import List, Dict, Union
from tdw.add_ons.add_on import AddOn
from tdw.output_data import OutputData, ObiParticles, StaticRigidbodies, StaticRobot
from tdw.obi_data.fluids.fluid import Fluid, FLUIDS
from tdw.obi_data.fluids.granular_fluid import GranularFluid, GRANULAR_FLUIDS
from tdw.obi_data.fluids.emitter_shape import EmitterShape
from tdw.obi_data.obi_actor import ObiActor
from tdw.obi_data.collision_materials.collision_material import CollisionMaterial


class Obi(AddOn):
    """
    This add-on handles most aspects of an Obi physics simulation, including initialization, actor creation, and particle output data.
    """

    def __init__(self, output_data: bool = True, floor_material: CollisionMaterial = None,
                 object_materials: Dict[int, CollisionMaterial] = None, vr_material: CollisionMaterial = None):
        """
        :param output_data: If True, receive [`ObiParticles`](../../api/output_data.md#ObiParticles) per frame.
        :param floor_material: The floor's [`CollisionMaterial`](../obi_data/collision_materials/collision_material.md). If None, uses default values.
        :param object_materials: Overrides for object and robot collision materials. Key = Object or Robot ID. Value = [`CollisionMaterial`](../obi_data/collision_materials/collision_material.md).
        :param vr_material: If there is a VR rig in the scene, its hands will have this [`CollisionMaterial`](../obi_data/collision_materials/collision_material.md). If None, uses default values.
        """

        super().__init__()
        """:field
        A dictionary of Obi actor data. Key = Object ID. Value = [`ObiActor`](../obi_data/obi_actor.md). The particle data is updated if `output_data == True` (see above).
        """
        self.actors: Dict[int, ObiActor] = dict()
        self._output_data: bool = output_data
        self._need_to_initialize_obi: bool = True
        if floor_material is None:
            self._floor_material: CollisionMaterial = CollisionMaterial()
        else:
            self._floor_material = floor_material
        if object_materials is None:
            self._object_materials: Dict[int, CollisionMaterial] = dict()
        else:
            self._object_materials = object_materials
        if vr_material is None:
            self._vr_material: CollisionMaterial = CollisionMaterial()
        else:
            self._vr_material = vr_material

    def get_initialization_commands(self) -> List[dict]:
        commands = [{"$type": "destroy_obi_solver"},
                    {"$type": "create_obi_solver"},
                    {"$type": "send_static_oculus_touch"},
                    {"$type": "send_static_rigidbodies"},
                    {"$type": "send_static_robots"},
                    {"$type": "create_floor_obi_colliders"}]
        # Set the floor material.
        floor_material_command = {"$type": "set_floor_obi_collision_material"}
        floor_material_command.update(self._floor_material.to_dict())
        commands.append(floor_material_command)
        if self._output_data:
            commands.append({"$type": "send_obi_particles",
                             "frequency": "always"})
        return commands

    def on_send(self, resp: List[bytes]) -> None:
        if self._need_to_initialize_obi:
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                # Add Obi colliders to each object with a rigidbody.
                if r_id == "srig":
                    static_rigidbodies = StaticRigidbodies(resp[i])
                    for j in range(static_rigidbodies.get_num()):
                        object_id = static_rigidbodies.get_id(j)
                        self.commands.append({"$type": "create_obi_colliders",
                                              "id": object_id})
                        material_command = {"$type": "set_obi_collision_material",
                                            "id": object_id}
                        # Use override values.
                        if object_id in self._object_materials:
                            material_command.update(self._object_materials[object_id].to_dict())
                        # Use the Unity physic material values here and the default Obi values.
                        else:
                            material_command.update({"dynamic_friction": static_rigidbodies.get_dynamic_friction(j),
                                                     "static_friction": static_rigidbodies.get_static_friction(j)})
                        self.commands.append(material_command)
                # Add Obi colliders to each robot and Magnebot.
                elif r_id == "srob":
                    static_robot = StaticRobot(resp[i])
                    robot_id = static_robot.get_id()
                    self.commands.append({"$type": "create_robot_obi_colliders",
                                          "id": robot_id})
                    material_command = {"$type": "set_robot_obi_collision_material",
                                        "id": robot_id}
                    if robot_id in self._object_materials:
                        material_command.update(self._object_materials[robot_id].to_dict())
                    else:
                        material_command.update(CollisionMaterial().to_dict())
                    self.commands.append(material_command)
                # Add Obi colliders to the VR rig.
                elif r_id == "soct":
                    self.commands.append({"$type": "create_vr_obi_colliders"})
                    material_command = {"$type": "set_vr_obi_collision_material"}
                    material_command.update(self._vr_material.to_dict())
                    self.commands.append(material_command)
            self._need_to_initialize_obi = False
        # Parse particle data.
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "obip":
                obi_particles = ObiParticles(resp[i])
                for j in range(obi_particles.get_num_objects()):
                    object_id = obi_particles.get_object_id(j)
                    # Add an actor.
                    if object_id not in self.actors:
                        self.actors[object_id] = ObiActor(object_id=object_id,
                                                          object_index=j,
                                                          solver_id=obi_particles.get_solver_id(j))
                # Update the particles.
                for object_id in self.actors:
                    self.actors[object_id].on_communicate(obi_particles=obi_particles)

    def create_fluid(self, object_id: int, fluid: Union[str, Fluid, GranularFluid], shape: EmitterShape,
                     position: Dict[str, float] = None, rotation: Dict[str, float] = None, speed: float = 0,
                     lifespan: float = 4, minimum_pool_size: float = 0.5, solver_id: int = 0) -> None:
        """
        Create a cube-shaped fluid emitter.

        :param object_id: The unique ID of the emitter.
        :param fluid: Either a [`Fluid`](../obi_data/fluids/fluid.md), a [`GranularFluid`](../obi_data/fluids/granular_fluid.md), the name of a fluid (see `Fluid.FLUIDS`), or the name of a granular fluid (see `GranularFluid.GRANULAR_FLUIDS`).
        :param shape: Either a [`CubeEmitter`](../obi_data/fluids/cube_emitter.md), [`DiskEmitter`](../obi_data/fluids/disk_emitter.md), [`EdgeEmitter`](../obi_data/fluids/edge_emitter.md), or [`SphereEmitter`](../obi_data/fluids/sphere_emitter.md).
        :param position: The position of the emitter object. If None, defaults to (0, 0, 0).
        :param rotation: The rotation of the emitter object, in Euler angles.  If None, defaults to (0, 0, 0).
        :param speed: The speed of emission in meters per second. If 0, there is no emission.
        :param lifespan: The particle lifespan in seconds.
        :param minimum_pool_size: The minimum amount of inactive particles available before the emitter is allowed to resume emission.
        :param solver_id: The ID of the Obi solver.
        """

        # Set a default position and rotation.
        if position is None:
            position = {"x": 0, "y": 0, "z": 0}
        if rotation is None:
            rotation = {"x": 0, "y": 0, "z": 0}
        # Get the fluid. If it's a string, it's a preset.
        if isinstance(fluid, str):
            if fluid in FLUIDS:
                f = FLUIDS[fluid]
            elif fluid in GRANULAR_FLUIDS:
                f = GRANULAR_FLUIDS[fluid]
            else:
                raise Exception(f"Fluid not found: {fluid}")
        else:
            f = fluid
        self.commands.append({"$type": "create_obi_fluid",
                              "id": object_id,
                              "fluid": f.to_dict(),
                              "shape": shape.to_dict(),
                              "position": position,
                              "rotation": rotation,
                              "lifespan": lifespan,
                              "minimum_pool_size": minimum_pool_size,
                              "solver_id": solver_id,
                              "speed": speed})

    def set_fluid_speed(self, object_id: int, speed: float) -> None:
        """
        Set the speed of a fluid emitter. By default, the speed of an emitter is 0 (no fluid emission).

        :param object_id: The ID of the fluid emitter.
        :param speed: The speed in meters per second. Set this to 0 to stop emission.
        """

        self.commands.append({"$type": "set_obi_fluid_emission_speed",
                              "id": object_id,
                              "speed": speed})

    def reset(self, floor_material: CollisionMaterial = None, object_materials: Dict[int, CollisionMaterial] = None,
              vr_material: CollisionMaterial = None) -> None:
        """
        :param floor_material: The floor's [`CollisionMaterial`](../obi_data/collision_materials/collision_material.md). If None, uses default values.
        :param object_materials: Overrides for object and robot collision materials. Key = Object or Robot ID. Value = [`CollisionMaterial`](../obi_data/collision_materials/collision_material.md).
        :param vr_material: If there is a VR rig in the scene, its hands will have this [`CollisionMaterial`](../obi_data/collision_materials/collision_material.md). If None, uses default values.
        """

        self.commands.clear()
        self.initialized = False
        self.actors.clear()
        self._need_to_initialize_obi = True
        if floor_material is None:
            self._floor_material = CollisionMaterial()
        else:
            self._floor_material = floor_material
        if object_materials is None:
            self._object_materials.clear()
        else:
            self._object_materials = object_materials
        if vr_material is None:
            self._vr_material = CollisionMaterial()
        else:
            self._vr_material = vr_material
