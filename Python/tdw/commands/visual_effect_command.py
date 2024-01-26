# AUTOGENERATED FROM C#. DO NOT MODIFY.

from abc import ABC
from tdw.commands.non_physics_object_command import NonPhysicsObjectCommand


class VisualEffectCommand(NonPhysicsObjectCommand, ABC):
    """
    These commands can be used for non-physical visual effects in the scene.
    """

    def __init__(self, id: int):
        """
        :param id: The ID of the non-physics object.
        """

        super().__init__(id=id)
