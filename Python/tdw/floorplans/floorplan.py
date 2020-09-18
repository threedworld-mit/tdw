from pkg_resources import resource_filename
import json
from pathlib import Path
from platform import system
from requests import head
from tdw.librarian import SceneLibrarian
from tdw.object_init_data import TransformInitData, RigidbodyInitData, AudioInitData


class Floorplan:
    def __init__(self, scene: str, layout: int):
        floorplans = json.loads(Path(resource_filename(__name__, "floorplan_layouts.json")).
                                read_text(encoding="utf-8"))
        if scene not in floorplans:
            raise Exception(f"Floorplan not found: {scene}")
        layout = str(layout)
        if layout not in floorplans[scene]:
            raise Exception(f"Layout not found: {layout}")
        
        print(floorplans.keys())


Floorplan("2a", 0)

