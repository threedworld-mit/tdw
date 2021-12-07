from enum import Enum


class ShelfItemsType(Enum):
    """
    Enum for the items on a shelf.
    """

    none = 1  # An empty shelf.
    random = 2  # A shelf with random items.