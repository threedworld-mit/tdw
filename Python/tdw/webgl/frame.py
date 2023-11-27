from typing import List


class Frame:
    """
    The commands executed, and the output data sent, on a frame.
    """

    def __init__(self, commands: List[dict], resp: List[bytes]):
        """
        :param commands: The commands that were sent on this frame. This only includes commands required for non-physics playback.
        :param resp: The response from the build (the output data) on this frame.
        """

        """:field
        The commands that were sent on this frame. This only includes commands required for non-physics playback.
        """
        self.commands: List[dict] = commands
        """:field
        The response from the build (the output data) on this frame.
        """
        self.resp: List[bytes] = resp
