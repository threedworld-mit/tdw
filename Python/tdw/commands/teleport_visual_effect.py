# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.adjust_visual_effect_command import AdjustVisualEffectCommand
from typing import Dict


class TeleportVisualEffect(AdjustVisualEffectCommand):
    """
    Teleport a non-physical visual effect to a new position.
    """

    def __init__(self, id: int, position: Dict[str, float]):
        """
        :param id: The ID of the non-physics object.
        :param position: The new position of the visual effect.
        """

        super().__init__(id=id)
        """:field
        The new position of the visual effect.
        """
        self.position: Dict[str, float] = position