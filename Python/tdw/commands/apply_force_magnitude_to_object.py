# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.object_type_command import ObjectTypeCommand


class ApplyForceMagnitudeToObject(ObjectTypeCommand):
    """
    Apply a force of a given magnitude along the forward directional vector of the object.
    """

    def __init__(self, id: int, magnitude: float):
        """
        :param id: The unique object ID.
        :param magnitude: The magnitude of the force.
        """

        super().__init__(id=id)
        """:field
        The magnitude of the force.
        """
        self.magnitude: float = magnitude
