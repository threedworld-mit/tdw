from enum import Enum


class EyeTorsionCalibration(Enum):
    """
    Indicate whether each eye torsion calibration should be run.
    """

    default = 0  # Use the settings coming from the configuration file.
    if_enabled = 1  # Run eye torsion calibration only if the capability is currently enabled.
    always = 2  # Always run eye torsion calibration independently of whether the capability is used.
