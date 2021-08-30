from enum import Enum


class JointType(Enum):
    """
    Types of joint articulation.
    """

    revolute = 1
    spherical = 2
    prismatic = 4
    fixed_joint = 8
