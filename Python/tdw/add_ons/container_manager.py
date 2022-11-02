from typing import List, Dict
import numpy as np
from tdw.output_data import OutputData, StaticCompositeObjects, Containment
from tdw.add_ons.add_on import AddOn
from tdw.container_data.container_tag import ContainerTag
from tdw.container_data.containment_event import ContainmentEvent
from tdw.object_data.composite_object.composite_object_static import CompositeObjectStatic


class ContainerManager(AddOn):
    """
    Manage containment events for 'container' objects.

    'Containers' can be concave objects such as baskets but they don't have to be. For example, a table surface can be a 'container' and if another object is on that surface, the table is currently 'containing' that object.

    An object is 'contained' by a 'container' if it overlaps with a "containment" space, for example the interior of a pot.
    """

    def __init__(self):
        """
        (no parameters)
        """

        super().__init__()
        self._getting_static_data: bool = True
        """:field
        A dictionary describing which objects contain other objects on this frame. This is updated per-frame. Key = The container shape ID (not the object ID). Value = A list of [`ContainmentEvent`](../container_data/containment_event.md) data.
        """
        self.events: Dict[int, ContainmentEvent] = dict()
        """:field
        A dictionary of container shape IDs. Key = The container shape ID. Value = The object ID.
        """
        self.container_shapes: Dict[int, int] = dict()
        """:field
        Tags describing each container shape. Key = The container shape ID. Value = [`ContainerTag`](../container_data/container_tag.md).
        """
        self.tags: Dict[int, ContainerTag] = dict()
        self._excluded_objects: List[int] = list()

    def get_initialization_commands(self) -> List[dict]:
        return [{"$type": "send_static_composite_objects"},
                {"$type": "send_containment",
                 "frequency": "always"}]

    def on_send(self, resp: List[bytes]) -> None:
        # Get model names.
        if self._getting_static_data:
            self._getting_static_data = False
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                # Exclude composite sub-objects.
                if r_id == "scom":
                    static_composite_objects = StaticCompositeObjects(resp[i])
                    for j in range(static_composite_objects.get_num()):
                        s = CompositeObjectStatic(static_composite_objects, j)
                        self._excluded_objects.extend(s.sub_object_ids)
                    break
        self.events.clear()
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            # Use the model names from SegmentationColors output data to add container shapes.
            if r_id == "cont":
                containment = Containment(resp[i])
                container_id = containment.get_container_id()
                tag = containment.get_tag()
                # Add the shape.
                if container_id not in self.container_shapes:
                    self.container_shapes[container_id] = containment.get_object_id()
                    self.tags[container_id] = tag
                # Add the event.
                self.events[container_id] = ContainmentEvent(container_id=container_id,
                                                             object_ids=np.array([o_id for o_id in containment.get_overlap_ids()
                                                                                  if int(o_id) not in self._excluded_objects], dtype=int),
                                                             tag=tag)

    def reset(self) -> None:
        """
        Reset this add-on. Call this before resetting a scene.
        """

        self.initialized = False
        self.commands.clear()
        self._getting_static_data = True
        self.events.clear()
        self.tags.clear()
        self._excluded_objects.clear()
        self.container_shapes.clear()
