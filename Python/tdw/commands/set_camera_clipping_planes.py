# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.avatar_command import AvatarCommand


class SetCameraClippingPlanes(AvatarCommand):
    """
    Set the near and far clipping planes of the avatar's camera.
    """

    def __init__(self, near: float = 0.1, far: float = 100, avatar_id: str = "a"):
        """
        :param near: The distance of the near clipping plane.
        :param far: The distance of the far clipping plane.
        :param avatar_id: The ID of the avatar.
        """

        super().__init__(avatar_id=avatar_id)
        """:field
        The distance of the near clipping plane.
        """
        self.near: float = near
        """:field
        The distance of the far clipping plane.
        """
        self.far: float = far