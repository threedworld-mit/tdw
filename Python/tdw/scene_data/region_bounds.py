from typing import Tuple, List
from tdw.cardinal_direction import CardinalDirection
from tdw.output_data import SceneRegions


class RegionBounds:
    """
    Data for the bounds of a region in a scene. In an interior scene, this usually corresponds to a room.
    """

    def __init__(self, region_id: int, center: Tuple[float, float, float], bounds: Tuple[float, float, float]):
        """
        :param region_id: The ID of the region.
        :param center: The center of the region.
        :param bounds: The bounds of the region.
        """

        """:field
        The ID of the region.
        """
        self.region_id: int = region_id
        """:field
        The center of the region.
        """
        self.center: Tuple[float, float, float] = center
        """:field
        The bounds of the region.
        """
        self.bounds: Tuple[float, float, float] = bounds
        """:field
        Minimum x positional coordinate of the room.
        """
        self.x_min: float = self.center[0] - (self.bounds[0] / 2)
        """:field
        Minimum y positional coordinate of the room.
        """
        self.y_min: float = self.center[1] - (self.bounds[1] / 2)
        """:field
        Minimum z positional coordinate of the room.
        """
        self.z_min: float = self.center[2] - (self.bounds[2] / 2)
        """:field
        Maximum x positional coordinate of the room.
        """
        self.x_max: float = self.center[0] + (self.bounds[0] / 2)
        """:field
        Maximum y positional coordinate of the room.
        """
        self.y_max: float = self.center[1] + (self.bounds[1] / 2)
        """:field
        Maximum z positional coordinate of the room.
        """
        self.z_max: float = self.center[2] + (self.bounds[2] / 2)

    def is_inside(self, x: float, z: float) -> bool:
        """
        :param x: The x coordinate.
        :param z: The z coordinate.

        :return: True if position (x, z) is in the scene.
        """

        return self.x_min <= x <= self.x_max and self.z_min <= z <= self.z_max

    def get_length(self, side: CardinalDirection) -> float:
        """
        :param side: A side of the region as a [`CardinalDirection`](../cardinal_direction.md).

        :return: The length of the side.
        """

        if side == CardinalDirection.north or side == CardinalDirection.south:
            return self.x_max - self.x_min
        else:
            return self.z_max - self.z_min

    def get_longer_sides(self) -> Tuple[List[CardinalDirection], float]:
        """
        :return: Tuple: A list of the longer sides as [`CardinalDirection` values](../cardinal_direction.md), the length of the sides.
        """

        x = self.x_max - self.x_min
        z = self.z_max - self.z_min
        if x < z:
            return [CardinalDirection.west, CardinalDirection.east], z
        else:
            return [CardinalDirection.north, CardinalDirection.south], x

    def get_shorter_sides(self) -> Tuple[List[CardinalDirection], float]:
        """
        :return: Tuple: A list of the shorter sides as [`CardinalDirection` values](../cardinal_direction.md), the length of the sides.
        """

        x = self.x_max - self.x_min
        z = self.z_max - self.z_min
        if x > z:
            return [CardinalDirection.west, CardinalDirection.east], z
        else:
            return [CardinalDirection.north, CardinalDirection.south], x


def get_from_scene_regions(scene_regions: SceneRegions, i: int) -> RegionBounds:
    """
    :param scene_regions: The scene regions output data.
    :param i: The index of this scene in env.get_num()

    :return: `RegionBounds`.
    """

    return RegionBounds(region_id=scene_regions.get_id(i),
                        center=scene_regions.get_center(i),
                        bounds=scene_regions.get_bounds(i))
