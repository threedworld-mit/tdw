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

    c = FloorplanController(scene="2a", layout=0, audio=True)
    init_commands = c.get_scene_init_commands()
    c.communicate(init_commands)
    ```

    Valid scenes and layouts:

    | `scene` | `layout` |
    | --- | --- |
    | 2a | 0 |

    In addition to the fields in `Controller`, there is an `objects` field, a list of initialization data.

    """
    def __init__(self, scene: str, layout: int, audio: bool = False, port: int = 1071, check_version: bool = True,
                 launch_build: bool = True):
        """
        :param port: The port number.
        :param check_version: If true, the controller will check the version of the build and print the result.
        :param launch_build: If True, automatically launch the build.
        :param scene: The name of the scene. Corresponds to a record named: `floorplan_[scene]`.
        :param layout: The layout index.
        :param audio: If True, `objects` will be [`AudioInitData`](object_init_data.md#audioinitdata) and will be assigned physics values based on their audio properties. If False, `objects` will be [`TransformInitData`](object_init_data.md#transforminitdata).
        """

        self.scene = scene
        self.layout = str(layout)
        self.audio = audio

        floorplans = loads(Path(resource_filename(__name__, "floorplan_layouts.json")).
                           read_text(encoding="utf-8"))
        if self.scene not in floorplans:
            raise Exception(f"Floorplan not found: {self.scene}")
        if self.layout not in floorplans[self.scene]:
            raise Exception(f"Layout not found: {self.layout}")

        objects = floorplans[self.scene][self.layout]
        # Deserialize the JSON data.
        if audio:
            self.objects = [AudioInitData(**o) for o in objects]
        else:
            self.objects = [TransformInitData(**o) for o in objects]

        super().__init__(port=port, check_version=check_version, launch_build=launch_build)

    def get_scene_init_commands(self) -> List[dict]:
        """
        :return: A list of commands to initialize the scene and populate it with objects.
        """

        commands = [self.get_add_scene(scene_name=f"floorplan_{self.scene}")]
        # Get the commands to initialize each object.
        for o in self.objects:
            object_id, object_commands = o.get_commands()
            commands.extend(object_commands)
        return commands
