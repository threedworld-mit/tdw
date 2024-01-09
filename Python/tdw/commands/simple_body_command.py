# AUTOGENERATED FROM C#. DO NOT MODIFY.

from abc import ABC
from tdw.commands.avatar_type_command import AvatarTypeCommand


class SimpleBodyCommand(AvatarTypeCommand, ABC):
    """
    These commands are only valid for a SimpleBodyAvatar.
    """

    def __init__(self, avatar_id: str = "a"):
        """
        :param avatar_id: The ID of the avatar.
        """

        super().__init__(avatar_id=avatar_id)
