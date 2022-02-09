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
        self.container_colliders:  Dict[int, int] = dict()
        """:field
        A dictionary describing which objects contain other objects on this frame. This is updated per-frame. Key = The container ID *(not the trigger ID)*. Value = A list of [`ContainmentEvent`](container_manager_data/containment_event.md) data.
        """
        self.containment: Dict[int, List[ContainmentEvent]] = dict()
        """:field
        Tags describing each collider. Key = The trigger ID. Value = [`ContainerColliderTag`](container_manager_data/container_collider_tag.md).
        """
        self.tags: Dict[int, ContainerColliderTag] = dict()

    def get_initialization_commands(self) -> List[dict]:
        return [{"$type": "send_segmentation_colors"},
                {"$type": "send_rigidbodies",
                 "frequency": "always"}]

    def on_send(self, resp: List[bytes]) -> None:
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
                            if "cube" in ContainerManager.CONTAINERS[model_name]:
                                for collider in ContainerManager.CONTAINERS[model_name]["cube"]:
                                    trigger_collider = self.add_box_collider(object_id=object_id,
                                                                             position=collider["position"],
                                                                             scale=collider["scale"])
                                    self.tags[trigger_collider] = ContainerColliderTag[collider["tag"]]
                            if "sphere" in ContainerManager.CONTAINERS[model_name]:
                                for collider in ContainerManager.CONTAINERS[model_name]["sphere"]:
                                    trigger_collider = self.add_sphere_collider(object_id=object_id,
                                                                                position=collider["position"],
                                                                                diameter=collider["diameter"])
                                    self.tags[trigger_collider] = ContainerColliderTag[collider["tag"]]
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
                    trigger_collision.trigger_id in self.container_colliders and \
                    (trigger_collision.state == "enter" or trigger_collision.state == "stay"):
                if trigger_collision.collidee_id not in self.containment:
                    self.containment[trigger_collision.collidee_id] = list()
                # Record the event.
                if trigger_collision.collider_id not in self.containment[trigger_collision.collidee_id]:
                    self.containment[trigger_collision.collidee_id].append(ContainmentEvent(container_id=trigger_collision.collidee_id,
                                                                                            object_id=trigger_collision.collider_id,
                                                                                            tag=self.tags[trigger_collision.trigger_id]))

    def _add_trigger_collider(self, object_id: int, position: Dict[str, float], scale: Dict[str, float],
                              rotation: Dict[str, float], shape: str, trigger_id: int = None) -> int:
        trigger_id = super()._add_trigger_collider(object_id=object_id, position=position, scale=scale,
                                                   rotation=rotation, shape=shape, trigger_id=trigger_id)
        self.container_colliders[trigger_id] = object_id
        return trigger_id

    def reset(self) -> None:
        """
        Reset this add-on. Call this before resetting a scene.
        """

        super().reset()
        self._getting_model_names = True
        self.container_colliders.clear()
        self.containment.clear()
        self.tags.clear()
