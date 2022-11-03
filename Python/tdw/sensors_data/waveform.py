from enum import Enum


class Waveform(Enum):
    """
    Enum values for vibration waveforms.
    """

    short_double_click_strong = 27
    short_double_click_medium = 31
    short_double_sharp_tick = 34
    long_double_sharp_click_strong = 37
    long_double_sharp_click_medium = 41
    buzz_1 = 47
    pulsing_strong = 52
    pulsing_medium = 54
    pulsing_sharp = 56
    transition_ramp_up_medium_smooth = 84
    transition_ramp_up_long_sharp = 88

