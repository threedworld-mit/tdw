from typing import Optional
import numpy as np


class CalibrationSphere:
    """
    Metadata for a sphere used for FOVE calibration.
    """

    def __init__(self, position: np.ndarray):
        """
        :param position: The position of the sphere.
        """

        """:field
        The position of the sphere.
        """
        self.position: np.ndarray = position
        """:field
        The start time of a collision with a hand. If None, the hand isn't colliding with the sphere.
        """
        self.t0: Optional[int] = None
        """:field
        If True, we're done calibrating with this sphere.
        """
        self.done: bool = False
