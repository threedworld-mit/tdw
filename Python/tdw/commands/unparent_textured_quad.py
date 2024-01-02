# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.adjust_textured_quad_command import AdjustTexturedQuadCommand


class UnparentTexturedQuad(AdjustTexturedQuadCommand):
    """
    Unparent a textured quad from a parent object. If the textured quad doesn't have a parent object, this command doesn't do anything.
    """

    def __init__(self, id: int):
        """
        :param id: The ID of the non-physics object.
        """

        super().__init__(id=id)

