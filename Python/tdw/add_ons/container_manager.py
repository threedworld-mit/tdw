from json import loads
from pkg_resources import resource_filename
from pathlib import Path
from typing import List, Dict
from tdw.output_data import OutputData, SegmentationColors, Rigidbodies
from tdw.add_ons.trigger_collision_listener import TriggerCollisionListener
from tdw.add_ons.container_manager_data.container_collider_tag import ContainerColliderTag
from tdw.add_ons.container_manager_data.containment_event import ContainmentEvent


class ContainerManager(TriggerCollisionListener):
    """
    Manage trigger collisions for 'container' objects.

    This add-on assigns trigger collisions based on a pre-defined dictionary of models and collider shapes, positions, etc. There are many models in TDW that could be containers but haven't been added to this dictionary yet. See: `ContainerManager.CONTAINERS`.

    'Containers' can be concave objects such as baskets but they don't have to be. For example, a table surface can be a 'container' and if another object is on that surface, the table is currently 'containing' that object.

    An object is 'contained' by a 'container' if:

    1. The object isn't moving (the Rigidbody is sleeping).
    2. There is a trigger "enter" or "stay" event.
    3. The trigger event is between the object and one of the container trigger colliders.
    """

    """:class_var
    A dictionary of all container model names and their trigger colliders.
    """
    CONTAINERS: dict = loads(Path(resource_filename(__name__, "container_manager_data/colliders.json")).read_text())

    def __init__(self):
        """
        (no parameters)
        """

        super().__init__()
        self._getting_model_names: bool = True
        """:field
        A dictionary of trigger colliders used for containers. Key = The trigger ID. Value = The object ID.
        """
        self.container_trigger_ids:  Dict[int, int] = dict()
        """:field
        A dictionary describing which objects contain other objects on this frame. This is updated per-frame. Key = The container ID *(not the trigger ID)*. Value = A list of [`ContainmentEvent`](container_manager_data/containment_event.md) data.
        """
        self.containment: Dict[int, List[ContainmentEvent]] = dict()
        # Tags describing each collider. Key = The trigger ID. Value = `ContainerColliderTag`.
        self._tags: Dict[int, ContainerColliderTag] = dict()

    def get_initialization_commands(self) -> List[dict]:
        """
        This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

        :return: A list of commands that will initialize this add-on.
        """

        return [{"$type": "send_segmentation_colors"},
                {"$type": "send_rigidbodies",
                 "frequency": "always"}]

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
                        # This is a container. Add trigger colliders.
                        if model_name in ContainerManager.CONTAINERS:
                            if "box" in ContainerManager.CONTAINERS[model_name]:
                                for collider in ContainerManager.CONTAINERS[model_name]["cube"]:
                                    self.add_box_collider(object_id=object_id,
                                                          position=collider["position"],
                                                          scale=collider["scale"])
                            if "sphere" in ContainerManager.CONTAINERS[model_name]:
                                for collider in ContainerManager.CONTAINERS[model_name]["sphere"]:
                                    self.add_sphere_collider(object_id=object_id,
                                                             position=collider["position"],
                                                             diameter=collider["diameter"])
                    break
        super().on_send(resp=resp)
        # Get all sleeping objects.
        sleeping: List[int] = list()
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "rigi":
                rigidbodies = Rigidbodies(resp[i])
                for j in range(rigidbodies.get_num()):
                    if rigidbodies.get_sleeping(j):
                        sleeping.append(rigidbodies.get_id(j))
                break
        # Get containment.
        self.containment.clear()
        # An object is contained by a container if:
        # 1. The object is sleeping.
        # 2. The trigger collider is a container collider.
        # 3. The trigger event is "enter" or "stay".
        for trigger_collision in self.collisions:
            if trigger_collision.collider_id in sleeping and \
                    trigger_collision.trigger_id in self.container_trigger_ids and \
                    (trigger_collision.state == "enter" or trigger_collision.state == "stay"):
                if trigger_collision.collidee_id not in self.containment:
                    self.containment[trigger_collision.collidee_id] = list()
                # Record the event.
                if trigger_collision.collider_id not in self.containment[trigger_collision.collidee_id]:
                    self.containment[trigger_collision.collidee_id].append(ContainmentEvent(container_id=trigger_collision.collidee_id,
                                                                                            object_id=trigger_collision.collider_id,
                                                                                            tag=self._tags[trigger_collision.trigger_id]))

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
        :param tag: The semantic [`ContainerColliderTag`](collision_manager_data/container_collider_tag.md).

        :return: The ID of the trigger collider.
        """

        trigger_id = super().add_box_collider(object_id=object_id, position=position, scale=scale, rotation=rotation,
                                              trigger_id=trigger_id)
        # Remember the tag.
        self._tags[trigger_id] = ContainerColliderTag[tag]
        # Remember the IDs.
        self.container_trigger_ids[trigger_id] = object_id
        return trigger_id

    def add_sphere_collider(self, object_id: int, position: Dict[str, float], diameter: float, trigger_id: int = None,
                            tag: ContainerColliderTag = ContainerColliderTag.on) -> int:
        """
        Add a sphere-shaped trigger collider to an object. Optionally, set the trigger collider's containment semantic tag.

        :param object_id: The ID of the object.
        :param position: The position of the trigger collider relative to the parent object.
        :param diameter: The diameter of the trigger collider.
        :param trigger_id: The unique ID of the trigger collider. If None, an ID will be automatically assigned.
        :param tag: The semantic [`ContainerColliderTag`](collision_manager_data/container_collider_tag.md).

        :return: The ID of the trigger collider.
        """

        trigger_id = super().add_sphere_collider(object_id=object_id, position=position, diameter=diameter,
                                                 trigger_id=trigger_id)
        # Remember the tag.
        self._tags[trigger_id] = ContainerColliderTag[tag]
        # Remember the IDs.
        self.container_trigger_ids[trigger_id] = object_id
        return trigger_id

    def reset(self) -> None:
        """
        Reset this add-on. Call this before resetting a scene.
        """

        super().reset()
        self._getting_model_names = True
        self.container_trigger_ids.clear()
        self.containment.clear()
        self._tags.clear()
