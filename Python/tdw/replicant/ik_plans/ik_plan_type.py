from enum import IntEnum


class IkPlanType(IntEnum):
    """
    Enum values defining IK plans.
    """

    vertical_horizontal = 0  # [`VerticalHorizontal`](vertical_horizontal.md)
    reset = 1  # [`Reset`](reset.md)
