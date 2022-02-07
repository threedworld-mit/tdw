from json import loads
from pkg_resources import resource_filename
from pathlib import Path
from typing import List, Dict
from tdw.output_data import OutputData, SegmentationColors
from tdw.add_ons.trigger_collision_listener import TriggerCollisionListener


class ContainerManager(TriggerCollisionListener):
    """
    Manage trigger collisions for 'container' objects.

    This add-on assigns trigger collisions based on a pre-defined dictionary of models and collider shapes, positions, etc. There are many models in TDW that could be containers but haven't been added to this dictionary yet. See: `ContainerManager.CONTAINERS`.

    'Containment' doesn't imply a concave object such as a basket. For example, a table surface can be a 'container' and if another object is on that surface, the table is currently 'containing' that object.
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
        A dictionary describing which objects contain other objects on this frame. This is updated per-frame. Key = The container ID *(not the trigger ID)*. Value = A list of object IDs contained by the container.
        """
        self.containment: Dict[int, List[int]] = dict()

    def get_initialization_commands(self) -> List[dict]:
        return [{"$type": "send_segmentation_colors"}]

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
                                    self.add_box_collider(object_id=object_id, position=collider["position"],
                                                          scale=collider["scale"])
                            if "sphere" in ContainerManager.CONTAINERS[model_name]:
                                for collider in ContainerManager.CONTAINERS[model_name]["sphere"]:
                                    self.add_sphere_collider(object_id=object_id, position=collider["position"],
                                                             diameter=collider["diameter"])
        super().on_send(resp=resp)
        # Get containment.
        self.containment.clear()
        for trigger_collision in self.collisions:
            # This trigger collision involved a container trigger collider and an enter or stay event.
            # Therefore, the container contains the collider object.
            if trigger_collision.trigger_id in self.container_colliders and \
                    (trigger_collision.state == "enter" or trigger_collision.state == "stay"):
                if trigger_collision.collidee_id not in self.containment:
                    self.containment[trigger_collision.collidee_id] = list()
                if trigger_collision.collider_id not in self.containment[trigger_collision.collidee_id]:
                    self.containment[trigger_collision.collidee_id].append(trigger_collision.collider_id)

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
