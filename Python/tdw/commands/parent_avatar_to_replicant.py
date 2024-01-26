# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.replicant_base_command import ReplicantBaseCommand
from typing import Dict


class ParentAvatarToReplicant(ReplicantBaseCommand):
    """
    Parent an avatar to a Replicant. The avatar's position and rotation will always be relative to the Replicant's head. Usually you'll want to do this to add a camera to the Replicant.
    """

    def __init__(self, id: int, position: Dict[str, float], avatar_id: str = "a"):
        """
        :param id: The unique object ID.
        :param position: The position of the avatar relative to the Replicant's head.
        :param avatar_id: The ID of the avatar. It must already exist in the scene.
        """

        super().__init__(id=id)
        """:field
        The ID of the avatar. It must already exist in the scene.
        """
        self.avatar_id: str = avatar_id
        """:field
        The position of the avatar relative to the Replicant's head.
        """
        self.position: Dict[str, float] = position