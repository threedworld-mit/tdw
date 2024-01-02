# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.send_avatars_command import SendAvatarsCommand
from typing import List


class SendIdPassGrayscale(SendAvatarsCommand):
    """
    Send the average grayscale value of an _id pass.
    """

    def __init__(self, ids: List[str] = None, frequency: str = "once"):
        """
        :param ids: The IDs of the avatars. If this list is undefined or empty, the build will return data for all avatars.
        :param frequency: The frequency at which data is sent.
        """

        super().__init__(ids=ids, frequency=frequency)

