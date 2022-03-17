from typing import List, Dict, Union
from tdw.controller import Controller
from tdw.add_ons.add_on import AddOn
from tdw.output_data import OutputData, ImageSensors, StaticRigidbodies, StaticCompositeObjects, StaticRobot
from tdw.obi_data.collision_material import CollisionMaterial, COLLISION_MATERIALS, DEFAULT_MATERIAL
from tdw.object_data.composite_object.composite_object_static import CompositeObjectStatic


class Obi(AddOn):
    def __init__(self, floor_collision_material: CollisionMaterial = None,
                 collision_material_overrides: Dict[int, CollisionMaterial] = None):
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
                            collision_material = self._collision_material_overrides[object_id].to_dict()
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
