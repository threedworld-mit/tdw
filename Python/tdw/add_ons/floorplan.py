from typing import List
import re
from json import loads
from pathlib import Path
from pkg_resources import resource_filename
from tdw.add_ons.add_on import AddOn
from tdw.controller import Controller


class Floorplan(AddOn):
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

        # Example: "1a"
        if re.match(r"^([1245][abc])", scene) is not None:
            scene_name = f"floorplan_{scene}"
            scene_index = scene[0]
        elif re.match(r"^floorplan_([1245][abc])", scene) is not None:
            scene_name = scene
            scene_index = scene[-2]
        else:
            raise Exception(f"Invalid scene: {scene}")
        layout_index = str(layout)
        floorplans = loads(Path(resource_filename(__name__, "floorplan_layouts.json")).
                           read_text(encoding="utf-8"))
        if layout_index not in floorplans[scene_index]:
            raise Exception(f"Layout not found: {layout_index}")

        objects = floorplans[scene_index][layout_index]
        # Load the scene and add post-processing commands.
        self.commands = [Controller.get_add_scene(scene_name=scene_name),
                         {"$type": "set_aperture",
                          "aperture": 8.0},
                         {"$type": "set_focus_distance",
                          "focus_distance": 2.25},
                         {"$type": "set_post_exposure",
                          "post_exposure": 0.4},
                         {"$type": "set_ambient_occlusion_intensity",
                          "intensity": 0.175},
                         {"$type": "set_ambient_occlusion_thickness_modifier",
                          "thickness": 3.5}]
        # Add objects.
        for o in objects:
            object_id = Controller.get_unique_id()
            self.commands.extend(Controller.get_add_physics_object(model_name=o["name"],
                                                                   library=o["library"],
                                                                   position=o["position"],
                                                                   rotation=o["rotation"],
                                                                   scale_factor=o["scale_factor"],
                                                                   kinematic=o["kinematic"],
                                                                   gravity=o["gravity"],
                                                                   object_id=object_id))

    def get_initialization_commands(self) -> List[dict]:
        return []

    def on_send(self, resp: List[bytes]) -> None:
        pass
