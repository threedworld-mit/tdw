from typing import Dict, List
from tdw.add_ons.add_on import AddOn
from tdw.object_data.composite_object.composite_object_static import CompositeObjectStatic
from tdw.object_data.composite_object.composite_object_dynamic import CompositeObjectDynamic
from tdw.output_data import OutputData, DynamicCompositeObjects, StaticCompositeObjects


class CompositeObjectManager(AddOn):
    """
    Manager add-on for static and dynamic composite object data.

    Note that some useful information, such as the positions, rotations, names, of the objects, is not included here. See: [`ObjectManager`](object_manager.md).
    """

    def __init__(self):
        """
        (no parameters)
        """

        super().__init__()
        """:field
        A dictionary of [`CompositeObjectStatic`](../object_data/composite_object/composite_object_static.md) data that is set when this add-on intializes. Key = The object ID.
        """
        self.static: Dict[int, CompositeObjectStatic] = dict()
        """:field
        A dictionary of [`CompositeObjectDynamic`](../object_data/composite_object/composite_object_dynamic.md) data that is set per-frame. Key = The object ID.
        """
        self.dynamic: Dict[int, CompositeObjectDynamic] = dict()

    def get_initialization_commands(self) -> List[dict]:
        return [{"$type": "send_static_composite_objects"},
                {"$type": "send_dynamic_composite_objects",
                 "frequency": "always"}]

    def on_send(self, resp: List[bytes]) -> None:
        self.dynamic.clear()
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            # Cache static data.
            if r_id == "scom":
                static_composite_objects = StaticCompositeObjects(resp[i])
                for j in range(static_composite_objects.get_num()):
                    o = CompositeObjectStatic(static_composite_objects=static_composite_objects, object_index=j)
                    self.static[o.object_id] = o
            elif r_id == "dcom":
                dynamic_composite_objects = DynamicCompositeObjects(resp[i])
                for j in range(dynamic_composite_objects.get_num()):
                    o = CompositeObjectDynamic(dynamic_composite_objects=dynamic_composite_objects, object_index=j)
                    self.dynamic[o.object_id] = o

    def is_open(self, object_id: int, sub_object_id: int, open_at: float = 30) -> bool:
        """
        :param object_id: The ID of the root object.
        :param sub_object_id: The ID of one of the root object's hinges, motors, or springs.
        :param open_at: A threshold of 'openness' in degrees. If the sub-object's angle is greater than or equal to this, it is considered 'open'.

        :return: True if the hinge, motor, or spring is open.
        """

        return self.dynamic[object_id].hinges[sub_object_id].angle >= open_at

    def reset(self) -> None:
        """
        Reset this add-on. Call this when resetting the scene.
        """

        self.initialized = False
        self.static.clear()
        self.dynamic.clear()
