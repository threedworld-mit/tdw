from enum import Enum


class CollisionAudioType(Enum):
    """
    This class is used only in PyImpact, which has been deprecated. See: [`Clatter`](../add_ons/clatter.md).

    The "type" of a collision, defined by the motion of the object.
    """

    none = 1
    impact = 2
    scrape = 4
    roll = 8
