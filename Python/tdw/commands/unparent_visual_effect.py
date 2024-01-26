# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.adjust_visual_effect_command import AdjustVisualEffectCommand


class UnparentVisualEffect(AdjustVisualEffectCommand):
    """
    Unparent a non-physical visual effect from a parent object. If the visual effect doesn't have a parent object, this command doesn't do anything.
    """

    def __init__(self, id: int):
        """
        :param id: The ID of the non-physics object.
        """

        super().__init__(id=id)
