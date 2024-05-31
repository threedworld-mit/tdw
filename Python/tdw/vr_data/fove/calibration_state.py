from enum import Enum


class CalibrationState(Enum):
    """
    State machine flags for controlling FOVE calibration.
    """

    calibrating = 0  # The headset is running the built-in FOVE calibration.
    calibrating_with_spheres = 1  # The simulation is running a TDW-specific calibration scene.
    running = 2   # The headset is done calibrating.
