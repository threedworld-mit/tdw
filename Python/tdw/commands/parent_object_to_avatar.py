# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.object_command import ObjectCommand


class ParentObjectToAvatar(ObjectCommand):
    """
    Parent an object to an avatar. The object won't change its position or rotation relative to the avatar. Only use this command in non-physics simulations.
    """

    def __init__(self, id: int, avatar_id: str = "a", sensor: bool = True):
        """
        :param id: The unique object ID.
        :param avatar_id: The ID of the avatar in the scene.
        :param sensor: If true, parent the object to the camera rather than the root object of the avatar.
        """

        super().__init__(id=id)
        """:field
        The ID of the avatar in the scene.
        """
        self.avatar_id: str = avatar_id
        """:field
        If true, parent the object to the camera rather than the root object of the avatar.
        """
        self.sensor: bool = sensor
