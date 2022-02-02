from typing import Callable, Dict
from tdw.librarian import ModelRecord
from tdw.cardinal_direction import CardinalDirection
from tdw.scene_data.region_walls import RegionWalls


class LateralSubArrangement:
    """
    Data for a sub-arrangement of a lateral arrangement, for example a kitchen counter.
    This contains the function that will be used to create the sub-arrangement.
    """

    def __init__(self, category: str, function: Callable[[ModelRecord, Dict[str, float], CardinalDirection,
                                                          CardinalDirection, RegionWalls], None],
                 position_offset_multiplier: int = 1):
        """
        :param category: The proc-gen category.
        :param function: The function that will be used to create the sub-arrangement.
        :param position_offset_multiplier: After creating the sub-arrangement, offset the lateral arrangement position by the half of extents of the root object multiplied by this factor.
        """

        self.category: str = category
        self.function: Callable[[ModelRecord, Dict[str, float],
                                 CardinalDirection, CardinalDirection,
                                 RegionWalls], None] = function
        self.position_offset_multiplier: int = position_offset_multiplier
