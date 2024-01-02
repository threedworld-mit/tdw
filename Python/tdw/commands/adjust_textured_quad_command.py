# AUTOGENERATED FROM C#. DO NOT MODIFY.

from abc import ABC
from tdw.commands.textured_quad_command import TexturedQuadCommand


class AdjustTexturedQuadCommand(TexturedQuadCommand, ABC):
    """
    These commands adjust an existing textured quad.
    """

    def __init__(self, id: int):
        """
        :param id: The ID of the non-physics object.
        """

        super().__init__(id=id)

