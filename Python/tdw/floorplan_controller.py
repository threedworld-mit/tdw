from pathlib import Path
from json import loads
from pkg_resources import resource_filename
from typing import List
from tdw.controller import Controller


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

    def get_scene_init_commands(self, scene: str, layout: int) -> List[dict]:
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
        for o in objects:
            object_id = self.get_unique_id()
            commands.extend(self.get_add_physics_object(model_name=o["name"],
                                                        library=o["library"],
                                                        position=o["position"],
                                                        rotation=o["rotation"],
                                                        scale_factor=o["scale_factor"],
                                                        kinematic=o["kinematic"],
                                                        gravity=o["gravity"],
                                                        object_id=object_id))
        return commands
