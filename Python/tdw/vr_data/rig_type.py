from enum import Enum


class RigType(Enum):
    """
    Enum values for VR rigs.
    """

    oculus_touch = 1  # A VR rig based on Oculus headset and Oculus Touch controllers.
    auto_hand = 2  # A VR rig based on Oculus Quest headset, Touch controllers and AutoHand grasping.
