from tdw.output_data import Environments


class RoomBounds:
    """
    Data for the bounds of a room in a scene.
    """

    def __init__(self, env: Environments, i: int):
        """
        :param env: The environments output data.
        :param i: The index of this scene in env.get_num()
        """

        """:field
        The ID of the room.
        """
        self.room_id: int = env.get_id(i)
        """:field
        The center of the room.
        """
        self.center = env.get_center(i)
        """:field
        The bounds of the room.
        """
        self.bounds = env.get_bounds(i)
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