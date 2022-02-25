from typing import Dict, Union
from abc import ABC, abstractmethod
import numpy as np
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
                 model: Union[str, ModelRecord], rng: np.random.RandomState):
        """
        :param wall: The wall as a [`CardinalDirection`](../../cardinal_direction.md) that the root object is next to.
        :param corner: The origin [`Corner`](../../corner.md) of this wall. This is used to derive the direction.
        :param distance: The distance in meters from the corner along the derived direction.
        :param region: The [`InteriorRegion`](../../scene_data/interior_region.md) that the object is in.
        :param model: Either the name of the model (in which case the model must be in `models_core.json` or a `ModelRecord`.
        :param rng: The random number generator.
        """

        self._corner: OrdinalDirection = corner
        self._wall: CardinalDirection = wall
        self._direction: CardinalDirection = ProcGenUtils.get_direction_from_corner(corner=corner, wall=self._wall)
        self._distance: float = distance
        self._region: InteriorRegion = region
        super().__init__(model=model, position={"x": 0, "y": 0, "z": 0}, rng=rng)

    def _get_position(self, position: Dict[str, float]) -> Dict[str, float]:
        # Get the unit position plus the depth offset.
        depth = self._get_depth()
        # Get the depth offset.
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
        pos = {"x": x, "y": 0, "z": z}
        # Get the distance offset.
        distance = self._distance + self.get_length() / 2
        if self._direction == CardinalDirection.north:
            pos["z"] += distance
        elif self._direction == CardinalDirection.south:
            pos["z"] -= distance
        elif self._direction == CardinalDirection.west:
            pos["x"] -= distance
        elif self._direction == CardinalDirection.east:
            pos["x"] += distance
        else:
            raise Exception(self._direction)
        return pos

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
