import numpy as np
from tdw.vr_data.fove.eye_state import EyeState


class Eye:
    """
    FOVE eye data.
    """

    def __init__(self, state: EyeState, direction: np.ndarray):
        """
        :param state: The state of the eye: not_connected, opened, or closed.
        :param direction: Where the eye is looking.
        """

        """:field
        The state of the eye: not_connected, opened, or closed.
        """
        self.state: EyeState = state
        """:field
        Where the eye is looking.
        """
        self.direction: np.ndarray = direction
