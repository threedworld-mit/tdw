from typing import List
from tdw.tdw_utils import TDWUtils
from tdw.cardinal_direction import CardinalDirection
from tdw.proc_gen.arrangements.arrangement_along_wall import ArrangementAlongWall


class Shelf(ArrangementAlongWall):
    """
    Shelving with objects on the shelves.

    - The shelf model is chosen randomly; see `Shelf.MODEL_CATEGORIES["shelf"]`.
    - The shelf is placed next to a wall.
      - The shelf's position is automatically adjusted to set it flush to the wall.
      - The shelf is automatically rotated so that it faces away from the wall.
    - Each shelf of the object has a rectangular arrangement of objects. See: `Shelf.CELL_SIZE`, `Shelf.CELL_DENSITY`, `Shelf.WIDTH_SCALE`, and `Shelf.DEPTH_SCALE`.
      - The objects are chosen randomly; see `Shelf.ON_TOP_OF["shelf"]`.
      - The objects are positioned in a rectangular grid on each shelf with random positional perturbations.
      - The objects have random rotations (0 to 360 degrees).
    - The shelf object is kinematic.
    """

    """:class_var
    The size of each cell in the shelf rectangular arrangements. This controls the minimum size of objects and the density of the arrangement.
    """
    CELL_SIZE: float = 0.0125
    """:class_var
    The probability from 0 to 1 of a "cell" in the shelf rectangular arrangements being empty. Lower value = a higher density of small objects.
    """
    CELL_DENSITY: float = 0.8
    """:class
    When adding objects, the width of the shelf is assumed to be `actual_width * WIDTH_SCALE`. This prevents objects from intersecting with the edges of the shelf.
    """
    WIDTH_SCALE: float = 0.75
    """:class
    When adding objects, the depth of the shelf is assumed to be `actual_depth * DEPTH_SCALE`. This prevents objects from intersecting with the edges of the shelf.
    """
    DEPTH_SCALE: float = 0.75

    def get_commands(self) -> List[dict]:
        return self._add_object_with_other_objects_on_top(cell_size=Shelf.CELL_SIZE,
                                                          density=Shelf.CELL_DENSITY,
                                                          x_scale=Shelf.WIDTH_SCALE,
                                                          z_scale=Shelf.DEPTH_SCALE)

    def _get_rotation(self) -> float:
        if self._wall == CardinalDirection.north:
            return 270
        elif self._wall == CardinalDirection.east:
            return 180
        elif self._wall == CardinalDirection.south:
            return 90
        else:
            return 0

    def get_length(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[2]

    def _get_depth(self) -> float:
        return TDWUtils.get_bounds_extents(bounds=self._record.bounds)[0]

    def _get_category(self) -> str:
        return "shelf"
