from abc import ABC
from overrides import final
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.proc_gen_objects_data.arrangement_along_wall import ArrangementAlongWall
from tdw.cardinal_direction import CardinalDirection


class KitchenCabinet(ArrangementAlongWall, ABC):
    """
    A kitchen counter, wall cabinet, or sink. These all shared the same canonical rotation and height.
    """

    @final
    def _get_rotation(self) -> float:
        if self._wall == CardinalDirection.north:
            return 180
        elif self._wall == CardinalDirection.east:
            return 90
        elif self._wall == CardinalDirection.south:
            return 0
        else:
            return 270

    @final
    def _get_depth(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[2]
