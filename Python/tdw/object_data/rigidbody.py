import numpy as np


class Rigidbody:
    """
    Dynamic object rigidbody data. Note that this excludes *static* rigidbody data such as the mass of the object.
    """

    def __init__(self, velocity: np.ndarray, angular_velocity: np.ndarray, sleeping: bool):
        """
        :param velocity: The directional velocity of the object.
        :param angular_velocity: The angular velocity of the object.
        :param sleeping: If True, the object isn't moving.
        """

        """:field
        The directional velocity of the object.
        """
        self.velocity: np.ndarray = velocity
        """:field
        The angular velocity of the object.
        """
        self.angular_velocity: np.ndarray = angular_velocity
        """:field
        If True, the object isn't moving.
        """
        self.sleeping: bool = sleeping
