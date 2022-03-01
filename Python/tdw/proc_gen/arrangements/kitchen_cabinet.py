from abc import ABC
from typing import Union, Optional
import numpy as np
from overrides import final
from tdw.tdw_utils import TDWUtils
from tdw.proc_gen.arrangements.arrangement_along_wall import ArrangementAlongWall
from tdw.proc_gen.arrangements.kitchen_cabinets.kitchen_cabinet_type import KitchenCabinetType
from tdw.proc_gen.arrangements.kitchen_cabinets.kitchen_cabinet_set import KitchenCabinetSet, CABINETRY
from tdw.cardinal_direction import CardinalDirection
from tdw.ordinal_direction import OrdinalDirection
from tdw.librarian import ModelRecord
from tdw.scene_data.interior_region import InteriorRegion


class KitchenCabinet(ArrangementAlongWall, ABC):
    """
    A kitchen counter, wall cabinet, or sink. These all shared the same canonical rotation and height.
    """

    _CABINETRY: Optional[KitchenCabinetSet] = None

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

        if KitchenCabinet._CABINETRY is None:
            if rng is None:
                rng = np.random.RandomState()
            cabinetry = [c for c in KitchenCabinetType]
            KitchenCabinet._CABINETRY = CABINETRY[cabinetry[rng.randint(0, len(cabinetry))]]
        super().__init__(wall=wall, corner=corner, distance=distance, region=region, model=model,
                         wall_length=wall_length, rng=rng)

    @final
    def get_length(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[0]

    @final
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
