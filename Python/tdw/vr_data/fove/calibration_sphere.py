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
        If True, the hand is colliding with this sphere.
        """
        self.colliding: bool = False
        """:field
        The start time of a collision with a hand.
        """
        self.t0: float = 0
        """:field
        If True, we're done calibrating with this sphere.
        """
        self.done: bool = False
