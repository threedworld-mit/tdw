from typing import List, Union
from tdw.cardinal_direction import CardinalDirection


class RegionWalls:
    """
    The walls bounding a [`RegionBounds`](region_bounds.md).

    Walls may be non-continuous (such as walls with doorways) or have windows.
    """

    def __init__(self, region: int, non_continuous_walls: Union[int, List[CardinalDirection]],
                 walls_with_windows: Union[int, List[CardinalDirection]]):
        """
        :param region: The index of the region in [`scene_bounds.rooms`](scene_bounds.md).
        :param non_continuous_walls: Non-continuous walls. This can be a list of [`CardinalDirection`](../cardinal_direction.md) values, or an integer representing a summed list of `CardinalDirection` values; for example, `3` is equivalent to `CardinalDirection.north.value + CardinalDirection.east.value`.
        :param walls_with_windows: Walls that have windows. This can be a list of [`CardinalDirection`](../cardinal_direction.md) values, or an integer representing a summed list of `CardinalDirection` values; for example, `3` is equivalent to `CardinalDirection.north.value + CardinalDirection.east.value`.
        """

        """:field
        The index of the region in [`scene_bounds.rooms`](scene_bounds.md).
        """
        self.region: int = region
        if isinstance(non_continuous_walls, list):
            """:field
            The summed values of the non-continuous walls. For example, if this is `3`, then the north and east walls are non-continuous.
            """
            self.non_continuous_walls: int = sum([c.value for c in non_continuous_walls])
        else:
            self.non_continuous_walls = non_continuous_walls
        if isinstance(walls_with_windows, list):
            """:field
            The summed values of the walls that have windows. For example, if this is `3`, then the north and east walls have windows.
            """
            self.walls_with_windows: int = sum([c.value for c in walls_with_windows])
        else:
            self.walls_with_windows = walls_with_windows
