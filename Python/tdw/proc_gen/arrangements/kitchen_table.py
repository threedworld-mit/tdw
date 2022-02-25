from typing import List, Dict, Optional, Union
import numpy as np
from tdw.cardinal_direction import CardinalDirection
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.librarian import ModelRecord
from tdw.scene_data.room import Room
from tdw.scene_data.interior_region import InteriorRegion
from tdw.proc_gen.arrangements.table_and_chairs import TableAndChairs
from tdw.proc_gen.arrangements.table_setting import TableSetting


class KitchenTable(TableAndChairs):
    """
    A kitchen table has chairs and table settings.

    - The kitchen table model is chosen randomly; see `KitchenTable.MODEL_CATEGORIES["kitchen_table"]`.
      - The kitchen table's position is defined by center of the main region of a room; see `room` in the constructor.
      - If there are alcoves, the kitchen table will be positioned part way between the main room and the largest connecting alcove. The offset is random: `((main_region_position + alcove_region_position) * random.uniform(0.35, 0.65))`
      - The position of the kitchen table is perturbed randomly (-0.1 to 0.1 meters).
      - The rotation of the kitchen table is perturbed randomly (-2 to 2 degrees).
    - There are *n* chairs around the table.
      - All chairs are the same model. The chair model is chosen randomly; see `KitchenTable.MODEL_CATEGORIES["kitchen_chair"]`.
      - If the surface area of the table is greater than 0.9 square meters, there are 4 chairs. Otherwise, there are two chairs and they are placed on the shorter sides of the table.
      - The `used_walls` parameter defines which walls are "used". It is assumed that there are objects along these walls. If the wall is less than 2 meters away from the table, a chair _won't_ be added on that side of the table.
      - The position of the chair is offset randomly: `half_extent + random.uniform(-0.1, -0.05)`
      - The chairs face the center of the table and then their rotations are perturbed randomly (-10 to 10 degrees).
    - For each chair, there is a [`TableSetting`](table_setting.md).
    - 75% of the time, if the surface area of the table is greater than 1.1 square meters, there is a centerpiece.
      - The centerpiece is a random model from a random category; see `KitchenTable.CENTERPIECE_CATEGORIES`.
      - The centerpiece is in the center of the table and then its position is perturbed randomly (-0.1 to 0.1 meters)
      - The rotation of the centerpiece is random.
    """

    """:class_var
    The possible centerpiece categories.
    """
    CENTERPIECE_CATEGORIES: List[str] = ["jug", "vase", "bowl"]

    def __init__(self, room: Room, used_walls: int,  model: Union[str, ModelRecord], position: Dict[str, float],
                 rng: np.random.RandomState, offset_distance: float = 0.1, plate_record: Optional[ModelRecord] = None,
                 food_probability: float = 0.7):
        """
        :param room: The [`Room`] that the table is in.
        :param used_walls: Bitwise sum of walls with objects.
        :param model: Either the name of the model (in which case the model must be in `models_core.json` or a `ModelRecord`.
        :param position: The position of the root object. This might be adjusted.
        :param rng: The random number generator.
        :param offset_distance: Offset the position from the used walls by this distance.
        :param plate_record: The model record for the plate. If None, defaults to plate06.
        :param food_probability: The probability that each plate will have food (0 to 1).
        """

        self._room: Room = room
        self._offset_distance: float = offset_distance
        if plate_record is None:
            self._plate_record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record("plate06")
        else:
            self._plate_record = plate_record
        self._food_probability = food_probability
        super().__init__(used_walls=used_walls, region=room.main_region, model=model, position=position, rng=rng)

    def get_commands(self) -> List[dict]:
        commands = super().get_commands()
        top = {"x": self._position["x"],
               "y": self._record.bounds["top"]["y"],
               "z": self._position["z"]}
        # Add table settings.
        for bound_point in self._bound_point_positions:
            # Get the vector towards the center.
            v = np.array([bound_point[0], bound_point[2]]) - np.array([top["x"], top["z"]])
            # Get the normalized direction.
            v = v / np.linalg.norm(v)
            # Move the plates inward.
            v *= -float(self._rng.uniform(0.15, 0.2))
            # Get a slightly perturbed position for the plate.
            table_setting = TableSetting(food_probability=self._food_probability,
                                         position={"x": float(top["x"] + v[0] + self._rng.uniform(-0.03, 0.03)),
                                                   "y": top["y"],
                                                   "z": float(top["z"] + v[1] + self._rng.uniform(-0.03, 0.03))},
                                         record=self._plate_record,
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
        if area > 1.1 and self._rng.random() < 0.75:
            centerpiece_category = KitchenTable.CENTERPIECE_CATEGORIES[self._rng.randint(0, len(KitchenTable.CENTERPIECE_CATEGORIES))]
            centerpiece_model_name = KitchenTable.MODEL_CATEGORIES[centerpiece_category][self._rng.randint(0, len(KitchenTable.MODEL_CATEGORIES[centerpiece_category]))]
            object_id = Controller.get_unique_id()
            self.object_ids.append(object_id)
            commands.extend(Controller.get_add_physics_object(model_name=centerpiece_model_name,
                                                              object_id=object_id,
                                                              position={"x": top["x"] + float(self._rng.uniform(-0.1, 0.1)),
                                                                        "y": top["y"],
                                                                        "z": top["z"] + float(self._rng.uniform(-0.1, 0.1))},
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
            pos = {"x": room_center[0] + self._rng.uniform(-0.1, 0.1),
                   "y": 0,
                   "z": room_center[2] + self._rng.uniform(-0.1, 0.1)}
            # Apply offsets.
            if CardinalDirection.north in self._used_walls:
                pos["z"] -= self._offset_distance
            if CardinalDirection.south in self._used_walls:
                pos["z"] += self._offset_distance
            if CardinalDirection.east in self._used_walls:
                pos["x"] -= self._offset_distance
            if CardinalDirection.west in self._used_walls:
                pos["x"] += self._offset_distance
        # Position the table between the main region and an alcove.
        else:
            p = (np.array(self._room.main_region.center) + np.array(alcove.center)) * self._rng.uniform(0.35, 0.65)
            pos = {"x": p[0] + self._rng.uniform(-0.1, 0.1),
                   "y": 0,
                   "z": p[2] + self._rng.uniform(-0.1, 0.1)}
        return pos

    def _get_category(self) -> str:
        return "kitchen_table"

    def _get_rotation(self) -> float:
        return float(self._rng.uniform(-2, 2))

    def _get_chair_rotation_range(self) -> float:
        return 10

    def _get_chair_category(self) -> str:
        return "kitchen_chair"
