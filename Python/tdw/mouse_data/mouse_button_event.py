from enum import Enum


class MouseButtonEvent(Enum):
    """
    Enum values for a mouse button event.
    """

    press = 0  # The button was pressed on this frame.
    hold = 1  # The button was held on this frame, having been pressed on a previous frame.
    release = 2  # The button was released on this frame.
