# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.send_data_command import SendDataCommand


class SendSystemInfo(SendDataCommand):
    """
    Send system and hardware information.
    """

    def __init__(self, frequency: str = "once"):
        """
        :param frequency: The frequency at which data is sent.
        """

        super().__init__(frequency=frequency)

