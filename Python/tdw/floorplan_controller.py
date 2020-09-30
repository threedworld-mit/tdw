from pathlib import Path
from json import loads
from pkg_resources import resource_filename
from typing import List
from tdw.controller import Controller
from tdw.object_init_data import TransformInitData, AudioInitData


class FloorplanController(Controller):
    """
    A controller that can create an interior scene populated with objects.

    ```python
    from tdw.floorplan_controller import FloorplanController

    c = FloorplanController()
    init_commands = c.get_scene_init_commands(scene="2a", layout=0, audio=True)
    c.communicate(init_commands)
    ```

    """

    def get_scene_init_commands(self, scene: str, layout: int, audio: bool) -> List[dict]:
        """
        Get commands to create a scene and populate it with objects.

        Valid scenes and layouts:

        | `scene` | `layout` |
        | --- | --- |
        | 1a, 1b, or 1c | 0, 1, or 2 |
        | 2a, 2b, or 2c | 0, 1, or 2 |
        | 4a, 4b, or 4c | 0, 1, or 2 |
        | 5a, 5b, or 5c | 0, 1, or 2 |

        :param scene: The name of the scene. Corresponds to a record named: `floorplan_[scene]`.
        :param layout: The layout index.
        :param audio: If True, instantiate physics values per object from audio properties.

        :return: A list of commands to initialize the scene and populate it with objects.
        """

        scene = scene
        scene_index = scene[0]
        layout = str(layout)

        floorplans = loads(Path(resource_filename(__name__, "floorplan_layouts.json")).
                           read_text(encoding="utf-8"))
        if scene_index not in floorplans:
            raise Exception(f"Floorplan not found: {scene_index}")
        if layout not in floorplans[scene_index]:
            raise Exception(f"Layout not found: {layout}")

        objects = floorplans[scene_index][layout]

        commands = [self.get_add_scene(scene_name=f"floorplan_{scene}"),
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
        # Deserialize the JSON data.
        if audio:
            objects = [AudioInitData(**o) for o in objects]
        else:
            objects = [TransformInitData(**o) for o in objects]
        # Get the commands to initialize each object.
        for o in objects:
            object_id, object_commands = o.get_commands()
            commands.extend(object_commands)
        return commands
