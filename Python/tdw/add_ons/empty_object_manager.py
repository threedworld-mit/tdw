from typing import List, Dict
import numpy as np
from tdw.add_ons.add_on import AddOn
from tdw.output_data import OutputData, SegmentationColors, EmptyObjects
from tdw.librarian import ModelLibrarian
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils


class EmptyObjectManager(AddOn):
    """
    A manager add-on that automatically adds empty objects to parent objects based on model record metadata.
    """

    def __init__(self):
        """
        (no parameters)
        """

        super().__init__()
        # Add the model librarians.
        for library_path in ModelLibrarian.get_library_filenames():
            if library_path not in Controller.MODEL_LIBRARIANS:
                Controller.MODEL_LIBRARIANS[library_path] = ModelLibrarian(library_path)
        self._added_empty_objects: bool = False
        """:field
        A dictionary of empty object IDs. Key = The parent object ID. Value = A list of empty object IDs.
        """
        self.empty_object_ids: Dict[int, List[int]] = dict()
        """:field
        A dictionary of empty object positions. Key = The empty object ID. Value = The position as a numpy array.
        """
        self.empty_object_positions: Dict[int, np.ndarray] = dict()

    def get_initialization_commands(self) -> List[dict]:
        return [{"$type": "send_segmentation_colors"}]

    def on_send(self, resp: List[bytes]) -> None:
        # Add empty objects.
        if not self._added_empty_objects:
            self._added_empty_objects = True
            empty_object_id = 0
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                # Get the names and IDs of each object.
                if r_id == "segm":
                    segmentation_colors = SegmentationColors(resp[i])
                    for j in range(segmentation_colors.get_num()):
                        object_id = segmentation_colors.get_object_id(j)
                        model_name = segmentation_colors.get_object_name(j).lower()
                        for library in Controller.MODEL_LIBRARIANS:
                            record = Controller.MODEL_LIBRARIANS[library].get_record(model_name)
                            # Got the model record.
                            if record is not None:
                                for affordance_position in record.affordance_points:
                                    # Add an empty object.
                                    self.commands.append({"$type": "attach_empty_object",
                                                          "id": object_id,
                                                          "empty_object_id": empty_object_id,
                                                          "position": affordance_position})
                                    self.empty_object_positions[empty_object_id] = TDWUtils.vector3_to_array(affordance_position)
                                    # Update the dictionary of empty object IDs.
                                    if object_id not in self.empty_object_ids:
                                        self.empty_object_ids[object_id] = list()
                                    self.empty_object_ids[object_id].append(empty_object_id)
                                    # Increment the next ID.
                                    empty_object_id += 1
                                break
                    # We only need SegmentationColors data.
                    break
            # Request empty objects data per frame.
            self.commands.append({"$type": "send_empty_objects",
                                  "frequency": "always"})
        # Update the positions of each empty object.
        self.empty_object_positions.clear()
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "empt":
                empty_objects = EmptyObjects(resp[i])
                for j in range(empty_objects.get_num()):
                    self.empty_object_positions[empty_objects.get_id(j)] = empty_objects.get_position(j)

    def reset(self) -> None:
        """
        Reset this add-on.
        """

        self.initialized = False
        self.empty_object_ids.clear()
        self.empty_object_positions.clear()
        self._added_empty_objects = False
