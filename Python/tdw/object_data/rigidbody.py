import numpy as np


class Rigidbody:
    """
    Dynamic object rigidbody data. Note that this excludes *static* rigidbody data such as the mass of the object.
    """

    def __init__(self, velocity: np.array, angular_velocity: np.array, sleeping: bool):
        """
        :param velocity:
        :param angular_velocity:
        :param sleeping:
        """

        self.velocity: np.array = velocity
        self.angular_velocity: np.array = angular_velocity
        self.sleeping: bool = sleeping
