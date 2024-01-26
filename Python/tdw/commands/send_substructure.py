# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.send_data_command import SendDataCommand


class SendSubstructure(SendDataCommand):
    """
    Send visual material substructure data for a single object.
    """

    def __init__(self, id: int, frequency: str = "once"):
        """
        :param id: The unique ID of the object.
        :param frequency: The frequency at which data is sent.
        """

        super().__init__(frequency=frequency)
        """:field
        The unique ID of the object.
        """
        self.id: int = id