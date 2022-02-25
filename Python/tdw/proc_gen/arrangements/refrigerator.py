from typing import List
from tdw.tdw_utils import TDWUtils
from tdw.proc_gen.arrangements.arrangement_along_wall import ArrangementAlongWall


class Refrigerator(ArrangementAlongWall):
    """
    A refrigerator.

    - The refrigerator model is chosen randomly; see `Refrigerator.MODEL_CATEGORIES["refrigerator"]`.
    - The refrigerator is placed next to a wall.
      - The refrigerator's position is automatically adjusted to set it flush to the way.
      - The refrigerator is automatically rotated so that it faces away from the wall.
    - The refrigerator's rotation is random.
    - The refrigerator is non-kinematic.
    """

    def get_commands(self) -> List[dict]:
        return self._add_root_object()

    def get_length(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[0]

    def _get_depth(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[2]

    def _get_category(self) -> str:
        return "refrigerator"

    def _get_rotation(self) -> float:
        return self._rng.uniform(0, 360)
