from json import loads
from pathlib import Path
from pkg_resources import resource_filename
from tdw.controller import Controller
from tdw.add_ons.floorplan import Floorplan
from typing import Dict, List


class FloorplanFlood(Floorplan):
    """
    Initialize a scene populated by objects in pre-scripted layouts.

    Then, create a set of flood objects for each floor section in the floorplan.

    This is a subclass of [`Floorplan`](floorplan.md).
    """

    # Load and cache the floorplan flood data.
    _FLOOD_DATA = loads(Path(resource_filename(__name__, "floorplan_floods.json")).read_text(encoding="utf-8"))

    def __init__(self):
        """
        (no parameters)
        """

        super().__init__()
        self._floors = {}
        self._flooded_floors: Dict[str, float] = dict()

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

        This will also load the flood effects at their initial positions below the floor.

        :param scene: The name of the floorplan scene to load. Can be just the suffix of the scene to load (such as `"1a"`) or the full name of the scene (such as `"floorplan_1a"`).
        :param layout: The layout index.
        """

        super().init_scene(scene, layout)
        # Get the floors for this floorplan. Create flood objects for each floor.
        # These will be at 0 in Y, and not visible until their height is adjusted.
        # The index is the number of the scene, i.e. "1".
        self._floors = FloorplanFlood._FLOOD_DATA[scene[0]]
        for i in range(len(self._floors)):
            floor = self._floors[str(i + 1)]
            floor_name = floor["name"]
            floor_id = Controller.get_unique_id()
            self.commands.append(Controller.get_add_visual_effect(name=floor_name,
                                                                  effect_id=floor_id,
                                                                  position=floor["position"],
                                                                  rotation={"x": 90, "y": 0, "z": 0},
                                                                  library="flood_effects.json"))
            # Add to dictionary of currently-flooded floors. Position will include current height (flood level).
            self._flooded_floors[floor_name] = floor_id

    def get_adjacent_floors(self, index: int) -> List[int]:
        """
        Return a list of the floors adjacent to the floor parameter.

        :param index: The floor index.
        """

        floor_index = str(index)
        if floor_index not in self._floors:
            raise Exception(f"Floor not found: {floor_index}")
        return self._floors[floor_index]["adjacent_floors"]

    def set_flood_height(self, index: int, height: float) -> None:
        """
        Set the height (Y) of a floor flood object.

        :param index: The index of the flood visual effect.
        :param height: The height to set the floor object to.
        """

        floor_index = str(index)
        if floor_index not in self._floors:
            raise Exception(f"Floor not found: {floor_index}")
        floor_name = self._floors[floor_index]["name"]
        floor_id = self._flooded_floors[floor_name]
        floor_position = self._floors[floor_index]["position"]
        floor_position["y"] = floor_position["y"] + height
        self._floors[floor_index]["position"] = floor_position
        self.commands.append({"$type": "teleport_visual_effect", 
                              "position": floor_position, 
                              "id": floor_id})
