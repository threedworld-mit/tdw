from enum import Enum


class ImageFrequency(Enum):
    """
    The per-frame frequency of image capture.
    """

    once = 1  # Capture an image only on this frame.
    always = 2  # Capture images per frame.
    never = 4  # Don't capture images on this or any frame.
