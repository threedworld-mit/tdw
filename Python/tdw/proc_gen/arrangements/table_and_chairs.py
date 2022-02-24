from abc import ABC, abstractmethod
from typing import List, Dict
import numpy as np
from tdw.cardinal_direction import CardinalDirection
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.librarian import ModelRecord
from tdw.scene_data.interior_region import InteriorRegion
from tdw.proc_gen.arrangements.arrangement_with_root_object import ArrangementWithRootObject


class TableAndChairs(ArrangementWithRootObject, ABC):
    def __init__(self, used_walls: int, region: InteriorRegion, record: ModelRecord, position: Dict[str, float], rng: np.random.RandomState):
        """
        :param used_walls: Bitwise sum of walls with objects.
        :param region: The region that the table is in.
        :param record: The record of the root object.
        :param position: The position of the root object. This might be adjusted.
        :param rng: The random number generator.
        """

        self._used_walls: int = used_walls
        self._region: InteriorRegion = region
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
                # Remove this side.
                if cd < 2:
                    chair_positions.append(self._get_chair_position(cardinal_direction=chair_direction))
            else:
                chair_positions.append(self._get_chair_position(cardinal_direction=chair_direction))

    @abstractmethod
    def _get_chair_category(self) -> str:
        raise Exception()

    def _get_chair_position(self, cardinal_direction: CardinalDirection) -> np.array:
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
