from enum import Enum


class ImageFrequency(Enum):
    """
    The per-frame frequency of image capture.
    """

    once = 1  # Capture an image only on this `communicate()` call.
    always = 2  # Capture images on every `communicate()` call.
    never = 4  # Don't capture images on any `communicate()` call.
