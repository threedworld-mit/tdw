from typing import List, Union, Tuple
from tdw.scene_data.region_bounds import RegionBounds
from tdw.cardinal_direction import CardinalDirection


class InteriorRegion(RegionBounds):
    """
    An interior region has bounds data and cached data regarding continuous walls and walls with windows.
    """

    def __init__(self, region_id: int, center: Tuple[float, float, float], bounds: Tuple[float, float, float],
                 non_continuous_walls: Union[int, List[CardinalDirection]], walls_with_windows: Union[int, List[CardinalDirection]]):
        """
        :param region_id: The ID of the region.
        :param center: The center of the region.
        :param bounds: The bounds of the region.
        :param non_continuous_walls: Non-continuous walls. This can be a list of [`CardinalDirection`](../cardinal_direction.md) values, or an integer representing a summed list of `CardinalDirection` values; for example, `3` is equivalent to `CardinalDirection.north.value + CardinalDirection.east.value`.
        :param walls_with_windows: Walls that have windows. This can be a list of [`CardinalDirection`](../cardinal_direction.md) values, or an integer representing a summed list of `CardinalDirection` values; for example, `3` is equivalent to `CardinalDirection.north.value + CardinalDirection.east.value`.
        """

        super().__init__(region_id=region_id, center=center, bounds=bounds)
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
