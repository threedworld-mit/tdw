# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.object_type_command import ObjectTypeCommand
from typing import Dict


class ApplyForceAtPosition(ObjectTypeCommand):
    """
    Apply a force to an object from a position. From Unity documentation: For realistic effects position should be approximately in the range of the surface of the rigidbody. Note that when position is far away from the center of the rigidbody the applied torque will be unrealistically large.
    """

    def __init__(self, id: int, force: Dict[str, float] = None, position: Dict[str, float] = None):
        """
        :param id: The unique object ID.
        :param force: The vector of a force to be applied in world space.
        :param position: The origin of the force in world coordinates.
        """

        super().__init__(id=id)
        if force is None:
            """:field
            The vector of a force to be applied in world space.
            """
            self.force: Dict[str, float] = {"x": 0, "y": 0, "z": 0}
        else:
            self.force = force
        if position is None:
            """:field
            The origin of the force in world coordinates.
            """
            self.position: Dict[str, float] = {"x": 0, "y": 0, "z": 0}
        else:
            self.position = position
