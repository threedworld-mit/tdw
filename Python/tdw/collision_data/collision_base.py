from abc import ABC
from typing import List, Union
import numpy as np
from tdw.output_data import Collision, EnvironmentCollision


class CollisionBase(ABC):
    """
    Abstract base class for collision data.
    """

    def __init__(self, collision: Union[Collision, EnvironmentCollision]):
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
