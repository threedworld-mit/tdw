# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.directional_light_command import DirectionalLightCommand


class RotateDirectionalLightBy(DirectionalLightCommand):
    """
    Rotate the directional light (the sun) by an angle and axis. This command will change the direction of cast shadows, which could adversely affect lighting that uses an HDRI skybox, Therefore this command should only be used for interior scenes where the effect of the skybox is less apparent. The original relationship between directional (sun) light and HDRI skybox can be restored by using the reset_directional_light_rotation command.
    """

    def __init__(self, angle: float, axis: str = "yaw", index: int = 0):
        """
        :param angle: The angle of rotation in degrees.
        :param axis: The axis of rotation.
        :param index: The index of the light. This should almost always be 0. The scene "archviz_house" has two directional lights; for this scene, index can be 0 or 1.
        """

        super().__init__(index=index)
        """:field
        The axis of rotation.
        """
        self.axis: str = axis
        """:field
        The angle of rotation in degrees.
        """
        self.angle: float = angle
