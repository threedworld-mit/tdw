from abc import ABC, abstractmethod
from typing import List, Dict, Union
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

    """:class_var
    The minimum surface area required for four chairs; below this, there are only two chairs.
    """
    AREA_FOUR_CHAIRS: float = 0.9
    """:class_var
    The minimum distace from a "used wall" at which a chair can be placed.
    """
    MIN_CHAIR_DISTANCE_FROM_USED_WALL: float = 2
    """:class_var
    The minimum random offset of a chair from the edge of the table.
    """
    MIN_CHAIR_OFFSET: float = -0.02
    """:class_var
    The minimum random offset of a chair from the edge of the table.
    """
    MAX_CHAIR_OFFSET: float = -0.01

    def __init__(self, used_walls: int, region: InteriorRegion, model: Union[str, ModelRecord],
                 position: Dict[str, float], rng: Union[int, np.random.RandomState] = None):
        """
        :param used_walls: Bitwise sum of walls with objects.
        :param region: The [`InteriorRegion`](../../scene_data/interior_region.md) that the table is in.
        :param model: Either the name of the model (in which case the model must be in `models_core.json` or a `ModelRecord`.
        :param position: The position of the root object. This might be adjusted.
        :param rng: Either a random seed or an `numpy.random.RandomState` object. If None, a new random number generator is created.
        """

        self._used_walls: int = used_walls
        self._region: InteriorRegion = region
        self._bound_point_positions: List[np.array] = list()
        super().__init__(model=model, position=position, rng=rng)

    def get_commands(self) -> List[dict]:
        commands = self._add_root_object()
        # Get positions for chairs.
        extents = TDWUtils.get_bounds_extents(bounds=self._record.bounds)
        area = extents[0] * extents[2]
        # Allow only two sides.
        if area < TableAndChairs.AREA_FOUR_CHAIRS:
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
                if cd > TableAndChairs.MIN_CHAIR_DISTANCE_FROM_USED_WALL:
                    self._bound_point_positions.append(self._get_chair_bound_position(cardinal_direction=chair_direction))
            else:
                self._bound_point_positions.append(self._get_chair_bound_position(cardinal_direction=chair_direction))
        # Add the chairs.
        rotation_range = self._get_chair_rotation_range()
        for chair_bound_point in self._bound_point_positions:
            chair_position = self._get_chair_position(chair_record=chair_record,
                                                      table_bound_point=chair_bound_point)
            object_id = Controller.get_unique_id()
            # Add the chair.
            commands.extend(Controller.get_add_physics_object(model_name=chair_model_name,
                                                              position=TDWUtils.array_to_vector3(chair_position),
                                                              object_id=object_id,
                                                              library="models_core.json"))
            self.object_ids.append(object_id)
            if rotation_range == 0:
                rotation = 0
            else:
                rotation = float(self._rng.uniform(-rotation_range, rotation_range))
            # Look at the bottom-center and add a little rotation for spice.
            commands.extend([{"$type": "object_look_at_position",
                              "position": self._position,
                              "id": object_id},
                             {"$type": "rotate_object_by",
                              "angle": rotation,
                              "id": object_id,
                              "axis": "yaw"}])
        commands.extend(self._get_rotation_commands())
        return commands

    @abstractmethod
    def _get_chair_category(self) -> str:
        """
        :return: The category of the chair models.
        """

        raise Exception()

    @abstractmethod
    def _get_chair_rotation_range(self) -> float:
        """
        :return: The range in rotation in degrees that the chairs can be rotated relative to the table.
        """

        raise Exception()

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

        table_bottom = TDWUtils.vector3_to_array(self._position)
        position_to_center = table_bound_point - table_bottom
        position_to_center_normalized = position_to_center / np.linalg.norm(position_to_center)
        # Scoot the chair back by half of its front-back extent.
        half_extent = TDWUtils.get_bounds_extents(bounds=chair_record.bounds)[2] / 2
        # Move the chair position back. Add some randomness for spice.
        chair_position = table_bound_point + (position_to_center_normalized *
                                              (half_extent + self._rng.uniform(TableAndChairs.MIN_CHAIR_OFFSET,
                                                                               TableAndChairs.MAX_CHAIR_OFFSET)))
        chair_position[1] = 0
        return chair_position
