from typing import List, Dict, Tuple
from tdw.tdw_utils import TDWUtils
from tdw.cardinal_direction import CardinalDirection
from tdw.proc_gen.arrangements.kitchen_counter_top_base import KitchenCounterTopBase


class Dishwasher(KitchenCounterTopBase):
    """
    A dishwasher with a kitchen counter top with objects on it.

    - The dishwasher model is chosen randomly; see `Dishwasher.MODEL_CATEGORIES["dishwasher"]`.
    - The dishwasher is placed next to a wall.
      - The dishwasher's position is automatically adjusted to set it flush to the way.
      - The dishwasher is automatically rotated so that it faces away from the wall.
    - The dishwasher has a floating kitchen counter top above it.
    - The floating kitchen counter top always has a rectangular arrangement of objects on top of it. The objects are chosen randomly; see `Dishwasher.ON_TOP_OF["kitchen_counter"]`.
    - All dishwashers have a door that can be opened.
    - The root object of the dishwasher is kinematic and the door sub-object is non-kinematic.
    """

    _DISHWASHER_OFFSET: float = 0.025

    def _get_commands(self) -> List[dict]:
        commands = self._add_root_object()
        commands.extend(super()._add_kitchen_counter_top())
        commands.extend(self._get_rotation_commands())
        return commands

    def _get_position(self, position: Dict[str, float]) -> Dict[str, float]:
        pos = super()._get_position(position=position)
        # Offset the position to leave a little gap.
        if self._direction == CardinalDirection.north:
            pos["z"] += Dishwasher._DISHWASHER_OFFSET
        elif self._direction == CardinalDirection.south:
            pos["z"] -= Dishwasher._DISHWASHER_OFFSET
        elif self._direction == CardinalDirection.east:
            pos["x"] += Dishwasher._DISHWASHER_OFFSET
        elif self._direction == CardinalDirection.west:
            pos["x"] -= Dishwasher._DISHWASHER_OFFSET
        else:
            raise Exception(self._direction)
        return pos

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

    def _get_depth(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[2]

    def _get_size(self) -> Tuple[float, float]:
        extents = TDWUtils.get_bounds_extents(bounds=self._record.bounds)
        return extents[0] + Dishwasher._DISHWASHER_OFFSET * 2, Dishwasher.DEFAULT_CELL_SIZE

    def _get_category(self) -> str:
        return "dishwasher"
