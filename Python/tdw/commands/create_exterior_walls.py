# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.proc_gen_walls_command import ProcGenWallsCommand
from typing import Dict, List


class CreateExteriorWalls(ProcGenWallsCommand):
    """
    Create the exterior walls. This must be called before all other ProcGenRoomCommands.
    """

    def __init__(self, walls: List[Dict[str, float]]):
        """
        :param walls: List of walls as (x, y) points on a grid.
        """

        super().__init__(walls=walls)
