# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.command import Command


class AdjustPointLightsIntensityBy(Command):
    """
    Adjust the intensity of all point lights in the scene by a value. Note that many scenes don't have any point lights.
    """

    def __init__(self, intensity: float):
        """
        :param intensity: Adjust all point lights in the scene by this value.
        """

        super().__init__()
        """:field
        Adjust all point lights in the scene by this value.
        """
        self.intensity: float = intensity
