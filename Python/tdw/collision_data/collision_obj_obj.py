from typing import List
import numpy as np
from tdw.output_data import Collision


class CollisionObjObj:
    """
    A collision between two objects.
    """

    def __init__(self, collision: Collision):
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
        The relative velocity of the objects.
        """
        self.relative_velocity: np.array = np.array(collision.get_relative_velocity())
        """:field
        The state of the collision.
        """
        self.state: str = collision.get_state()
