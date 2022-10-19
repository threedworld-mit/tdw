from enum import IntEnum
from typing import List


class ReplicantBodyPart(IntEnum):
    """
    The name of each Replicant body part.
    """

    hand_l = 0
    hand_r = 1
    head = 2
    lowerarm_l = 3
    lowerarm_r = 4
    lowerleg_l = 5
    lowerleg_r = 6
    spine_01 = 7
    spine_02 = 8
    spine_03 = 9
    upperarm_l = 10
    upperarm_r = 11
    upperleg_l = 12
    upperleg_r = 13


# The body part enum values in a list.
BODY_PARTS: List[ReplicantBodyPart] = [r for r in ReplicantBodyPart]
