from pathlib import Path
from pkg_resources import resource_filename
from json import loads
from typing import List
from tdw.tdw_utils import TDWUtils
from tdw.proc_gen.arrangements.arrangement_along_wall import ArrangementAlongWall


class Refrigerator(ArrangementAlongWall):
    """
    A refrigerator.

    - The refrigerator model is chosen randomly; see `Refrigerator.MODEL_CATEGORIES["refrigerator"]`.
    - The refrigerator is placed next to a wall.
      - The refrigerator's position is automatically adjusted to set it flush to the wall.
      - The refrigerator is automatically rotated so that it faces away from the wall.
    - The refrigerator is non-kinematic.
    """

    _ROTATIONS = loads(Path(resource_filename(__name__, "data/refrigerators.json")).read_text())

    def get_commands(self) -> List[dict]:
        commands = self._add_root_object()
        commands.extend(self._get_rotation_commands())
        return commands

    def get_length(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[Refrigerator._ROTATIONS[self._record.name]["length"]]

    def _get_depth(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[Refrigerator._ROTATIONS[self._record.name]["depth"]]

    def _get_category(self) -> str:
        return "refrigerator"

    def _get_rotation(self) -> float:
        return Refrigerator._ROTATIONS[self._record.name]["rotations"][self._wall.name]
