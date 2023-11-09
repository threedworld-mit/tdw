from typing import List


class FrameMessage:
    """
    A summary of the commands sent and the output data received on a `communicate()` call.
    """

    def __init__(self, commands: List[dict], resp: List[bytes]):
        """
        :param commands: The commands sent on this `communicate()` call.
        :param resp: The response received on this `communicate()` call.
        """

        """:field
        The commands sent on this `communicate()` call.
        """
        self.commands: List[dict] = commands
        """:field
        The response received on this `communicate()` call.
        """
        self.resp: List[bytes] = resp
