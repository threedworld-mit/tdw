# `controller.py`

## `Controller(object)`

`from tdw.controller import Controller`

Base class for all controllers.

Usage:

```python
from tdw.controller import Controller
c = Controller()
c.start()
```

***

#### `__init__(self, port: int = 1071, check_version: bool = True)`

Create the network socket and bind the socket to the port.

| Parameter | Description |
| --- | --- |
| port | The port number. |
| check_version | If true, the controller will check the version of the build and print the result. |

***

#### `communicate(self, commands: Union[dict, List[dict]]) -> list`

Send commands and receive output data in response.

| Parameter | Description |
| --- | --- |
| commands | A list of JSON commands. |

_Returns:_ The output data from the build.

***

#### `start(self, scene="ProcGenScene") -> None`

Init TDW.

| Parameter | Description |
| --- | --- |
| scene | The scene to load. |

***

#### `get_add_object(self, model_name: str, object_id: int, position={"x": 0, "y": 0, "z": 0}, rotation={"x": 0, "y": 0, "z": 0}, library: str = "") -> dict`

Returns a valid add_object command.

| Parameter | Description |
| --- | --- |
| model_name | The name of the model. |
| position | The position of the model. |
| rotation | The starting rotation of the model, in Euler angles. |
| library | The path to the records file. If left empty, the default library will be selected. See `ModelLibrarian.get_library_filenames()` and `ModelLibrarian.get_default_library()`. |
| object_id | The ID of the new object. |

_Returns:_ An add_object command that the controller can then send.

***

#### `get_add_material(self, material_name: str, library: str = "") -> dict`

Returns a valid add_material command.

| Parameter | Description |
| --- | --- |
| material_name | The name of the material. |
| library | The path to the records file. If left empty, the default library will be selected. See `MaterialLibrarian.get_library_filenames()` and `MaterialLibrarian.get_default_library()`. |

_Returns:_ An add_material command that the controller can then send.

***

#### `get_add_scene(self, scene_name: str, library: str = "") -> dict`

Returns a valid add_scene command.

| Parameter | Description |
| --- | --- |
| scene_name | The name of the scene. |
| library | The path to the records file. If left empty, the default library will be selected. See `SceneLibrarian.get_library_filenames()` and `SceneLibrarian.get_default_library()`. |

_Returns:_ An add_scene command that the controller can then send.

***

#### `get_add_hdri_skybox(self, skybox_name: str, library: str = "") -> dict`

Returns a valid add_hdri_skybox command.

| Parameter | Description |
| --- | --- |
| skybox_name | The name of the skybox. |
| library | The path to the records file. If left empty, the default library will be selected. See `HDRISkyboxLibrarian.get_library_filenames()` and `HDRISkyboxLibrarian.get_default_library()`. |

_Returns:_ An add_hdri_skybox command that the controller can then send.

***

#### `get_add_humanoid(self, humanoid_name: str, object_id: int, position={"x": 0, "y": 0, "z": 0}, rotation={"x": 0, "y": 0, "z": 0}, library: str ="") -> dict`

Returns a valid add_humanoid command.

| Parameter | Description |
| --- | --- |
| humanoid_name | The name of the humanoid. |
| position | The position of the humanoid. |
| rotation | The starting rotation of the humanoid, in Euler angles. |
| library | The path to the records file. If left empty, the default library will be selected. See `HumanoidLibrarian.get_library_filenames()` and `HumanoidLibrarian.get_default_library()`. |
| object_id | The ID of the new object. |

_Returns:_ An add_humanoid command that the controller can then send.

***

#### `get_add_humanoid_animation(self, humanoid_animation_name: str, library="") -> (dict, HumanoidAnimationRecord)`

Returns a valid add_humanoid_animation command and the record (which you will need to play an animation).
return An add_humanoid_animation command that the controller can then send.

| Parameter | Description |
| --- | --- |
| humanoid_animation_name | The name of the animation. |
| library | The path to the records file. If left empty, the default library will be selected. See `HumanoidAnimationLibrarian.get_library_filenames()` and `HumanoidAnimationLibrarian.get_default_library()`. |

***

#### `load_streamed_scene(self, scene="tdw_room_2018") -> None`

Load a streamed scene. This is equivalent to: `c.communicate(c.get_add_scene(scene))`

| Parameter | Description |
| --- | --- |
| scene | The name of the streamed scene. |

***

#### `add_object(self, model_name: str, position={"x": 0, "y": 0, "z": 0}, rotation={"x": 0, "y": 0, "z": 0}, library: str= "") -> int`

Add a model to the scene. This is equivalent to: `c.communicate(c.get_add_object())`

| Parameter | Description |
| --- | --- |
| model_name | The name of the model. |
| position | The position of the model. |
| rotation | The starting rotation of the model, in Euler angles. |
| library | The path to the records file. If left empty, the default library will be selected. See `ModelLibrarian.get_library_filenames()` and `ModelLibrarian.get_default_library()`. |

_Returns:_ The ID of the new object.

***

#### `get_version(self) -> Tuple[str, str]`

Send a send_version command to the build.

_Returns:_ The TDW version and the Unity Engine version.

***

#### `get_unique_id() -> int`

_This is a static function._

Generate a unique integer. Useful when creating objects.

_Returns:_ The new unique ID.

***

#### `get_frame(frame: bytes) -> int`

_This is a static function._

Converts the frame byte array to an integer.

| Parameter | Description |
| --- | --- |
| frame | The frame as bytes. |

_Returns:_ The frame as an integer.

***

