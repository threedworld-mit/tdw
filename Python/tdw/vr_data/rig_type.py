from enum import Enum


class RigType(Enum):
    """
    Enum values for VR rigs.
    """

    oculus_touch_robot_hands = 1  # Oculus Touch controller. Hands are rendered as robot hands.
    oculus_touch_human_hands = 2  # Oculus Touch controller. Hands are rendered as human hands.
    oculus_leap_motion = 3  # Oculus rig with Leap Motion hand tracking.
