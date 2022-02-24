from typing import List, Dict
from tdw.tdw_utils import TDWUtils
from tdw.cardinal_direction import CardinalDirection
from tdw.proc_gen.arrangements.arrangement_along_wall import ArrangementAlongWall


class Painting(ArrangementAlongWall):
    """
    A painting hanging on the wall.

    - The painting model is chosen randomly; see `Painting.MODEL_CATEGORIES["painting"]`.
    - The height of the painting is random, from 1.1 meters to `(ceiling_height - painting_height)`.
    - The painting is kinematic.
    """

    def get_commands(self) -> List[dict]:
        return self._add_root_object()

    def get_length(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[0]

    def _get_position(self, position: Dict[str, float]) -> Dict[str, float]:
        pos = super()._get_position(position=position)
        extents = TDWUtils.get_bounds_extents(bounds=self._record.bounds)
        pos["y"] = float(self._rng.uniform(1.1, self._region.bounds[1] - extents[1]))
        return pos
    
    def _get_depth(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[2]
    
    def _get_rotation(self) -> float:
        if self._wall == CardinalDirection.north:
            return 180
        elif self._wall == CardinalDirection.south:
            return 0
        elif self._wall == CardinalDirection.west:
            return 90
        elif self._wall == CardinalDirection.east:
            return 270

    def _get_category(self) -> str:
        return "painting"
