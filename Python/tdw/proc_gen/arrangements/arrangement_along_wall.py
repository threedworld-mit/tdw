from typing import List, Dict, Union, Optional
from abc import ABC, abstractmethod
import numpy as np
from tdw.controller import Controller
from tdw.proc_gen.proc_gen_utils import ProcGenUtils
from tdw.proc_gen.arrangements.arrangement_with_root_object import ArrangementWithRootObject
from tdw.scene_data.interior_region import InteriorRegion
from tdw.cardinal_direction import CardinalDirection
from tdw.ordinal_direction import OrdinalDirection
from tdw.librarian import ModelRecord


class ArrangementAlongWall(ArrangementWithRootObject, ABC):
    """
    A procedurally-generated spatial arrangement of objects that is positioned alongside a wall.
    """

    def __init__(self, corner: OrdinalDirection, wall: CardinalDirection, distance: float, region: InteriorRegion,
                 model: Union[str, ModelRecord] = None, wall_length: float = None, rng: np.random.RandomState = None):
        """
        :param wall: The wall as a [`CardinalDirection`](../../cardinal_direction.md) that the root object is next to.
        :param corner: The origin [`Corner`](../../corner.md) of this wall. This is used to derive the direction.
        :param distance: The distance in meters from the corner along the derived direction.
        :param region: The [`InteriorRegion`](../../scene_data/interior_region.md) that the object is in.
        :param model: Either the name of the model (in which case the model must be in `models_core.json`, or a `ModelRecord`, or None. If None, a model that fits along the wall at `distance` is randomly selected.
        :param wall_length: The total length of the lateral arrangement. If None, defaults to the length of the wall.
        :param rng: The random number generator. If None, a new random number generator is created.
        """

        self._corner: OrdinalDirection = corner
        self._wall: CardinalDirection = wall
        self._direction: CardinalDirection = ProcGenUtils.get_direction_from_corner(corner=corner, wall=self._wall)
        self._distance: float = distance
        self._region: InteriorRegion = region
        if wall_length is None:
            self._wall_length: float = self._region.get_length(side=self._wall)
        else:
            self._wall_length = wall_length
        if model is None:
            if rng is None:
                rng = np.random.RandomState()
            model = self._get_random_record_that_fits_along_wall(distance=distance)
        super().__init__(model=model, position={"x": 0, "y": 0, "z": 0}, rng=rng)

    def get_commands(self) -> List[dict]:
        if self._record is None:
            return []
        else:
            return self._get_commands()

    def _get_random_record_that_fits_along_wall(self, distance: float) -> Optional[ModelRecord]:
        """
        :param distance: The distance from the starting position.

        :return: A random model record that fits along the wall. Can be None.
        """

        possible_records = []
        for model_name in self._get_model_names():
            # Set the record.
            self._record = Controller.MODEL_LIBRARIANS["models_core.json"].get_record(model_name)
            # This record fits.
            if distance + self.get_length() / 2 < self._wall_length:
                possible_records.append(self._record)
        # There is no record.
        if len(possible_records) == 0:
            return None
        # Choose a random record.
        else:
            return possible_records[self._rng.randint(0, len(possible_records))]

    def _get_position(self, position: Dict[str, float]) -> Dict[str, float]:
        """
        :param position: The non-adjusted position.

        :return: The adjusted position along the wall.
        """

        return ProcGenUtils.get_position_along_wall(length=self.get_length(), depth=self._get_depth(),
                                                    corner=self._corner, wall=self._wall, distance=self._distance,
                                                    region=self._region)

    def _get_model_names(self) -> List[str]:
        """
        :return: A list of possible model names.
        """

        return ArrangementAlongWall.MODEL_CATEGORIES[self._get_category()]

    @abstractmethod
    def _get_commands(self) -> List[dict]:
        """
        :return: A list of commands that will create the arrangement.
        """
        raise Exception()

    @abstractmethod
    def get_length(self) -> float:
        """
        :return: The lateral extent of the object.
        """

        raise Exception()

    @abstractmethod
    def _get_depth(self) -> float:
        """
        :return: The depth extent of the object.
        """

        raise Exception()
