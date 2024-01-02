# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.send_objects_data_command import SendObjectsDataCommand
from typing import List


class SendEulerAngles(SendObjectsDataCommand):
    """
    Send the rotations of each object expressed as Euler angles.
    """

    def __init__(self, ids: List[int], frequency: str = "once"):
        """
        :param ids: The IDs of the objects. If this list is undefined or empty, the build will return data for all objects.
        :param frequency: The frequency at which data is sent.
        """

        super().__init__(ids=ids, frequency=frequency)

