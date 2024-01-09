# AUTOGENERATED FROM C#. DO NOT MODIFY.

from abc import ABC
from tdw.commands.visual_effect_command import VisualEffectCommand


class AdjustVisualEffectCommand(VisualEffectCommand, ABC):
    """
    These commands adjust non-physical visual effects.
    """

    def __init__(self, id: int):
        """
        :param id: The ID of the non-physics object.
        """

        super().__init__(id=id)
