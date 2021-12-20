from enum import Enum
from json import loads
from typing import Dict, List
from pathlib import Path
from pkg_resources import resource_filename


class SpatialRelation(Enum):
    """
    Enum values to define spatial relations.
    """

    on_top_of = 1
    on_shelf = 2
    left_or_right_of = 3


def __get() -> Dict[SpatialRelation, Dict[str, List[str]]]:
    """
    :return: A dictionary of spatial relations.
    """

    data = loads(Path(resource_filename(__name__, "spatial_relations.json")).read_text())
    spatial_relations: Dict[SpatialRelation, Dict[str, List[str]]] = dict()
    for r in data:
        spatial_relations[SpatialRelation[r]] = dict()
        for c in data[r]:
            spatial_relations[SpatialRelation[r]][c] = data[r][c]
    return spatial_relations


SPATIAL_RELATIONS: Dict[SpatialRelation, Dict[str, List[str]]] = __get()
