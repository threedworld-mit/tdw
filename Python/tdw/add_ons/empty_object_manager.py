from typing import Dict, List, Tuple
import numpy as np
from tdw.add_ons.add_on import AddOn
from tdw.output_data import OutputData, StaticEmptyObjects, DynamicEmptyObjects


class EmptyObjectManager(AddOn):
    """
    A manager add-on for empty objects.

    In TDW, empty objects are typically used to set affordance points on objects, such as the handle of a coffee mug. These affordance points can then be targeted by agents.

    This add-on allows you to add your own empty objects to TDW objects and track their positions per `communicate()` call.
    """

    def __init__(self, empty_object_positions: Dict[int, List[dict]] = None):
        """
        :param empty_object_positions: A dictionary of empty object positions. Key = Parent object ID. Value = Positions relative to the parent object's bottom-center. Can be None.
        """

        super().__init__()
        """:field
        The positions of the empty objects. This is updated after every `communicate()` call. Key = Parent object ID. Value = Dictionary. Key = Empty object ID. Value = Empty object position as a numpy array, in world space coordinates.
        """
        self.empty_objects: Dict[int, Dict[int, np.ndarray]] = dict()
        # The positions of empty objects that the user is manually adding.
        self._empty_object_positions: Dict[int, List[dict]] = dict()
        if empty_object_positions is not None:
            self._empty_object_positions.update({k: v for k, v in empty_object_positions.items()})
        # A mapping of output data indices to object/empty object IDs.
        self._empty_object_indices: Dict[int, Tuple[int, int]] = dict()
        # A flag for caching static data.
        self._got_static_data: bool = False

    def get_initialization_commands(self) -> List[dict]:
        self._got_static_data = False
        commands = []
        for object_id in self._empty_object_positions:
            for i in range(len(self._empty_object_positions[object_id])):
                commands.append({"$type": "attach_empty_object",
                                 "position": self._empty_object_positions[object_id][i],
                                 "empty_object_id": i,
                                 "id": object_id})
        commands.extend([{"$type": "send_static_empty_objects",
                         "frequency": "once"},
                         {"$type": "send_dynamic_empty_objects",
                         "frequency": "always"}])
        return commands

    def on_send(self, resp: List[bytes]) -> None:
        if not self._got_static_data:
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                if r_id == "stem":
                    static_empty_objects = StaticEmptyObjects(resp[i])
                    for j in range(static_empty_objects.get_num()):
                        object_id = static_empty_objects.get_object_id(j)
                        empty_object_id = static_empty_objects.get_empty_object_id(j)
                        # Remember this object ID.
                        if object_id not in self.empty_objects:
                            self.empty_objects[object_id] = dict()
                        # Remember the indices.
                        self._empty_object_indices[j] = (object_id, empty_object_id)
                    break
                self._got_static_data = True
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "dyem":
                dynamic_empty_objects = DynamicEmptyObjects(resp[i])
                for j in range(dynamic_empty_objects.get_num()):
                    # Convert the index to object IDs.
                    ids = self._empty_object_indices[j]
                    # Store the position.
                    self.empty_objects[ids[0]][ids[1]] = dynamic_empty_objects.get_position(j)

    def reset(self, empty_object_positions: Dict[int, List[dict]] = None) -> None:
        """
        Reset the add-on.

        :param empty_object_positions: A dictionary of empty object positions. Key = Parent object ID. Value = Positions relative to the parent object's bottom-center. Can be None.
        """

        self.empty_objects.clear()
        self.initialized = False
        self._got_static_data = False
        self._empty_object_positions.clear()
        self._empty_object_indices.clear()
        if empty_object_positions is not None:
            self._empty_object_positions.update({k: v for k, v in empty_object_positions.items()})
