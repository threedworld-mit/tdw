from enum import IntFlag


class OculusTouchButton(IntFlag):
    """
    Enum values for Oculus Touch buttons.
    """

    grip_button = 1
    menu_button = 2
    primary_button = 4
    secondary_button = 8
    trigger_button = 16
    primary_2d_axis_click = 32
    secondary_2d_axis_click = 64
