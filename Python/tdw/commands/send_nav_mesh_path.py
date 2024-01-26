# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.send_multiple_data_once_command import SendMultipleDataOnceCommand
from typing import Dict


class SendNavMeshPath(SendMultipleDataOnceCommand):
    """
    Tell the build to send data of a path on the NavMesh from the origin to the destination.
    """

    def __init__(self, destination: Dict[str, float], origin: Dict[str, float], id: int = 0):
        """
        :param destination: The destination of the path.
        :param origin: The origin of the path.
        :param id: The ID of the output data object. This can be used to match the output data back to the command that created it.
        """

        super().__init__(id=id)
        """:field
        The origin of the path.
        """
        self.origin: Dict[str, float] = origin
        """:field
        The destination of the path.
        """
        self.destination: Dict[str, float] = destination