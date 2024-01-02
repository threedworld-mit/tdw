# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.visual_effect_command import VisualEffectCommand


class DestroyVisualEffect(VisualEffectCommand):
    """
    Destroy a non-physical effect object.
    """

    def __init__(self, id: int):
        """
        :param id: The ID of the non-physics object.
        """

        super().__init__(id=id)

