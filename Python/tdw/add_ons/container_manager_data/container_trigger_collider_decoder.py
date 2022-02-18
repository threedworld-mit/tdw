import json
from tdw.add_ons.container_manager_data.container_collider_tag import ContainerColliderTag


class ContainerTriggerColliderDecoder(json.JSONDecoder):
    """
    Decode container trigger collider data from a JSON dictionary.
    """

    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=ContainerTriggerColliderDecoder.dict_to_object)

    @staticmethod
    def dict_to_object(dictionary):
        from tdw.add_ons.container_manager_data.container_box_trigger_collider import ContainerBoxTriggerCollider
        from tdw.add_ons.container_manager_data.container_sphere_trigger_collider import ContainerSphereTriggerCollider
        from tdw.add_ons.container_manager_data.container_cylinder_trigger_collider import ContainerCylinderTriggerCollider
        from tdw.collision_data.trigger_collider_shape import TriggerColliderShape
        if "shape" in dictionary and "tag" in dictionary:
            shape = TriggerColliderShape[dictionary["shape"]]
            tag = ContainerColliderTag[dictionary["tag"]]
            if shape == TriggerColliderShape.box:
                obj = ContainerBoxTriggerCollider(tag=tag,
                                                  position=dictionary["position"],
                                                  scale=dictionary["scale"])
            elif shape == TriggerColliderShape.cylinder:
                obj = ContainerCylinderTriggerCollider(tag=tag,
                                                       position=dictionary["position"],
                                                       scale=dictionary["scale"])
            elif shape == TriggerColliderShape.sphere:
                obj = ContainerSphereTriggerCollider(tag=tag,
                                                     position=dictionary["position"],
                                                     diameter=dictionary["diameter"])
            else:
                raise Exception(shape)
        else:
            obj = dictionary
        return obj