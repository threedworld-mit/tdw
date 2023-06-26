from enum import Enum


class WheelPosition(Enum):
    """
    The position of a wheelchair wheel.
    """

    left_front = 0
    left_rear = 1
    right_front = 2
    right_rear = 3
