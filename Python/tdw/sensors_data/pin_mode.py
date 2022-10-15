from enum import Enum


class PinMode(Enum):
    """
    Enum values for pin odes.
    """

    Output = 0
    PWM = 1
    Input = 2
    Input_pullup = 3
    Servo = 4
