from tdw.scene_data.region_bounds import RegionBounds
from tdw.scene_data.region_walls import RegionWalls


class InteriorRegion:
    """
    An interior region has [bounds](region_bounds.md) and [walls](region_walls.md).
    """

    def __init__(self, bounds: RegionBounds, walls: RegionWalls):
        """
        :param bounds: The [`RegionBounds`](region_bounds.md).
        :param walls: The [`RegionWalls`](region_walls.md).
        """

        """:field
        The [`RegionBounds`](region_bounds.md).
        """
        self.bounds: RegionBounds = bounds
        """:field
        The [`RegionWalls`](region_walls.md).
        """
        self.walls: RegionWalls = walls
