from typing import List, Dict
from pathlib import Path
from pkg_resources import resource_filename
import json
from tdw.scene_data.region_bounds import RegionBounds
from tdw.scene_data.region_walls import RegionWalls
from tdw.scene_data.interior_region import InteriorRegion
from tdw.scene_data.room import Room


class _Decoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):
        if "region_id" in dct:
            region_bounds = RegionBounds(region_id=dct["region_id"], center=dct["center"], bounds=dct["bounds"])
            region_bounds.x_min = dct["x_min"]
            region_bounds.z_min = dct["z_min"]
            region_bounds.x_max = dct["x_max"]
            region_bounds.z_max = dct["z_max"]
            return region_bounds
        elif "non_continuous_walls" in dct:
            return RegionWalls(**dct)
        elif "bounds" in dct and "walls" in dct:
            return InteriorRegion(**dct)
        elif "main_region" in dct:
            return Room(**dct)
        else:
            return {k: InteriorScene(name=k, rooms=v) for k, v in dct.items()}


class InteriorScene:
    """
    Cached interior scene data.
    """

    def __init__(self, name: str, rooms: List[Room]):
        """
        :param name: The name of the scene.
        :param rooms: A list of [`Room`] data.
        """

        """:field
        The name of the scene.
        """
        self.name: str = name
        """:field
        A list of [`Room`] data.
        """
        self.rooms: List[Room] = rooms


INTERIOR_SCENES: Dict[str, InteriorScene] = json.loads(Path(resource_filename(__name__, "rooms.json")).read_text(),
                                                       cls=_Decoder)
