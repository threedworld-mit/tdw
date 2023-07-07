import numpy as np
from tdw.output_data import Collision
from tdw.collision_data.collision_base import CollisionBase


class CollisionObjObj(CollisionBase):
    """
    A collision between two objects.
    """

    def __init__(self, collision: Collision):
        """
        :param collision: The collision output data.
        """

        super().__init__(collision=collision)
        """:field
        The relative velocity of the objects.
        """
        self.relative_velocity: np.ndarray = np.array(collision.get_relative_velocity())
        """:field
        The total impulse applied to the pair of objects to resolve the collision.
        """
        self.impulse: np.ndarray = np.array(collision.get_impulse())
