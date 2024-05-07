from enum import Enum


class EyeByEyeCalibration(Enum):
    """
    Indicate whether each eye should be calibrated separately or not.
    """

    default = 0
    disabled = 1
    enabled = 2  # Requires license.
