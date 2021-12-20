from enum import Enum
from json import loads
from typing import Dict, List
from pathlib import Path
from pkg_resources import resource_filename


class VerticalSpatialRelations(Enum):
    """
    Enum values to define vertical spatial relations.
    """

    on_top_of = 1
    on_shelf = 2


def __get() -> Dict[VerticalSpatialRelations, Dict[str, List[str]]]:
    """
    :return: A dictionary of vertical spatial relations.
    """

    data = loads(Path(resource_filename(__name__, "vertical_spatial_relations.json")).read_text())
    spatial_relations: Dict[VerticalSpatialRelations, Dict[str, List[str]]] = dict()
    for r in data:
        spatial_relations[VerticalSpatialRelations[r]] = dict()
        for c in data[r]:
            spatial_relations[VerticalSpatialRelations[r]][c] = data[r][c]
    return spatial_relations


VERTICAL_SPATIAL_RELATIONS: Dict[VerticalSpatialRelations, Dict[str, List[str]]] = __get()
