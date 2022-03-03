from typing import Tuple, List
import numpy as np
from tdw.proc_gen.arrangements.kitchen_counter_top_base import KitchenCounterTopBase
from tdw.proc_gen.arrangements.kitchen_cabinets.kitchen_cabinet_set import KitchenCabinetSet
from tdw.scene_data.interior_region import InteriorRegion
from tdw.cardinal_direction import CardinalDirection
from tdw.ordinal_direction import OrdinalDirection


class KitchenCounterTop(KitchenCounterTopBase):
    """
    A floating kitchen counter top along a wall.

    - The kitchen counter top is placed next to a wall and at a height equal to the height of the kitchen counter models.
      - The kitchen counter top's position is automatically adjusted to set it flush to the way.
    - The kitchen counter top will have a rectangular arrangement of objects on top of it. The objects are chosen randomly; see `KitchenCounterTop.ON_TOP_OF["kitchen_counter"]`.
    - The kitchen counter top is kinematic.
    """

    def __init__(self, cabinetry: KitchenCabinetSet, corner: OrdinalDirection, wall: CardinalDirection, distance: float,
                 region: InteriorRegion, wall_length: float = None, rng: np.random.RandomState = None):
        """
        :param cabinetry: The [`KitchenCabinetSet`](kitchen_cabinets/kitchen_cabinet_set.md).
        :param wall: The wall as a [`CardinalDirection`](../../cardinal_direction.md) that the root object is next to.
        :param corner: The origin [`Corner`](../../corner.md) of this wall. This is used to derive the direction.
        :param distance: The distance in meters from the corner along the derived direction.
        :param wall_length: The total length of the lateral arrangement. If None, defaults to the length of the wall.
        :param rng: The random number generator. If None, a new random number generator is created.
        """

        self._distance: float = distance
        super().__init__(cabinetry=cabinetry, corner=corner, wall=wall, distance=distance, region=region,
                         wall_length=wall_length, rng=rng)
        self.send_commands = True

    def get_commands(self) -> List[dict]:
        # Add the counter top if it fits in the region.
        if self._distance + KitchenCounterTopBase.DEFAULT_CELL_SIZE < self._wall_length:
            return self._add_kitchen_counter_top()
        else:
            self.send_commands = False
            return []

    def get_length(self) -> float:
        return KitchenCounterTopBase.DEFAULT_CELL_SIZE

    def _get_rotation(self) -> float:
        if self._wall == CardinalDirection.west or self._wall == CardinalDirection.east:
            return 90
        else:
            return 0

    def _get_size(self) -> Tuple[float, float]:
        return KitchenCounterTopBase.DEFAULT_CELL_SIZE, KitchenCounterTopBase.DEFAULT_CELL_SIZE

    def _get_depth(self) -> float:
        return KitchenCounterTopBase.DEFAULT_CELL_SIZE

    def _get_category(self) -> str:
        return ""

    def _get_model_names(self) -> List[str]:
        return []
