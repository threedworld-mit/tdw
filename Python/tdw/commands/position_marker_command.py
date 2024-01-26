# AUTOGENERATED FROM C#. DO NOT MODIFY.

from abc import ABC
from tdw.commands.non_physics_object_command import NonPhysicsObjectCommand


class PositionMarkerCommand(NonPhysicsObjectCommand, ABC):
    """
    These commands show or hide position markers. They can be useful for debugging.
    """

    def __init__(self, id: int):
        """
        :param id: The ID of the non-physics object.
        """

        super().__init__(id=id)
