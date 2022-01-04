from tdw.output_data import SceneRegions


class RegionBounds:
    """
    Data for the bounds of a region in a scene. In an interior scene, this usually corresponds to a room.
    """

    def __init__(self, scene_regions: SceneRegions, i: int):
        """
        :param scene_regions: The scene regions output data.
        :param i: The index of this scene in env.get_num()
        """

        """:field
        The ID of the region.
        """
        self.region_id: int = scene_regions.get_id(i)
        """:field
        The center of the region.
        """
        self.center = scene_regions.get_center(i)
        """:field
        The bounds of the region.
        """
        self.bounds = scene_regions.get_bounds(i)
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
