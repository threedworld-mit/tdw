import numpy as np


class Rigidbody:
    """
    Dynamic object rigidbody data. Note that this excludes *static* rigidbody data such as the mass of the object.
    """

    def __init__(self, velocity: np.array, angular_velocity: np.array, sleeping: bool):
        """
        :param velocity: The directional velocity of the object.
        :param angular_velocity: The angular velocity of the object.
        :param sleeping: If True, the object isn't moving.
        """

        """:field
        The directional velocity of the object.
        """
        self.velocity: np.array = velocity
        """:field
        The angular velocity of the object.
        """
        self.angular_velocity: np.array = angular_velocity
        """:field
        If True, the object isn't moving.
        """
        self.sleeping: bool = sleeping
