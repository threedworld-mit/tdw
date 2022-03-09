from enum import Enum


class ContainerColliderTag(Enum):
    """
    A tag for a container collider.
    """

    on = 1  # An object on top of a surface, for example a plate on a table.
    inside = 2  # An object inside a cavity or basin, for example a toy in a basket or a plate in a sink.
    enclosed = 4  # An object inside an enclosed cavity, for example a pan in an oven.
