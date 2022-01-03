from enum import Enum
from typing import Dict, List
from pkg_resources import resource_filename
from json import loads
from pathlib import Path


class RoomType(Enum):
    """
    The type of room.
    """

    kitchen = 1


def __get_lateral_relations() -> Dict[RoomType, Dict[str, List[str]]]:
    """
    :return: A dictionary of lateral spatial relations.
    """

    data = loads(Path(resource_filename(__name__, "lateral_spatial_relations.json")).read_text())
    spatial_relations: Dict[RoomType, Dict[str, List[str]]] = dict()
    for room_type in data:
        spatial_relations[RoomType[room_type]] = data[room_type]
    return spatial_relations


ROOM_TYPE_LATERAL_SPATIAL_RELATIONS: Dict[RoomType, Dict[str, List[str]]] = __get_lateral_relations()
