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

#### `__init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True)`

Create the network socket and bind the socket to the port.

| Parameter | Description |
| --- | --- |
| port | The port number. |
| check_version | If true, the controller will check the version of the build and print the result. |
| launch_build | If True, automatically launch the build. If one doesn't exist, download and extract the correct version. Set this to False to use your own build, or (if you are a backend developer) to use Unity Editor. |

***

#### `communicate(self, commands: Union[dict, List[dict]]) -> list`

Send commands and receive output data in response.

| Parameter | Description |
| --- | --- |
| commands | A list of JSON commands. |

_Returns:_ The output data from the build.

***

#### `get_add_object(self, model_name: str, object_id: int, position: Dict[str, float] = None, rotation: Dict[str, float] = None, library: str = "") -> dict`

Returns a valid add_object command.

| Parameter | Description |
| --- | --- |
| model_name | The name of the model. |
| position | The position of the model. If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| rotation | The starting rotation of the model, in Euler angles. If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| library | The path to the records file. If left empty, the default library will be selected. See `ModelLibrarian.get_library_filenames()` and `ModelLibrarian.get_default_library()`. |
| object_id | The ID of the new object. |

_Returns:_ An add_object command that the controller can then send.

***

#### `get_add_physics_object(self, model_name: str, object_id: int, position: Dict[str, float] = None, rotation: Dict[str, float] = None, library: str = "", scale_factor: Dict[str, float] = None, kinematic: bool = False, gravity: bool = True, default_physics_values: bool = True, mass: float = 1, dynamic_friction: float = 0.3, static_friction: float = 0.3, bounciness: float = 0.7) -> List[dict]`


| Parameter | Description |
| --- | --- |
| model_name | The name of the model. |
| position | The position of the model. If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| rotation | The starting rotation of the model, in Euler angles. If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| library | The path to the records file. If left empty, the default library will be selected. See `ModelLibrarian.get_library_filenames()` and `ModelLibrarian.get_default_library()`. |
| object_id | The ID of the new object. |
| scale_factor | The [scale factor](../api/command_api.md#scale_object). |
| kinematic | If True, the object will be [kinematic](../api/command_api.md#set_kinematic_state). |
| gravity | If True, the object won't respond to [gravity](../api/command_api.md#set_kinematic_state). |
| default_physics_values | If True, use default physics values. Not all objects have default physics values. To determine if object does: `has_default_physics_values = model_name in Controller.DEFAULT_PHYSICS_VALUES`. |
| mass | The mass of the object. Ignored if `default_physics_values == True`. |
| dynamic_friction | The [dynamic friction](../api/command_api.md#set_physic_material) of the object. Ignored if `default_physics_values == True`. |
| static_friction | The [static friction](../api/command_api.md#set_physic_material) of the object. Ignored if `default_physics_values == True`. |
| bounciness | The [bounciness](../api/command_api.md#set_physic_material) of the object. Ignored if `default_physics_values == True`. |

_Returns:_  A list of commands to add the object and apply physics values.

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

| Parameter | Description |
| --- | --- |
| humanoid_animation_name | The name of the animation. |
| library | The path to the records file. If left empty, the default library will be selected. See `HumanoidAnimationLibrarian.get_library_filenames()` and `HumanoidAnimationLibrarian.get_default_library()`. |

_Returns:_ An add_humanoid_animation command that the controller can then send.

***

#### `get_add_robot(self, name: str, robot_id: int, position: Dict[str, float] = None, rotation: Dict[str, float] = None, library: str = "") -> dict`

Returns a valid add_robot command.

| Parameter | Description |
| --- | --- |
| name | The name of the robot. |
| robot_id | A unique ID for the robot. |
| position | The initial position of the robot. If None, the position will be (0, 0, 0). |
| rotation | The initial rotation of the robot in Euler angles. |
| library | The path to the records file. If left empty, the default library will be selected. See `RobotLibrarian.get_library_filenames()` and `RobotLibrarian.get_default_library()`. |

_Returns:_ An `add_robot` command that the controller can then send.

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

#### `launch_build(port: int = 1071) -> None`

_This is a static function._

Launch the build. If a build doesn't exist at the expected location, download one to that location.

| Parameter | Description |
| --- | --- |
| port | The socket port. |

***

