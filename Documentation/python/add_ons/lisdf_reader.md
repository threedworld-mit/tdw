# LisdfReader

`from tdw.add_ons.lisdf_reader import LisdfReader`

Import data from an [.sdf](http://sdformat.org/) or [.lisdf](https://learning-and-intelligent-systems.github.io/kitchen-worlds/tut-lisdf/) file into TDW as asset bundles and commands.

Models referenced by .sdf and .lisdf  files can't be directly added into TDW; they must first be converted into asset bundles. These asset bundles will be saved to the local disk, meaning that converting data to asset bundles is a one-time process.

When `read()` is called, asset bundles are automatically generated if they don't already exist. Then this add-on appends commands to the controller to add the objects to the scene.

***

## Fields

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

***

## Functions

#### \_\_init\_\_

**`LisdfReader()`**

(no parameters)

#### get_initialization_commands

**`self.get_initialization_commands()`**

This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

_Returns:_  A list of commands that will initialize this add-on.

#### on_send

**`self.on_send(resp)`**

This is called within `Controller.communicate(commands)` after commands are sent to the build and a response is received.

Use this function to send commands to the build on the next `Controller.communicate(commands)` call, given the `resp` response.
Any commands in the `self.commands` list will be sent on the *next* `Controller.communicate(commands)` call.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |

#### before_send

**`self.before_send(commands)`**

This is called within `Controller.communicate(commands)` before sending commands to the build. By default, this function doesn't do anything.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| commands |  List[dict] |  | The commands that are about to be sent to the build. |

#### get_early_initialization_commands

**`self.get_early_initialization_commands()`**

This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

These commands are added to the list being sent on `communicate()` *before* any other commands, including those added by the user and by other add-ons.

Usually, you shouldn't override this function. It is useful for a small number of add-ons, such as loading screens, which should initialize before anything else.

_Returns:_  A list of commands that will initialize this add-on.

#### read

**`self.read(lisdf_path, output_directory)`**

**`self.read(lisdf_path, output_directory, overwrite=False, cleanup=True, robot_metadata=None, send_commands=True, quiet=False, display="0", unity_editor_path=None, check_version=True)`**

Read an .lisdf file and send commands to the build to add the objects to the scene. This will launch a process in the Asset Bundle Creator Unity project. If it needs to generate new asset bundles, it can take a while to finish reading and generating.

Example source directory:

```
source_directory/
....scene/
........kitchen.lisdf
....models/
........counter/
............urdf/
................counter_0.urdf
................textured_objs/
....................01.obj
.................... (etc.)
........ (etc.)
```

- In this example, set `lisdf_path` to `"source_directory/scene/kitchen.lisdf"`
- The location of the .urdf files must match the relative path in `kitchen.lisdf` (in this case, `../models.counter/urdf/counter_0.urdf`)
- The location of the .obj files must match the relative path in the .urdf files (in this case, `counter_0.urdf` is expecting meshes to be in `textured_objs/`)

Example output directory after running `LisdfReader.read()`:

```
output_directory/
....counter_0/
........model.json
........Darwin/
............counter_0
........Linux/
............counter_0
........Windows/
............counter_0
....commands.json
....log.txt
```

- `model.json` is a JSON representation of the model structure. This can be useful for debugging.
- `Darwin/counter_0`, `Linux/counter_0` and `Windows/counter_0` are the platform-specific asset bundles.
- `commands.json` is the list of commands that can be sent to the build. They will be sent automatically if the `send_commands=True`.
- `log.txt` is a log of all events while creating asset bundles, including errors.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| lisdf_path |  Union[str, Path] |  | The path to the .lisdf file as either a string or [`Path`](https://docs.python.org/3/library/pathlib.html). |
| output_directory |  Union[str, Path] |  | The directory of the object asset bundles as either a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If it doesn't exist, it will be created while the .lisdf models are being converted. |
| overwrite |  bool  | False | If True, overwrite any asset bundles in `output_directory`. If False, skip converting models if the asset bundles already exist. This should usually be False, especially if you're using robot asset bundles generated by [`RobotCreator`](../asset_bundle_creator/robot_creator.md). |
| cleanup |  bool  | True | If True, delete intermediary files such as .prefab files generated while creating asset bundles. |
| robot_metadata |  List[LisdfRobotMetadata] | None | If not None, this is a list of [`LisdfRobotMetadata`](../lisdf_data/lisdf_robot_metadata.md). **If there are any robots in the scene, they must be added to this list, or else they will be imported incorrectly.** |
| send_commands |  bool  | True | If True, the commands generated from the .lisdf file will be sent the next time `c.communicate()` is called. |
| quiet |  bool  | False | If True, don't print any messages to console. |
| display |  str  | "0" | The display to launch Unity Editor on. Ignored if this isn't Linux. |
| unity_editor_path |  Union[Path, str] | None | The path to the Unity Editor executable, for example `C:/Program Files/Unity/Hub/Editor/2020.3.24f1/Editor/Unity.exe`. If None, this script will try to find Unity Editor automatically. |
| check_version |  bool  | True | If True, check if there is an update to the Unity Editor project. |