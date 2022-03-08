from typing import List, Dict
from tdw.tdw_utils import TDWUtils
from tdw.cardinal_direction import CardinalDirection
from tdw.proc_gen.arrangements.arrangement_along_wall import ArrangementAlongWall


class Painting(ArrangementAlongWall):
    """
    A painting hanging on the wall.

    - The painting model is chosen randomly; see `Painting.MODEL_CATEGORIES["painting"]`.
    - The painting is placed next to a wall.
      - The painting's position is automatically adjusted to set it flush to the wall.
      - The painting is automatically rotated so that it faces away from the wall.
      - The height of the painting is random, from `Painting.MIN_Y` to `(ceiling_height - painting_height)`.
    - The painting is kinematic.
    """

    """:class_var
    The minimum value of the y positional coordinate (the height) of a painting.
    """
    MIN_Y: float = 1.1

    def get_commands(self) -> List[dict]:
        commands = self._add_root_object()
        commands.extend(self._get_rotation_commands())
        return commands

    def get_length(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[0] * 2

    def _get_position(self, position: Dict[str, float]) -> Dict[str, float]:
        pos = super()._get_position(position=position)
        extents = TDWUtils.get_bounds_extents(bounds=self._record.bounds)
        pos["y"] = float(self._rng.uniform(Painting.MIN_Y, self._region.bounds[1] - extents[1]))
        return pos
    
    def _get_depth(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[2] * 4
    
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
