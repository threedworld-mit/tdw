from enum import Enum


class CollisionAudioType(Enum):
    """
    The "type" of a collision, defined by the motion of the object.
    """

    none = 1
    impact = 2
    scrape = 4
    roll = 8
