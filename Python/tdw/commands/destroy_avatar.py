# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.avatar_command import AvatarCommand


class DestroyAvatar(AvatarCommand):
    """
    Destroy an avatar.
    """

    def __init__(self, avatar_id: str = "a"):
        """
        :param avatar_id: The ID of the avatar.
        """

        super().__init__(avatar_id=avatar_id)
