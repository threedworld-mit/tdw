# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.send_overlap_command import SendOverlapCommand
from typing import Dict


class SendOverlapSphere(SendOverlapCommand):
    """
    Check which objects a sphere-shaped space overlaps with.
    """

    def __init__(self, position: Dict[str, float], radius: float, id: int = 0):
        """
        :param position: The center of the shape.
        :param radius: The radius of the sphere.
        :param id: The ID of the output data object. This can be used to match the output data back to the command that created it.
        """

        super().__init__(position=position, id=id)
        """:field
        The radius of the sphere.
        """
        self.radius: float = radius
