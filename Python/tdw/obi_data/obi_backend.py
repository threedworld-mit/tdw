from enum import Enum


class ObiBackend(Enum):
    """
    Obi solver backends.
    """

    """:field
    The optimized backend. You should almost always use this.
    """
    burst = 0
    """:field
    The unoptimized legacy backend. This should only be used for ongoing projects. It doesn't work on Apple Silicon.
    """
    oni = 1
