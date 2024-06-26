from typing import Optional
import numpy as np
from tdw.vr_data.fove.eye_state import EyeState


class Eye:
    """
    FOVE eye data.
    """

    def __init__(self, state: EyeState, direction: np.ndarray, gaze_id: Optional[int], gaze_position: Optional[np.ndarray]):
        """
        :param state: The state of the eye: not_connected, opened, or closed.
        :param direction: Where the eye is looking.
        :param gaze_id: The ID of the object that the eye is gazing at. Can be None.
        :param gaze_position: The position hit by the eye's ray. The ray can hit either an object or a scene mesh. Can be None.
        """

        """:field
        The state of the eye: not_connected, opened, or closed.
        """
        self.state: EyeState = state
        """:field
        Where the eye is looking.
        """
        self.direction: np.ndarray = direction
        """:field
        The ID of the object that the eye is gazing at. Can be None.
        """
        self.gaze_id: Optional[int] = gaze_id
        """:field
        The position hit by the eye's ray. The ray can hit either an object or a scene mesh. Can be None.
        """
        self.gaze_position: gaze_position[np.ndarray] = gaze_position
