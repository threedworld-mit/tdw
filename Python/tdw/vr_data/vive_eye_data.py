import numpy as np


class ViveEyeData:
    """
    Vive eye-tracking data.
    """

    def __init__(self, valid: bool, ray: np.ndarray, blinking: np.ndarray):
        """
        :param valid: If True, there is valid eye tracking data.
        :param ray: A numpy array describing the eye ray. Shape: `(2, 3)`. Order: `(origin, direction)`. This is only valid data is `valid == True`.
        :param blinking: A numpy array of booleans describing whether each eye is blinking: `[left, right]`. This is only valid data is `valid == True`.
        """

        """:field
        If True, there is valid eye tracking data.
        """
        self.valid: bool = valid
        """:field
        A numpy array describing the eye ray. Shape: `(2, 3)`. Order: `(origin, direction)`. This is only valid data is `valid == True`.
        """
        self.ray: np.ndarray = ray
        """:field
        A numpy array of booleans describing whether each eye is blinking: `[left, right]`. This is only valid data is `valid == True`.
        """
        self.blinking: np.ndarray = blinking


def get_default_data() -> ViveEyeData:
    """
    :return: Default `ViveEyeData`.
    """

    return ViveEyeData(valid=False, ray=np.zeros(shape=(2, 3)), blinking=np.zeros(shape=2, dtype=bool))
