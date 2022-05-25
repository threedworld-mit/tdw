from abc import ABC
from typing import Union
import numpy as np
from overrides import final
from tdw.tdw_utils import TDWUtils
from tdw.proc_gen.arrangements.arrangement_along_wall import ArrangementAlongWall
from tdw.proc_gen.arrangements.cabinetry.cabinetry import Cabinetry
from tdw.cardinal_direction import CardinalDirection
from tdw.ordinal_direction import OrdinalDirection
from tdw.librarian import ModelRecord
from tdw.scene_data.interior_region import InteriorRegion


class KitchenCabinet(ArrangementAlongWall, ABC):
    """
    Abstract class for kitchen counters, wall cabinets, and sinks. These all shared the same canonical rotation and height.
    """

    def __init__(self, cabinetry: Cabinetry, corner: OrdinalDirection, wall: CardinalDirection,
                 distance: float, region: InteriorRegion, model: Union[str, ModelRecord] = None,
                 wall_length: float = None, rng: Union[int, np.random.RandomState] = None):
        """
        :param cabinetry: The [`Cabinetry`](cabinetry/cabinetry.md) set.
        :param wall: The wall as a [`CardinalDirection`](../../cardinal_direction.md) that the root object is next to.
        :param corner: The origin [`OrdinalDirection`](../../ordinal_direction.md) of this wall. This is used to derive the direction.
        :param distance: The distance in meters from the corner along the derived direction.
        :param region: The [`InteriorRegion`](../../scene_data/interior_region.md) that the object is in.
        :param model: Either the name of the model (in which case the model must be in `models_core.json`), or a `ModelRecord`, or None. If None, a model that fits along the wall at `distance` is randomly selected.
        :param wall_length: The total length of the lateral arrangement. If None, defaults to the length of the wall.
        :param rng: Either a random seed or an `numpy.random.RandomState` object. If None, a new random number generator is created.
        """

        self._cabinetry: Cabinetry = cabinetry
        super().__init__(wall=wall, corner=corner, distance=distance, region=region, model=model,
                         wall_length=wall_length, rng=rng)

    @final
    def get_length(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[0]

    def _get_rotation(self) -> float:
        if self._wall == CardinalDirection.north:
            return 180
        elif self._wall == CardinalDirection.east:
            return 270
        elif self._wall == CardinalDirection.south:
            return 0
        else:
            return 90

    @final
    def _get_depth(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[2]
