from typing import Dict, Union
from abc import ABC, abstractmethod
import numpy as np
from tdw.proc_gen.arrangements.arrangement_with_root_object import ArrangementWithRootObject
from tdw.scene_data.interior_region import InteriorRegion
from tdw.cardinal_direction import CardinalDirection
from tdw.librarian import ModelRecord


class ArrangementAlongWall(ArrangementWithRootObject, ABC):
    """
    A procedurally-generated spatial arrangement of objects that is positioned alongside a wall.
    """

    def __init__(self, wall: CardinalDirection, region: InteriorRegion, model: Union[str, ModelRecord], position: Dict[str, float],
                 rng: np.random.RandomState):
        """
        :param wall: The wall as a [`CardinalDirection`](../../cardinal_direction.md) that the root object is next to.
        :param region: The [`InteriorRegion`](../../scene_data/interior_region.md) that the object is in.
        :param model: Either the name of the model (in which case the model must be in `models_core.json` or a `ModelRecord`.
        :param position: The position of the root object. This might be adjusted.
        :param rng: The random number generator.
        """

        self._wall: CardinalDirection = wall
        self._region: InteriorRegion = region
        super().__init__(model=model, position=position, rng=rng)

    def _get_position(self, position: Dict[str, float]) -> Dict[str, float]:
        depth = self._get_depth()
        if self._wall == CardinalDirection.north:
            return {"x": position["x"],
                    "y": 0,
                    "z": self._region.z_max - depth / 2}
        elif self._wall == CardinalDirection.south:
            return {"x": position["x"],
                    "y": 0,
                    "z": self._region.z_min + depth / 2}
        elif self._wall == CardinalDirection.west:
            return {"x": self._region.x_min + depth / 2,
                    "y": 0,
                    "z": position["z"]}
        elif self._wall == CardinalDirection.east:
            return {"x": self._region.x_max - depth / 2,
                    "y": 0,
                    "z": position["z"]}
        else:
            raise Exception(self._wall)

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
