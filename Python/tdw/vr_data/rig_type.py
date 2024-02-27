from enum import Enum


class RigType(Enum):
    """
    Enum values for VR rigs.
    """

    oculus_touch_robot_hands = 1  # Oculus Touch controller. Hands are rendered as robot hands.
    oculus_touch_human_hands = 2  # Oculus Touch controller. Hands are rendered as human hands.
    oculus_leap_motion = 3  # Oculus rig with Leap Motion hand tracking.
    fove_human_leap_motion = 4  # A VR rig based on a FOVE human headset with Leap Motion hand tracking.
    fove_human_optical = 5  # A VR rig based on a FOVE human headset with Optitrack optical hand tracking.
    fove_primate_leap_motion = 6  # A VR rig based on a FOVE headset for primates, with Leap Motion hand tracking.
    fove_primate_optical = 7  # A VR rig based on a FOVE headset for primates, with Optitrack optical hand tracking.