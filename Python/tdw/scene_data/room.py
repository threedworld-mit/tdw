from typing import List
from tdw.scene_data.interior_region import InteriorRegion


class Room:
    """
    A room in an interior environment. Rooms can be comprised of multiple box-shaped [regions](interior_region.md).
    Each room has 1 main region and *n* alcove regions.
    For example, an L shaped room has a main region ( `|` ) and one alcove ( `_` ).
    """

    def __init__(self, main_region: InteriorRegion, alcoves: List[InteriorRegion]):
        """
        :param main_region: The main [`InteriorRegion`](interior_region.md).
        :param alcoves: A list of alcove regions. Can be an empty list.
        """

        """:field
        The main [`InteriorRegion`](interior_region.md).
        """
        self.main_region: InteriorRegion = main_region
        """:field
        A list of alcove regions. Can be an empty list.
        """
        self.alcoves: List[InteriorRegion] = alcoves
