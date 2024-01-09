# AUTOGENERATED FROM C#. DO NOT MODIFY.

from abc import ABC
from tdw.commands.proc_gen_room_command import ProcGenRoomCommand
from typing import Dict, List


class ProcGenWallsCommand(ProcGenRoomCommand, ABC):
    """
    These commands involve placing walls in a procedural room. (See description for Proc Gen Room Command.)
    """

    def __init__(self, walls: List[Dict[str, float]]):
        """
        :param walls: List of walls as (x, y) points on a grid.
        """

        super().__init__()
        """:field
        List of walls as (x, y) points on a grid.
        """
        self.walls: List[Dict[str, float]] = walls