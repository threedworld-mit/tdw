from enum import Enum


class FoveStatus(Enum):
    """
    The status of the Fove re:calibration and trials.
    """

    fove_spiral = 0  # Running the FOVE spiral calibration.
    eye_hand = 1  # Performing the sphere touch calibration protocol.
    waiting_for_trigger = 2  # Listening on the port for the hardware trigger.
    trial_ongoing = 3  # Received trigger. Trial has begun and is in process.
    trial_success = 4  # Trial completed successfully.
    trial_failure = 5  # Trial failed.

