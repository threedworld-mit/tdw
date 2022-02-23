from abc import ABC
from overrides import final
from tdw.tdw_utils import TDWUtils
from tdw.proc_gen.arrangements.arrangement_along_wall import ArrangementAlongWall
from tdw.cardinal_direction import CardinalDirection


class KitchenCabinet(ArrangementAlongWall, ABC):
    """
    A kitchen counter, wall cabinet, or sink. These all shared the same canonical rotation and height.
    """

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
