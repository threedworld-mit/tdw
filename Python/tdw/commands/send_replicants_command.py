# AUTOGENERATED FROM C#. DO NOT MODIFY.

from abc import ABC
from tdw.commands.send_single_data_command import SendSingleDataCommand


class SendReplicantsCommand(SendSingleDataCommand, ABC):
    """
    These commands send Replicants output data for different types of Replicants.
    """

    def __init__(self):
        """
        (no arguments)
        """

        super().__init__()
