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
    CONTAINERS: dict = loads(Path(resource_filename(__name__, "container_manager_data/colliders.json").read_text()))

    def __init__(self):
        super().__init__()
        self._getting_model_names: bool = True
        """:field
        A dictionary of trigger colliders used for containers. Key = The object ID. Value = A list of trigger collider IDs.
        """
        self.container_trigger_colliders:  Dict[int, List[int]] = dict()

    def get_initialization_commands(self) -> List[dict]:
        self._getting_model_names = True
        self.container_trigger_colliders.clear()
        return [{"$type": "send_segmentation_colors"}]

    def on_send(self, resp: List[bytes]) -> None:
        # Get model names.
        if self._getting_model_names:
            self._getting_model_names = False
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
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

    def _add_trigger_collider(self, object_id: int, position: Dict[str, float], scale: Dict[str, float],
                              rotation: Dict[str, float], shape: str, trigger_id: int = None) -> int:
        trigger_id = super()._add_trigger_collider(object_id=object_id, position=position, scale=scale,
                                                   rotation=rotation, shape=shape, trigger_id=trigger_id)
        # Add the trigger collider to the container collider dictionary.
        if object_id not in self.container_trigger_colliders:
            self.container_trigger_colliders[object_id] = list()
        self.trigger_colliders[object_id].append(trigger_id)
        return trigger_id
