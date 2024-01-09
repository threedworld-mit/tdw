# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.adjust_line_renderer_command import AdjustLineRendererCommand
from typing import Dict, List


class AddPointsToLineRenderer(AdjustLineRendererCommand):
    """
    Add points to an existing line in the scene.
    """

    def __init__(self, id: int, points: List[Dict[str, float]]):
        """
        :param id: The ID of the non-physics object.
        :param points: Additional points on the line.
        """

        super().__init__(id=id)
        """:field
        Additional points on the line.
        """
        self.points: List[Dict[str, float]] = points