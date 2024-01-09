# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.adjust_visual_effect_command import AdjustVisualEffectCommand
from typing import Dict


class ScaleVisualEffect(AdjustVisualEffectCommand):
    """
    Scale a non-physical visual effect by a factor.
    """

    def __init__(self, id: int, scale_factor: Dict[str, float] = None):
        """
        :param id: The ID of the non-physics object.
        :param scale_factor: Multiply the scale of the object by this vector. (For example, if scale_factor is (2,2,2), then the object's current size will double.)
        """

        super().__init__(id=id)
        if scale_factor is None:
            """:field
            Multiply the scale of the object by this vector. (For example, if scale_factor is (2,2,2), then the object's current size will double.)
            """
            self.scale_factor: Dict[str, float] = {"x": 1, "y": 1, "z": 1}
        else:
            self.scale_factor = scale_factor