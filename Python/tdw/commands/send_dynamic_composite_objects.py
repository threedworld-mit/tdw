# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.send_single_data_command import SendSingleDataCommand


class SendDynamicCompositeObjects(SendSingleDataCommand):
    """
    Send dynamic data for every composite object in the scene.
    """

    def __init__(self, frequency: str = "once"):
        """
        :param frequency: The frequency at which data is sent.
        """

        super().__init__(frequency=frequency)
