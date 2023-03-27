from typing import List
import re
from json import loads
from pathlib import Path
from pkg_resources import resource_filename
from tdw.controller import Controller
from tdw.add_ons.floorplan import Floorplan
from typing import List, Dict
from tdw.librarian import VisualEffectLibrarian


class FloorplanFlood(Floorplan):
    """
    Initialize a scene populated by objects in pre-scripted layouts.

    There are four scenes (1, 2, 4, 5), each with three visual variants (a, b, c). Each scene has three different object layouts (0, 1, 2).

    ```python
    from tdw.controller import Controller
    from tdw.add_ons.floorplan import Floorplan

    c = Controller()
    f = Floorplan()
    f.init_scene(scene="1a", layout=0)
    c.add_ons.append(f)
    c.communicate([])
    ```
    """

    def __init__(self):
        """
        (no parameters)
        """

        super().__init__()
        self.initialized = True
        self.floors = {}
        self.flooded_floors: Dict[str, float]  = dict()
        self.lib = VisualEffectLibrarian()

    def init_scene(self, scene: str, layout: int) -> None:
        """
        Set commands to initialize the scene. On the next frame, the scene will be initialized.
        Valid scenes and layouts:
        | `scene` | `layout` |
        | --- | --- |
        | 1a, 1b, or 1c | 0, 1, or 2 |
        | 2a, 2b, or 2c | 0, 1, or 2 |
        | 4a, 4b, or 4c | 0, 1, or 2 |
        | 5a, 5b, or 5c | 0, 1, or 2 |
        Where `1a` is the scene number (1) and visual variant (a).
        :param scene: The name of the floorplan scene to load. Can be just the suffix of the scene to load (such as `"1a"`) or the full name of the scene (such as `"floorplan_1a"`).
        :param layout: The layout index.
        """
        super().init_scene(scene, layout)

        # Example: "1a"
        if re.match(r"^([1245][abc])", scene) is not None:
            scene_name = f"floorplan_{scene}"
            scene_index = scene[0]
        elif re.match(r"^floorplan_([1245][abc])", scene) is not None:
            scene_name = scene
            scene_index = scene[-2]
        else:
            raise Exception(f"Invalid scene: {scene}")
        floorplan_floods = loads(Path(resource_filename(__name__, "floorplan_floods.json")).
                           read_text(encoding="utf-8"))
        # Get the floors for this floorplan.
        self.floors = floorplan_floods[scene_index[0:1]]
        for i in range(len(self.floors) - 1):
            floor_index = str(i+1)
            floor = self.floors[floor_index]
            floor_name = floor["name"]
            floor_id = Controller.get_unique_id()
            floor_position = floor["position"]
            record = self.lib.get_record(floor_name)
            self.commands.append({"$type": "add_visual_effect",
                             "id": floor_id,
                             "name": floor_name,
                             "url": record.get_url(),
                             "position": floor_position,
                             "rotation": {"x": 90, "y": 0, "z": 0}})
            # Add to dictionary of currently-flooded floors. Position will include current height (flood level).
            self.flooded_floors[floor_name] = floor_id

    def get_initialization_commands(self) -> List[dict]:
        return []

    def on_send(self, resp: List[bytes]) -> None:
        pass
        
    def get_adjacent_floors(self, floor: int):
        floor_index = str(floor)
        if floor_index not in self.floors:
            raise Exception(f"Floor not found: {floor_index}")
        adjacents = self.floors[floor_index]["adjacent_floors"]
        return adjacents

    def set_flood_height(self, floor: int, height: float):
        floor_index = str(floor)
        if floor_index not in self.floors:
            raise Exception(f"Floor not found: {floor_index}")
        floor_name = self.floors[floor_index]["name"]
        floor_id = self.flooded_floors[floor_name]
        floor_position = self.floors[floor_index]["position"]
        floor_position["y"] = floor_position["y"] + height
        self.floors[floor_index]["position"] = floor_position
        self.commands.append({"$type": "teleport_visual_effect", 
                              "position": floor_position, 
                              "id": floor_id})
   
        
        
        
