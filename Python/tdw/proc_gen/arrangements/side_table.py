from typing import List
from tdw.tdw_utils import TDWUtils
from tdw.cardinal_direction import CardinalDirection
from tdw.proc_gen.arrangements.arrangement_along_wall import ArrangementAlongWall


class SideTable(ArrangementAlongWall):
    """
    A small side table with objects on it.

    - The side table model is chosen randomly; see `SideTable.MODEL_CATEGORIES["side_table"]`.
    - The side table is placed next to a wall.
      - The side table's position is automatically adjusted to set it flush to the wall.
      - The side table is automatically rotated so that it faces away from the wall.
      - The side table's (x, z) positional coordinates are offset by a factor; see `SideTable.DEPTH_FACTOR` and `SIDE_TABLE.LENGTH_FACTOR`.
    - The side table will have a rectangular arrangement of objects on top of it.
      - The objects are chosen randomly; see `SideTable.ON_TOP_OF["side_table"]`.
      - The objects are positioned in a rectangular grid on the table with random rotations and positional perturbations; see: `SideTable.CELL_SIZE`, `SideTable.CELL_DENSITY`, `SideTable.WIDTH_SCALE`, and `SideTable.DEPTH_SCALE`.
    - The side table is non-kinematic.
    """

    """:class_var
    Offset the distance from the wall by this factor.
    """
    DEPTH_FACTOR: float = 1.05
    """:class_var
    Offset the distance along the wall by this factor.
    """
    LENGTH_FACTOR: float = 1.25
    """:class_var
    The size of each cell in the side table rectangular arrangement. This controls the minimum size of objects and the density of the arrangement.
    """
    CELL_SIZE: float = 0.05
    """:class_var
    The probability from 0 to 1 of a "cell" in the side table rectangular arrangement being empty. Lower value = a higher density of small objects.
    """
    CELL_DENSITY: float = 0.4
    """:class
    When adding objects, the width of the side table is assumed to be `actual_width * WIDTH_SCALE`. This prevents objects from being too close to the edges of the side table.
    """
    WIDTH_SCALE: float = 0.8
    """:class
    When adding objects, the depth of the side table is assumed to be `actual_depth * DEPTH_SCALE`. This prevents objects from being too close to the edges of the side table.
    """
    DEPTH_SCALE: float = 0.8

    def get_commands(self) -> List[dict]:
        return self._add_object_with_other_objects_on_top(kinematic=False,
                                                          cell_size=SideTable.CELL_SIZE,
                                                          density=SideTable.CELL_DENSITY,
                                                          x_scale=SideTable.WIDTH_SCALE,
                                                          z_scale=SideTable.DEPTH_SCALE)

    def get_length(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[2] * SideTable.LENGTH_FACTOR

    def _get_depth(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[0] * SideTable.DEPTH_FACTOR

    def _get_rotation(self) -> float:
        if self._wall == CardinalDirection.north:
            return 0
        elif self._wall == CardinalDirection.east:
            return 90
        elif self._wall == CardinalDirection.south:
            return 180
        else:
            return 270

    def _get_category(self) -> str:
        return "side_table"
