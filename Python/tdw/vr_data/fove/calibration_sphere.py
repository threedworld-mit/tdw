from typing import Optional
from tdw.controller import Controller


class CalibrationSphere:
    """
    Metadata for a sphere used for FOVE calibration.
    """

    def __init__(self):
        """
        (no arguments)
        """

        """:field
        The object ID.
        """
        self.id: int = Controller.get_unique_id()
        """:field
        The start time of a collision with a hand. If None, there is no collision.
        """
        self.t0: Optional[float] = None
        """:field
        If True, we're done calibrating with this sphere.
        """
        self.done: bool = False
