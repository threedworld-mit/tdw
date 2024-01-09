# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.adjust_textured_quad_command import AdjustTexturedQuadCommand
from typing import Dict


class RotateTexturedQuadTo(AdjustTexturedQuadCommand):
    """
    Set the rotation of a textured quad.
    """

    def __init__(self, id: int, rotation: Dict[str, float]):
        """
        :param id: The ID of the non-physics object.
        :param rotation: The rotation quaternion.
        """

        super().__init__(id=id)
        """:field
        The rotation quaternion.
        """
        self.rotation: Dict[str, float] = rotation