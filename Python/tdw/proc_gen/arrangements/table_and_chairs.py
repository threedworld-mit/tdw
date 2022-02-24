from abc import ABC, abstractmethod
from typing import List, Dict
import numpy as np
from overrides import final
from tdw.cardinal_direction import CardinalDirection
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.librarian import ModelRecord
from tdw.scene_data.interior_region import InteriorRegion
from tdw.proc_gen.arrangements.arrangement_with_root_object import ArrangementWithRootObject


class TableAndChairs(ArrangementWithRootObject, ABC):
    """
    Abstract base class for a table with chairs around it.
    """

    def __init__(self, table_rotation_range: float, chair_rotation_range: float, used_walls: int,
                 region: InteriorRegion, record: ModelRecord, position: Dict[str, float], rng: np.random.RandomState):
        """
        :param table_rotation_range: The table will be randomly rotated up to +/- this angle in degrees. Can be 0.
        :param chair_rotation_range: The chairs will each be randomly rotated up to +/- this angle in degrees relative to the table. Can be 0.
        :param used_walls: Bitwise sum of walls with objects.
        :param region: The [`InteriorRegion`](../../scene_data/interior_region.md) that the table is in.
        :param record: The record of the root object.
        :param position: The position of the root object. This might be adjusted.
        :param rng: The random number generator.
        """

        self._used_walls: int = used_walls
        self._region: InteriorRegion = region
        self._table_rotation_range: float = table_rotation_range
        self._chair_rotation_range: float = chair_rotation_range
        super().__init__(record=record, position=position, rng=rng)

    def get_commands(self) -> List[dict]:
        commands = self._add_root_object()
        # Get positions for chairs.
        extents = TDWUtils.get_bounds_extents(bounds=self._record.bounds)
        area = extents[0] * extents[2]
        # Allow only two sides.
        if area < 0.9:
            if extents[0] > extents[2]:
                chair_directions = [CardinalDirection.east, CardinalDirection.west]
            else:
                chair_directions = [CardinalDirection.north, CardinalDirection.south]
        # Allow all four sides.
        else:
            chair_directions = [c for c in CardinalDirection]
        # Get a random chair model name.
        chairs = TableAndChairs.MODEL_CATEGORIES[self._get_chair_category()]
        chair_model_name: str = chairs[self._rng.randint(0, len(chairs))]
        chair_record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(chair_model_name)
        chair_positions: List[np.array] = list()
        tc = np.array([self._position["x"], self._position["z"]])
        for chair_direction in chair_directions:
            # Check if we're too close to a used wall.
            if self._used_walls & chair_direction != 0:
                if chair_direction == CardinalDirection.north:
                    cp = np.array([self._position["x"], self._region.z_max])
                elif chair_direction == CardinalDirection.south:
                    cp = np.array([self._position["x"], self._region.z_min])
                elif chair_direction == CardinalDirection.west:
                    cp = np.array([self._region.x_min, self._position["z"]])
                elif chair_direction == CardinalDirection.east:
                    cp = np.array([self._region.x_max, self._position["z"]])
                else:
                    raise Exception(chair_direction)
                cd = np.linalg.norm(tc - cp)
                # Add this side.
                if cd > 2:
                    chair_positions.append(self._get_chair_bound_position(cardinal_direction=chair_direction))
            else:
                chair_positions.append(self._get_chair_bound_position(cardinal_direction=chair_direction))
        pass
        # Add the chairs.
        for chair_bound_point in chair_positions:
            chair_position = self._get_chair_position(chair_record=chair_record,
                                                      table_bound_point=chair_bound_point)
            object_id = Controller.get_unique_id()
            # Add the chair.
            commands.extend(Controller.get_add_physics_object(model_name=chair_model_name,
                                                              position=TDWUtils.array_to_vector3(chair_position),
                                                              object_id=object_id,
                                                              library="models_core.json"))
            self.object_ids.append(object_id)
            # Look at the bottom-center and add a little rotation for spice.
            commands.extend([{"$type": "object_look_at_position",
                              "position": self._position,
                              "id": object_id},
                             {"$type": "rotate_object_by",
                              "angle": float(self._rng.uniform(-15, 15)),
                              "id": object_id,
                              "axis": "yaw"}])
        commands.extend(self._get_rotation_commands())
        return commands

    @abstractmethod
    def _get_chair_category(self) -> str:
        raise Exception()

    @final
    def _get_rotation(self) -> float:
        if self._table_rotation_range == 0:
            return 0
        else:
            return float(self._rng.uniform(-self._table_rotation_range, self._table_rotation_range))

    @final
    def _get_chair_bound_position(self, cardinal_direction: CardinalDirection) -> np.array:
        """
        :param cardinal_direction: The direction of the chair from the center of the table.

        :return: The position of the chair.
        """

        if cardinal_direction == CardinalDirection.north:
            side = "front"
        elif cardinal_direction == CardinalDirection.east:
            side = "right"
        elif cardinal_direction == CardinalDirection.south:
            side = "back"
        else:
            side = "left"
        return np.array([self._record.bounds[side]["x"] + self._position["x"],
                         0,
                         self._record.bounds[side]["z"] + self._position["z"]])

    @final
    def _get_chair_position(self, chair_record: ModelRecord, table_bound_point: np.array) -> np.array:
        """
        :param chair_record: The chair model record.
        :param table_bound_point: The bounds position.

        :return: A position for a chair around the table.
        """

        table_bottom = np.array(self._position)
        position_to_center = table_bound_point - table_bottom
        position_to_center_normalized = position_to_center / np.linalg.norm(position_to_center)
        # Scoot the chair back by half of its front-back extent.
        half_extent = TDWUtils.get_bounds_extents(bounds=chair_record.bounds)[2] / 2
        # Move the chair position back. Add some randomness for spice.
        chair_position = table_bound_point + (position_to_center_normalized *
                                              (half_extent + self.rng.uniform(-0.1, -0.05)))
        chair_position[1] = 0
        return chair_position
