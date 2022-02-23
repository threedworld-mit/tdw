from enum import Enum


class TriggerColliderShape(Enum):
    """
    The shape of a trigger collider.
    """

    box = "cube"
    sphere = "sphere"
    cylinder = "cylinder"
