from typing import List
from tdw.tdw_utils import TDWUtils
from tdw.cardinal_direction import CardinalDirection
from tdw.proc_gen.arrangements.arrangement_along_wall import ArrangementAlongWall


class Suitcase(ArrangementAlongWall):
    """
    A suitcase.

    - The suitcase model is chosen randomly; see `Suitcase.MODEL_CATEGORIES["suitcase"]`.
    - The suitcase is placed next to a wall.
      - The suitcase's position is automatically adjusted to set it flush to the way.
      - The suitcase is automatically rotated so that it faces away from the wall.
    """

    def get_commands(self) -> List[dict]:
        commands = self._add_root_object(kinematic=False)
        commands.extend(self._get_rotation_commands())
        return commands

    def get_length(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[0] + 0.05

    def _get_depth(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[2]

    def _get_category(self) -> str:
        return "suitcase"

    def _get_rotation(self) -> float:
        if self._wall == CardinalDirection.north:
            return 180
        elif self._wall == CardinalDirection.east:
            return 270
        elif self._wall == CardinalDirection.south:
            return 0
        else:
            return 90
