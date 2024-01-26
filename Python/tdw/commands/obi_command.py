# AUTOGENERATED FROM C#. DO NOT MODIFY.

from abc import ABC
from tdw.commands.command import Command


class ObiCommand(Command, ABC):
    """
    These commands are used for aspects of an Obi simulation. There are other Obi-related commands as well; search for "obi" in this document.
    """

    def __init__(self):
        """
        (no arguments)
        """

        super().__init__()