from enum import Enum


class ScrapeMaterial(Enum):
    """
    An audio material used for a scrape event.
    """

    plywood = 0
    ceramic = 1
    pvc = 2
    rough_wood = 3
    acrylic = 4
    sanded_acrylic = 5
    vinyl = 6
    poplar_wood = 7
