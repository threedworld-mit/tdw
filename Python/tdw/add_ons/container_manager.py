from typing import List, Dict
from tdw.output_data import OutputData, SegmentationColors, StaticCompositeObjects
from tdw.add_ons.trigger_collision_manager import TriggerCollisionManager
from tdw.container_data.container_collider_tag import ContainerColliderTag
from tdw.container_data.container_box_trigger_collider import ContainerBoxTriggerCollider
from tdw.container_data.container_sphere_trigger_collider import ContainerSphereTriggerCollider
from tdw.container_data.container_cylinder_trigger_collider import ContainerCylinderTriggerCollider
from tdw.container_data.containment_event import ContainmentEvent
from tdw.object_data.composite_object.composite_object_static import CompositeObjectStatic
from tdw.controller import Controller


class ContainerManager(TriggerCollisionManager):
    """
    Manage trigger collisions for 'container' objects.

    'Containers' can be concave objects such as baskets but they don't have to be. For example, a table surface can be a 'container' and if another object is on that surface, the table is currently 'containing' that object.

    An object is 'contained' by a 'container' if:

    1. There is a trigger "enter" or "stay" event.
    2. The trigger event is between the object and one of the trigger colliders added via this add-on.
    """

    def __init__(self):
        """
        (no parameters)
        """

        super().__init__()
        self._getting_model_names: bool = True
        """:field
        A dictionary describing which objects contain other objects on this frame. This is updated per-frame. Key = The container ID *(not the trigger ID)*. Value = A list of [`ContainmentEvent`](../container_data/containment_event.md) data.
        """
        self.events: Dict[int, List[ContainmentEvent]] = dict()
        # Tags describing each collider. Key = The trigger ID. Value = `ContainerColliderTag`.
        self._tags: Dict[int, ContainerColliderTag] = dict()
        self._excluded_objects: List[int] = list()

    def get_initialization_commands(self) -> List[dict]:
        """
        This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

        :return: A list of commands that will initialize this add-on.
        """

        return [{"$type": "send_segmentation_colors"},
                {"$type": "send_static_composite_objects"}]

    def on_send(self, resp: List[bytes]) -> None:
        """
        This is called after commands are sent to the build and a response is received.

        Use this function to send commands to the build on the next frame, given the `resp` response.
        Any commands in the `self.commands` list will be sent on the next frame.

        :param resp: The response from the build.
        """

        # Get model names.
        if self._getting_model_names:
            self._getting_model_names = False
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                # Use the model names from SegmentationColors output data to add trigger colliders.
                if r_id == "segm":
                    segmentation_colors = SegmentationColors(resp[i])
                    for j in range(segmentation_colors.get_num()):
                        object_id = segmentation_colors.get_object_id(j)
                        model_name = segmentation_colors.get_object_name(j).lower()
                        # Fine the model record.
                        for library_path in Controller.MODEL_LIBRARIANS:
                            record = Controller.MODEL_LIBRARIANS[library_path].get_record(model_name)
                            if record is not None:
                                for trigger_collider_data in record.container_colliders:
                                    if isinstance(trigger_collider_data, ContainerBoxTriggerCollider):
                                        self.add_box_collider(object_id=object_id,
                                                              position=trigger_collider_data.position,
                                                              scale=trigger_collider_data.scale,
                                                              tag=trigger_collider_data.tag)
                                    elif isinstance(trigger_collider_data, ContainerCylinderTriggerCollider):
                                        self.add_cylinder_collider(object_id=object_id,
                                                                   position=trigger_collider_data.position,
                                                                   scale=trigger_collider_data.scale,
                                                                   tag=trigger_collider_data.tag)
                                    elif isinstance(trigger_collider_data, ContainerSphereTriggerCollider):
                                        self.add_sphere_collider(object_id=object_id,
                                                                 position=trigger_collider_data.position,
                                                                 diameter=trigger_collider_data.diameter,
                                                                 tag=trigger_collider_data.tag)
                                    else:
                                        raise Exception(trigger_collider_data)
                                break
                elif r_id == "scom":
                    static_composite_objects = StaticCompositeObjects(resp[i])
                    for j in range(static_composite_objects.get_num()):
                        s = CompositeObjectStatic(static_composite_objects, j)
                        self._excluded_objects.extend(s.sub_object_ids)
        super().on_send(resp=resp)
        # Get containment.
        self.events.clear()
        # Get objects that are in containers.
        for trigger_collision in self.collisions:
            if trigger_collision.trigger_id in self.trigger_ids and \
                    (trigger_collision.state == "enter" or trigger_collision.state == "stay") and \
                    trigger_collision.collider_id not in self._excluded_objects:
                if trigger_collision.collidee_id not in self.events:
                    self.events[trigger_collision.collidee_id] = list()
                # Record the event.
                self.events[trigger_collision.collidee_id].append(ContainmentEvent(container_id=trigger_collision.collidee_id,
                                                                                   object_id=trigger_collision.collider_id,
                                                                                   tag=self._tags[trigger_collision.trigger_id]))
        # Remove duplicate events.
        self.events = {k: list(set(v)) for k, v in self.events.items()}

    def add_box_collider(self, object_id: int, position: Dict[str, float], scale: Dict[str, float],
                         rotation: Dict[str, float] = None, trigger_id: int = None,
                         tag: ContainerColliderTag = ContainerColliderTag.on) -> int:
        """
        Add a box-shaped trigger collider to an object. Optionally, set the trigger collider's containment semantic tag.

        :param object_id: The ID of the object.
        :param position: The position of the trigger collider relative to the parent object.
        :param scale: The scale of the trigger collider.
        :param rotation: The rotation of the trigger collider in Euler angles relative to the parent object. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param trigger_id: The unique ID of the trigger collider. If None, an ID will be automatically assigned.
        :param tag: The semantic [`ContainerColliderTag`](../container_data/container_collider_tag.md).

        :return: The ID of the trigger collider.
        """

        trigger_id = super().add_box_collider(object_id=object_id, position=position, scale=scale, rotation=rotation,
                                              trigger_id=trigger_id)
        # Remember the tag.
        self._tags[trigger_id] = tag
        return trigger_id

    def add_cylinder_collider(self, object_id: int, position: Dict[str, float], scale: Dict[str, float],
                              rotation: Dict[str, float] = None, trigger_id: int = None,
                              tag: ContainerColliderTag = ContainerColliderTag.on) -> int:
        """
        Add a cylinder-shaped trigger collider to an object. Optionally, set the trigger collider's containment semantic tag.

        :param object_id: The ID of the object.
        :param position: The position of the trigger collider relative to the parent object.
        :param scale: The scale of the trigger collider.
        :param rotation: The rotation of the trigger collider in Euler angles relative to the parent object. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param trigger_id: The unique ID of the trigger collider. If None, an ID will be automatically assigned.
        :param tag: The semantic [`ContainerColliderTag`](../container_data/container_collider_tag.md).

        :return: The ID of the trigger collider.
        """

        trigger_id = super().add_cylinder_collider(object_id=object_id, position=position, scale=scale, rotation=rotation,
                                                   trigger_id=trigger_id)
        # Remember the tag.
        self._tags[trigger_id] = tag
        return trigger_id

    def add_sphere_collider(self, object_id: int, position: Dict[str, float], diameter: float, trigger_id: int = None,
                            tag: ContainerColliderTag = ContainerColliderTag.on) -> int:
        """
        Add a sphere-shaped trigger collider to an object. Optionally, set the trigger collider's containment semantic tag.

        :param object_id: The ID of the object.
        :param position: The position of the trigger collider relative to the parent object.
        :param diameter: The diameter of the trigger collider.
        :param trigger_id: The unique ID of the trigger collider. If None, an ID will be automatically assigned.
        :param tag: The semantic [`ContainerColliderTag`](../container_data/container_collider_tag.md).

        :return: The ID of the trigger collider.
        """

        trigger_id = super().add_sphere_collider(object_id=object_id, position=position, diameter=diameter,
                                                 trigger_id=trigger_id)
        # Remember the tag.
        self._tags[trigger_id] = tag
        return trigger_id

    def reset(self) -> None:
        """
        Reset this add-on. Call this before resetting a scene.
        """

        super().reset()
        self._getting_model_names = True
        self.events.clear()
        self._tags.clear()
        self._excluded_objects.clear()
