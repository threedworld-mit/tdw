from enum import Enum


class AvatarBody(Enum):
    """
    A body type for an [embodied avatar](embodied_avatar.md).
    """

    cube = 1
    capsule = 2
    cylinder = 4
    sphere = 8
