from tdw.output_data import EnvironmentCollision
from tdw.collision_data.collision_base import CollisionBase


class CollisionObjEnv(CollisionBase):
    """
    A collision between an object and the environment.
    """

    def __init__(self, collision: EnvironmentCollision):
        """
        :param collision: The collision output data.
        """

        super().__init__(collision=collision)
        """:field
        True if this is a collision with the floor.
        """
        self.floor: bool = collision.get_floor()
