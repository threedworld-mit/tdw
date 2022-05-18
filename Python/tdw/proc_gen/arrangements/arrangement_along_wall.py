from typing import List, Dict, Union, Optional
from abc import ABC, abstractmethod
from overrides import final
import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.proc_gen.arrangements.arrangement_with_root_object import ArrangementWithRootObject
from tdw.scene_data.interior_region import InteriorRegion
from tdw.cardinal_direction import CardinalDirection
from tdw.ordinal_direction import OrdinalDirection
from tdw.librarian import ModelRecord, ModelLibrarian


class ArrangementAlongWall(ArrangementWithRootObject, ABC):
    """
    Abstract class procedurally-generated spatial arrangements of objects that are positioned alongside a wall as part of a lateral arrangement.

    Rather than supplying a position and rotation for the object, the arrangement is placed at a `distance` from a `corner` along a `wall` in a `region` and then rotated so that it faces away from the wall.
    """

    def __init__(self, corner: OrdinalDirection, wall: CardinalDirection, distance: float, region: InteriorRegion,
                 model: Union[str, ModelRecord] = None, wall_length: float = None, rng: Union[int, np.random.RandomState] = None):
        """
        :param wall: The wall as a [`CardinalDirection`](../../cardinal_direction.md) that the root object is next to.
        :param corner: The origin [`OrdinalDirection`](../../ordinal_direction.md) of this wall. This is used to derive the direction.
        :param distance: The distance in meters from the corner along the derived direction.
        :param region: The [`InteriorRegion`](../../scene_data/interior_region.md) that the object is in.
        :param model: Either the name of the model (in which case the model must be in `models_core.json`), or a `ModelRecord`, or None. If None, a model that fits along the wall at `distance` is randomly selected. If no model fits, the arrangement will not be added to the scene.
        :param wall_length: The total length of the lateral arrangement. If None, defaults to the length of the wall.
        :param rng: Either a random seed or an `numpy.random.RandomState` object. If None, a new random number generator is created.
        """

        self._corner: OrdinalDirection = corner
        self._wall: CardinalDirection = wall
        self._direction: CardinalDirection = TDWUtils.get_direction_from_corner(corner=corner, wall=self._wall)
        self._distance: float = distance
        self._region: InteriorRegion = region
        if wall_length is None:
            self._wall_length: float = self._region.get_length(side=self._wall)
        else:
            self._wall_length = wall_length
        """:field
        If True, send commands when `self.get_commands()` is called. If False, `self.get_commands()` will return an empty list.
        """
        self.send_commands: bool = distance < self._wall_length
        if model is None:
            if rng is None:
                self._rng: np.random.RandomState = np.random.RandomState()
            elif isinstance(rng, int):
                self._rng = np.random.RandomState(rng)
            elif isinstance(rng, np.random.RandomState):
                self._rng = rng
            else:
                raise Exception(rng)
            model = self._get_random_record_that_fits_along_wall(distance=distance)
        super().__init__(model=model, position={"x": 0, "y": 0, "z": 0}, rng=rng)

    @final
    def _get_random_record_that_fits_along_wall(self, distance: float) -> Optional[ModelRecord]:
        """
        :param distance: The distance from the starting position.

        :return: A random model record that fits along the wall. Can be None.
        """

        if not self.send_commands:
            return None
        possible_records = []
        model_library = self._get_model_library()
        for model_name in self._get_model_names():
            # Set the record.
            if model_library not in Controller.MODEL_LIBRARIANS:
                Controller.MODEL_LIBRARIANS[model_library] = ModelLibrarian(model_library)
            self._record = Controller.MODEL_LIBRARIANS[model_library].get_record(model_name)
            # This record fits.
            if distance + self.get_length() < self._wall_length:
                possible_records.append(self._record)
        # There is no record.
        if len(possible_records) == 0:
            self.send_commands = False
            return None
        # Choose a random record.
        else:
            return possible_records[self._rng.randint(0, len(possible_records))]

    def _get_position(self, position: Dict[str, float]) -> Dict[str, float]:
        """
        :param position: The non-adjusted position.

        :return: The adjusted position along the wall.
        """

        return self._get_position_along_wall()

    def _get_model_names(self) -> List[str]:
        """
        :return: A list of possible model names.
        """

        return ArrangementAlongWall.MODEL_CATEGORIES[self._get_category()]

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

    @final
    def _get_position_along_wall(self) -> Dict[str, float]:
        """
        :return: The position along the `wall` in the `region` at `distance` meters from the `corner`.
        """

        depth = self._get_depth()
        length = self.get_length()
        # Get the position at the origin corner plus the depth offset.
        if self._wall == CardinalDirection.north:
            z = self._region.z_max - depth / 2
            if self._corner == OrdinalDirection.northeast:
                x = self._region.x_max
            elif self._corner == OrdinalDirection.northwest:
                x = self._region.x_min
            else:
                raise Exception(f"Invalid corner: {self._corner}")
        elif self._wall == CardinalDirection.south:
            z = self._region.z_min + depth / 2
            if self._corner == OrdinalDirection.southeast:
                x = self._region.x_max
            elif self._corner == OrdinalDirection.southwest:
                x = self._region.x_min
            else:
                raise Exception(f"Invalid corner: {self._corner}")
        elif self._wall == CardinalDirection.west:
            x = self._region.x_min + depth / 2
            if self._corner == OrdinalDirection.northwest:
                z = self._region.z_max
            elif self._corner == OrdinalDirection.southwest:
                z = self._region.z_min
            else:
                raise Exception(f"Invalid corner: {self._corner}")
        elif self._wall == CardinalDirection.east:
            x = self._region.x_max - depth / 2
            if self._corner == OrdinalDirection.northeast:
                z = self._region.z_max
            elif self._corner == OrdinalDirection.southeast:
                z = self._region.z_min
            else:
                raise Exception(f"Invalid corner: {self._corner}")
        else:
            raise Exception(self._wall)
        # Get the distance offset.
        pos = {"x": x, "y": 0, "z": z}
        distance = self._distance + length / 2
        direction = TDWUtils.get_direction_from_corner(corner=self._corner, wall=self._wall)
        if direction == CardinalDirection.north:
            pos["z"] += distance
        elif direction == CardinalDirection.south:
            pos["z"] -= distance
        elif direction == CardinalDirection.west:
            pos["x"] -= distance
        elif direction == CardinalDirection.east:
            pos["x"] += distance
        else:
            raise Exception(direction)
        return pos
