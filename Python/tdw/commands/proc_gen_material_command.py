# AUTOGENERATED FROM C#. DO NOT MODIFY.

from abc import ABC
from tdw.commands.proc_gen_room_command import ProcGenRoomCommand


class ProcGenMaterialCommand(ProcGenRoomCommand, ABC):
    """
    These commands add a material to part of the proc-gen room.
    """

    def __init__(self, name: str):
        """
        :param name: The name of the material. The material must already be loaded in memory.
        """

        super().__init__()
        """:field
        The name of the material. The material must already be loaded in memory.
        """
        self.name: str = name