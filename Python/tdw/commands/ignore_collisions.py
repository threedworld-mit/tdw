# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.object_command import ObjectCommand


class IgnoreCollisions(ObjectCommand):
    """
    Set whether one object should ignore collisions with another object. By default, objects never ignore any collisions.
    """

    def __init__(self, id: int, other_id: int, ignore: bool = True):
        """
        :param id: The unique object ID.
        :param other_id: The ID of the other object.
        :param ignore: If True, ignore collisions with the other object. If False, listen for collisions with the other object.
        """

        super().__init__(id=id)
        """:field
        The ID of the other object.
        """
        self.other_id: int = other_id
        """:field
        If True, ignore collisions with the other object. If False, listen for collisions with the other object.
        """
        self.ignore: bool = ignore
