# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.object_command import ObjectCommand
from typing import Dict


class RotateObjectAround(ObjectCommand):
    """
    Rotate an object by a given angle and axis around a position.
    """

    def __init__(self, id: int, position: Dict[str, float], angle: float, axis: str = "yaw"):
        """
        :param id: The unique object ID.
        :param position: Rotate around this position in world space coordinates.
        :param angle: The angle of rotation in degrees.
        :param axis: The axis of rotation.
        """

        super().__init__(id=id)
        """:field
        The axis of rotation.
        """
        self.axis: str = axis
        """:field
        The angle of rotation in degrees.
        """
        self.angle: float = angle
        """:field
        Rotate around this position in world space coordinates.
        """
        self.position: Dict[str, float] = position
