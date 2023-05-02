from enum import Enum


class RigType(Enum):
    """
    Enum values for VR rigs.
    """

    oculus_touch_robot_hands = 1  # Oculus Touch controller. Hands are rendered as robot hands.
    oculus_touch_human_hands = 2  # Oculus Touch controller. Hands are rendered as human hands.
    vive_human_hands_eyetracking = 3  # Vive Pro Eye headset and controllers, with eye tracking. Hands are rendered as human hands.
    vive_human_hands_eyetracking = 4  # Vive Pro Eye headset and controllers, with eye tracking. Hands are rendered as robot hands.
