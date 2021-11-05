from typing import List
import numpy as np
from tdw.output_data import EnvironmentCollision


class CollisionObjEnv:
    """
    A collision between an object and the environment.
    """

    def __init__(self, collision: EnvironmentCollision):
        """
        :param collision: The collision output data.
        """

        """:field
        The contact point positions.
        """
        self.points: List[np.array] = list()
        """:field
        The contact point normals.
        """
        self.normals: List[np.array] = list()
        for i in range(collision.get_num_contacts()):
            self.points.append(np.array(collision.get_contact_point(i)))
            self.normals.append(np.array(collision.get_contact_normal(i)))
        """:field
        The state of the collision.
        """
        self.state: str = collision.get_state()
        """:field
        True if this is a collision with the floor.
        """
        self.floor: bool = collision.get_floor()
