from typing import List, Dict, Optional, Union
import numpy as np
from tdw.cardinal_direction import CardinalDirection
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.librarian import ModelRecord, ModelLibrarian
from tdw.scene_data.room import Room
from tdw.scene_data.interior_region import InteriorRegion
from tdw.proc_gen.arrangements.table_and_chairs import TableAndChairs
from tdw.proc_gen.arrangements.table_setting import TableSetting


class KitchenTable(TableAndChairs):
    """
    A kitchen table has chairs and table settings.

    - The kitchen table model is chosen randomly; see `KitchenTable.MODEL_CATEGORIES["kitchen_table"]`.
      - The kitchen table's position is defined by center of the main region of a room; see `room` in the constructor.
      - If there are alcoves, the kitchen table will be positioned part way between the main room and the largest connecting alcove. The offset is random; see `KitchenTable.MIN_TABLE_ALCOVE_OFFSET_FACTOR` and `KitchenTable.MAX_TABLE_ALCOVE_OFFSET_FACTOR`.
      - The position of the kitchen table is perturbed randomly; see `KitchenTable.TABLE_POSITION_PERTURBATION`.
      - The rotation of the kitchen table is perturbed randomly; see `KITCHEN_TABLE_ROTATION`.
    - There are *n* chairs around the table.
      - All chairs are the same model. The chair model is chosen randomly; see `KitchenTable.MODEL_CATEGORIES["kitchen_chair"]`.
      - If the surface area of the table is greater than 0.9 square meters, there are 4 chairs. Otherwise, there are two chairs and they are placed on the shorter sides of the table.
      - The `used_walls` parameter defines which walls are "used". It is assumed that there are objects along these walls. If the wall is less than 2 meters away from the table, a chair _won't_ be added on that side of the table.
      - The position of the chair is offset randomly: `half_extent + random.uniform(-0.1, -0.05)`
      - The chairs face the center of the table and then their rotations are perturbed randomly; see `KitchenTable.CHAIR_ROTATION`.
    - For each chair, there is a [`TableSetting`](table_setting.md).
      - The table setting's position is set at the edge of the table and then moved inward by a random factor; see `KitchenTable.MIN_PLATE_OFFSET_FACTOR` and `KitchenTable.MAX_PLATE_OFFSET_FACTOR`.
      - The table setting's position is randomly perturbed; see `KitchenTable.PLATE_POSITION_PERTURBATION`.
    - Sometimes, if the table is big enough, there is a centerpiece; see `KitchenTable.CENTERPIECE_PROBABILITY` and `KitchenTable.MIN_AREA_FOR_CENTERPIECE`.
      - The centerpiece is a random model from a random category; see `KitchenTable.CENTERPIECE_CATEGORIES`.
      - The centerpiece is in the center of the table and then its position is perturbed randomly; see `KitchenTable.CENTERPIECE_POSITION_PERTURBATION`
      - The rotation of the centerpiece is random (0 to 360 degrees).
    """

    """:class_var
    The possible centerpiece categories.
    """
    CENTERPIECE_CATEGORIES: List[str] = ["jug", "vase", "bowl"]
    """:class_var
    The minimum offset of the plate from the edge of the table as a fraction of the table surface's extent.
    """
    MIN_PLATE_OFFSET_FACTOR: float = 0.65
    """:class_var
    The maximum offset of the plate from the edge of the table as a fraction of the table surface's extent.
    """
    MAX_PLATE_OFFSET_FACTOR: float = 0.7
    """:class_var
    Randomly perturb the (x, z) coordinates of each plate by up to +/- this distance.
    """
    PLATE_POSITION_PERTURBATION: float = 0.03
    """:class_var
    The table surface area must be greater than this for there to potentially be a centerpiece.
    """
    MIN_AREA_FOR_CENTERPIECE: float = 1.1
    """:class_var
    The probability (0 to 1) of adding a adding a centerpiece to a table.
    """
    CENTERPIECE_PROBABILITY: float = 0.75
    """:class_var
    Randomly perturb the (x, z) coordinates of the centerpiece by up to +/- this distance.
    """
    CENTERPIECE_POSITION_PERTURBATION: float = 0.1
    """:class_var
    Randomly perturb the (x, z) coordinates of the table by up to +/- this distance.
    """
    TABLE_POSITION_PERTURBATION: float = 0.1
    """:class_var
    If there is an alcove in the room, the table will be between the center of the main region and the center of the alcove at a random distance factor (0 to 1, with 0 being the center of the main region).
    """
    MIN_TABLE_ALCOVE_OFFSET_FACTOR: float = 0.35
    """:class_var
    If there is an alcove in the room, the table will be between the center of the main region and the center of the alcove at a random distance factor (0 to 1, with 0 being the center of the main region).
    """
    MAX_TABLE_ALCOVE_OFFSET_FACTOR: float = 0.65
    """:class_var
    The table will be rotated randomly up to +/- this many degrees.
    """
    TABLE_ROTATION: float = 2
    """:class_var
    The chairs will be rotated randomly up to +/- this many degrees with respect to their initial rotation (facing the table).
    """
    CHAIR_ROTATION: float = 10

    def __init__(self, room: Room, used_walls: int, model: Union[str, ModelRecord] = None,
                 offset_distance: float = 0.1, rng: Union[int, np.random.RandomState] = None):
        """
        :param room: The [`Room`] that the table is in.
        :param used_walls: Bitwise sum of walls with objects.
        :param model: Either the name of the model (in which case the model must be in `models_core.json`), or a `ModelRecord`, or None. If None, a random model in the category is selected.
        :param rng: Either a random seed or an `numpy.random.RandomState` object. If None, a new random number generator is created.
        :param offset_distance: Offset the position from the used walls by this distance.
        """

        if "models_core.json" not in Controller.MODEL_LIBRARIANS:
            Controller.MODEL_LIBRARIANS["models_core.json"] = ModelLibrarian()
        # Choose a random record.
        if model is None:
            if rng is None:
                rng = np.random.RandomState()
            category = self._get_category()
            if category not in TableAndChairs.MODEL_CATEGORIES:
                self._record: Optional[ModelRecord] = None
            else:
                model_names = TableAndChairs.MODEL_CATEGORIES[category]
                model_name = model_names[rng.randint(0, len(model_names))]
                self._record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(model_name)
        self._room: Room = room
        self._offset_distance: float = offset_distance
        super().__init__(used_walls=used_walls, region=room.main_region, model=model,
                         position={"x": 0, "y": 0, "z": 0}, rng=rng)

    def get_commands(self) -> List[dict]:
        commands = super().get_commands()
        top = {"x": self._position["x"],
               "y": self._record.bounds["top"]["y"],
               "z": self._position["z"]}
        # Add table settings.
        for bound_point in self._bound_point_positions:
            # Get the vector towards the center.
            v = np.array([bound_point[0], bound_point[2]]) * self._rng.uniform(KitchenTable.MIN_PLATE_OFFSET_FACTOR,
                                                                               KitchenTable.MAX_PLATE_OFFSET_FACTOR)
            # Get a slightly perturbed position for the plate.
            table_setting = TableSetting(position={"x": top["x"] + v[0] + self._rng.uniform(
                                             -KitchenTable.PLATE_POSITION_PERTURBATION,
                                             KitchenTable.PLATE_POSITION_PERTURBATION),
                                                   "y": top["y"],
                                                   "z": top["z"] + v[1] + self._rng.uniform(
                                                       -KitchenTable.PLATE_POSITION_PERTURBATION,
                                                       KitchenTable.PLATE_POSITION_PERTURBATION)},
                                         rng=self._rng)
            commands.extend(table_setting.get_commands())
            # Parent everything to the plate.
            for child_object_id in table_setting.object_ids:
                if child_object_id == table_setting.root_object_id:
                    continue
                commands.append({"$type": "parent_object_to_object",
                                 "parent_id": table_setting.root_object_id,
                                 "id": child_object_id})
            # Rotate the plate to look at the center of the table.
            commands.append({"$type": "object_look_at_position",
                             "position": top,
                             "id": table_setting.root_object_id})
            # Unparent everything.
            for child_object_id in table_setting.object_ids:
                if child_object_id == table_setting.root_object_id:
                    continue
                commands.append({"$type": "unparent_object",
                                 "id": child_object_id})
        # Add a centerpiece.
        table_extents = TDWUtils.get_bounds_extents(bounds=self._record.bounds)
        area = table_extents[0] * table_extents[2]
        if area > KitchenTable.MIN_AREA_FOR_CENTERPIECE and self._rng.random() < KitchenTable.CENTERPIECE_PROBABILITY:
            centerpiece_category = KitchenTable.CENTERPIECE_CATEGORIES[
                self._rng.randint(0, len(KitchenTable.CENTERPIECE_CATEGORIES))]
            centerpiece_model_name = KitchenTable.MODEL_CATEGORIES[centerpiece_category][
                self._rng.randint(0, len(KitchenTable.MODEL_CATEGORIES[centerpiece_category]))]
            object_id = Controller.get_unique_id()
            self.object_ids.append(object_id)
            commands.extend(Controller.get_add_physics_object(model_name=centerpiece_model_name,
                                                              object_id=object_id,
                                                              position={"x": top["x"] + float(self._rng.uniform(
                                                                  -KitchenTable.CENTERPIECE_POSITION_PERTURBATION,
                                                                  KitchenTable.CENTERPIECE_POSITION_PERTURBATION)),
                                                                        "y": top["y"],
                                                                        "z": top["z"] + float(self._rng.uniform(
                                                                            -KitchenTable.CENTERPIECE_POSITION_PERTURBATION,
                                                                            KitchenTable.CENTERPIECE_POSITION_PERTURBATION))},
                                                              rotation={"x": 0,
                                                                        "y": float(self._rng.uniform(0, 360)),
                                                                        "z": 0},
                                                              library="models_core.json"))
        return commands

    def _get_position(self, position: Dict[str, float]) -> Dict[str, float]:
        alcove: Optional[InteriorRegion] = None
        # The main region and a valid alcove must share a non-continuous wall.
        if len(self._room.alcoves) > 0:
            for a in self._room.alcoves:
                for c in CardinalDirection:
                    try:
                        d = c << 2
                    except ValueError:
                        d = c >> 2
                    if self._room.main_region.non_continuous_walls & c != 0 and a.non_continuous_walls & d != 0:
                        alcove = a
                        break
        # If there are no valid alcoves, the position is in the center offset from the used walls.
        if alcove is None:
            room_center = self._room.main_region.center
            pos = {"x": room_center[0] + self._rng.uniform(-KitchenTable.TABLE_POSITION_PERTURBATION,
                                                           KitchenTable.TABLE_POSITION_PERTURBATION),
                   "y": 0,
                   "z": room_center[2] + self._rng.uniform(-KitchenTable.TABLE_POSITION_PERTURBATION,
                                                           KitchenTable.TABLE_POSITION_PERTURBATION)}
            # Apply offsets.
            if self._used_walls & CardinalDirection.north != 0:
                pos["z"] -= self._offset_distance
            if self._used_walls & CardinalDirection.south != 0:
                pos["z"] += self._offset_distance
            if self._used_walls & CardinalDirection.east != 0:
                pos["x"] -= self._offset_distance
            if self._used_walls & CardinalDirection.west != 0:
                pos["x"] += self._offset_distance
        # Position the table between the main region and an alcove.
        else:
            p = (np.array(self._room.main_region.center) + np.array(alcove.center)) * self._rng.uniform(
                KitchenTable.MIN_TABLE_ALCOVE_OFFSET_FACTOR, KitchenTable.MAX_TABLE_ALCOVE_OFFSET_FACTOR)
            pos = {"x": p[0] + self._rng.uniform(-KitchenTable.TABLE_POSITION_PERTURBATION,
                                                 KitchenTable.TABLE_POSITION_PERTURBATION),
                   "y": 0,
                   "z": p[2] + self._rng.uniform(-KitchenTable.TABLE_POSITION_PERTURBATION,
                                                 KitchenTable.TABLE_POSITION_PERTURBATION)}
        return pos

    def _get_category(self) -> str:
        return "kitchen_table"

    def _get_rotation(self) -> float:
        return float(self._rng.uniform(-KitchenTable.TABLE_ROTATION, KitchenTable.TABLE_ROTATION))

    def _get_chair_rotation_range(self) -> float:
        return KitchenTable.CHAIR_ROTATION

    def _get_chair_category(self) -> str:
        return "kitchen_chair"
