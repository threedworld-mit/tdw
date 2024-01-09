# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.send_single_data_command import SendSingleDataCommand


class SendSceneRegions(SendSingleDataCommand):
    """
    Receive data about the sub-regions within a scene in the scene. Only send this command after initializing the scene.
    """

    def __init__(self, frequency: str = "once"):
        """
        :param frequency: The frequency at which data is sent.
        """

        super().__init__(frequency=frequency)
