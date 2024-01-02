# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.directional_light_command import DirectionalLightCommand
from typing import Dict


class SetDirectionalLightColor(DirectionalLightCommand):
    """
    Set the color of the directional light (the sun).
    """

    def __init__(self, color: Dict[str, float], index: int = 0):
        """
        :param color: The color of the sunlight.
        :param index: The index of the light. This should almost always be 0. The scene "archviz_house" has two directional lights; for this scene, index can be 0 or 1.
        """

        super().__init__(index=index)
        """:field
        The color of the sunlight.
        """
        self.color: Dict[str, float] = color
