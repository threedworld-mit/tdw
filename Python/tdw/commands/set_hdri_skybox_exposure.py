# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.command import Command


class SetHdriSkyboxExposure(Command):
    """
    Set the exposure of the HDRI skybox to a given value.
    """

    def __init__(self, exposure: float):
        """
        :param exposure: The value to set the HDRI exposure to.
        """

        super().__init__()
        """:field
        The value to set the HDRI exposure to.
        """
        self.exposure: float = exposure