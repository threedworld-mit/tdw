from pathlib import Path
from pkg_resources import resource_filename
from json import loads
from typing import List
from tdw.tdw_utils import TDWUtils
from tdw.proc_gen.arrangements.arrangement_along_wall import ArrangementAlongWall


class Radiator(ArrangementAlongWall):
    """
    A radiator.

    - The radiator model is chosen randomly; see `Radiator.MODEL_CATEGORIES["radiator"]`.
    - The radiator is placed next to a wall.
      - The radiator's position is automatically adjusted to set it flush to the wall.
      - The radiator is automatically rotated so that it faces away from the wall.
      - In a lateral arrangement, there is always a little space between a radiator and the next object; see `Radiator.LENGTH_FACTOR`.
    - The radiator is non-kinematic.
    """

    _ROTATIONS = loads(Path(resource_filename(__name__, "data/radiators.json")).read_text())
    """:class_var
    The true length of a radiator is multiplied by this factor in order to create a small gap between it and adjacent objects.
    """
    LENGTH_FACTOR: float = 1.15

    def get_commands(self) -> List[dict]:
        commands = self._add_root_object()
        commands.extend(self._get_rotation_commands())
        return commands

    def get_length(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[Radiator._ROTATIONS[self._record.name]["length"]] * Radiator.LENGTH_FACTOR

    def _get_depth(self) -> float:
        depth = TDWUtils.get_bounds_extents(bounds=self._record.bounds)[Radiator._ROTATIONS[self._record.name]["depth"]]
        return depth + Radiator._ROTATIONS[self._record.name]["depth_offset"]

    def _get_category(self) -> str:
        return "radiator"

    def _get_rotation(self) -> float:
        return Radiator._ROTATIONS[self._record.name]["rotations"][self._wall.name]
