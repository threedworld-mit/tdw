from typing import List
from tdw.tdw_utils import TDWUtils
from tdw.proc_gen.arrangements.arrangement_along_wall import ArrangementAlongWall


class Stool(ArrangementAlongWall):
    """
    A stool.

    - The stool model is chosen randomly; see `Stool.MODEL_CATEGORIES["stool"]`.
    - The stool's rotation is random.
    - The stool is non-kinematic.
    """

    def get_commands(self) -> List[dict]:
        return self._add_root_object()

    def get_length(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[0]

    def _get_depth(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[2]

    def _get_category(self) -> str:
        return "stool"

    def _get_rotation(self) -> float:
        return self._rng.uniform(0, 360)
