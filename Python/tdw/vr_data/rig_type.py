from enum import Enum


class RigType(Enum):
    """
    Enum values for VR rigs.
    """

    oculus_touch_robot_hands = 1  # Oculus Touch controller. Hands are rendered as robot hands.
    oculus_touch_human_hands = 2  # Oculus Touch controller. Hands are rendered as human hands.
    leap_motion_capsule_hands = 3  # Leap Motion controller. Hands are rendered as capsule hands.
