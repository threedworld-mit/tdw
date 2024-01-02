# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.position_marker_command import PositionMarkerCommand
from typing import Dict


class AddPositionMarker(PositionMarkerCommand):
    """
    Create a non-physics, non-interactive marker at a position in the scene.
    """

    def __init__(self, id: int, position: Dict[str, float], scale: float = 0.05, color: Dict[str, float] = None, shape: str = "sphere"):
        """
        :param id: The ID of the non-physics object.
        :param position: Add a marker at this position.
        :param scale: The scale of the marker. If the scale is 1, a cube and square will be 1 meter wide and a sphere and circle will be 1 meter in diameter.
        :param color: The color of the marker. The default color is red.
        :param shape: The shape of the position marker object.
        """

        super().__init__(id=id)
        """:field
        Add a marker at this position.
        """
        self.position: Dict[str, float] = position
        """:field
        The scale of the marker. If the scale is 1, a cube and square will be 1 meter wide and a sphere and circle will be 1 meter in diameter.
        """
        self.scale: float = scale
        if color is None:
            """:field
            The color of the marker. The default color is red.
            """
            self.color: Dict[str, float] = {"r": 1, "g": 0, "b": 0, "a": 1}
        else:
            self.color = color
        """:field
        The shape of the position marker object.
        """
        self.shape: str = shape
