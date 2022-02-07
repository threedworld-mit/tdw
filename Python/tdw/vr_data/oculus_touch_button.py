from enum import IntFlag


class OculusTouchButton(IntFlag):
    """
    Oculus touch buttons.
    """

    grip_button = 1
    menu_button = 2
    primary_button = 4
    secondary_button = 8
    trigger_button = 16
    primary_2d_axis_click = 32
    primary_2d_axis_touch = 64
    secondary_2d_axis_click = 128
    primary_touch = 256
    secondary_touch = 512
