from enum import Enum


class FoveStatus(Enum):
    """
    The status of the Fove re:calibration and trials.
    """

    fove_spiral = 0  # Running the FOVE spiral calibration.
    fove_spiral_completed = 1  # Running the FOVE spiral calibration.
    eye_hand_ongoing = 2  # Performing the sphere touch calibration protocol.
    eye_hand_complete = 3  # Sphere touch calibration protocol completed.
    waiting_for_trigger = 4  # Listening on the port for the hardware trigger.
    trial_ongoing = 5  # Received trigger. Trial has begun and is in process.
    trial_success = 6  # Trial completed successfully.
    trial_failure = 7  # Trial failed.

