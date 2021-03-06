# `object_init_data.py`

## `TransformInitData`

`from tdw.object_init_data import TransformInitData`

Basic initialization parameters for an object. Can be converted to and from a list of commands.

This is similar to [`Controller.get_add_object()`](controller.md) except that it includes more parameters.

***

#### `__init__(self, name: str, library: str = "models_core.json", scale_factor: Dict[str, float] = None, position: Dict[str, float] = None, rotation: Dict[str, float] = None, kinematic: bool = False, gravity: bool = True)`


| Parameter | Description |
| --- | --- |
| name | The name of the model. |
| library | The filename of the library containing the model's record. |
| scale_factor | The [scale factor](../api/command_api.md#scale_object). |
| position | The initial position. If None, defaults to: `{"x": 0, "y": 0, "z": 0`}. |
| rotation | The initial rotation as Euler angles or a quaternion. If None, defaults to: `{"w": 1, "x": 0, "y": 0, "z": 0}` |
| kinematic | If True, the object will be [kinematic](../api/command_api.md#set_kinematic_state). |
| gravity | If True, the object won't respond to [gravity](../api/command_api.md#set_kinematic_state). |

***

#### `get_commands(self) -> Tuple[int, List[dict]]`

_Returns:_  Tuple: The ID of the object; a list of commands to create the object: `[add_object, rotate_object_to, scale_object, set_kinematic_state, set_object_collision_detection_mode]`

***

## `RigidbodyInitData(TransformInitData)`

`from tdw.object_init_data import RigidbodyInitData`

A subclass of `TransformInitData`. Includes data and commands to set the mass and physic material of the object.

***

#### `__init__(self, name: str, mass: float, dynamic_friction: float, static_friction: float, bounciness: float, library: str = "models_core.json", scale_factor: Dict[str, float] = None, position: Dict[str, float] = None, rotation: Dict[str, float] = None, kinematic: bool = False, gravity: bool = True)`


| Parameter | Description |
| --- | --- |
| name | The name of the model. |
| library | The filename of the library containing the model's record. |
| scale_factor | The [scale factor](../api/command_api.md#scale_object). |
| position | The initial position. If None, defaults to: `{"x": 0, "y": 0, "z": 0`}. |
| rotation | The initial rotation as Euler angles or a quaternion. If None, defaults to: `{"w": 1, "x": 0, "y": 0, "z": 0}` |
| kinematic | If True, the object will be [kinematic](../api/command_api.md#set_kinematic_state). |
| gravity | If True, the object won't respond to [gravity](../api/command_api.md#set_kinematic_state). |
| mass | The mass of the object. |
| dynamic_friction | The [dynamic friction](../api/command_api.md#set_physic_material) of the object. |

***

#### `get_commands(self) -> Tuple[int, List[dict]]`

_Returns:_  Tuple: The ID of the object; a list of commands to create the object: `[add_object, rotate_object_to, scale_object, set_kinematic_state, set_object_collision_detection_mode, set_mass, set_physic_material]`

***

## `AudioInitData(RigidbodyInitData)`

`from tdw.object_init_data import AudioInitData`

A subclass of `RigidbodyInitData` that includes [audio values](py_impact.md#objectinfo).
Physics values are derived from these audio values.

***

#### `__init__(self, name: str, library: str = "models_core.json", scale_factor: Dict[str, float] = None, position: Dict[str, float] = None, rotation: Dict[str, float] = None, kinematic: bool = False, gravity: bool = True, audio: ObjectInfo = None)`


| Parameter | Description |
| --- | --- |
| name | The name of the model. |
| library | The filename of the library containing the model's record. |
| scale_factor | The [scale factor](../api/command_api.md#scale_object). |
| position | The initial position. If None, defaults to: `{"x": 0, "y": 0, "z": 0`}. |
| rotation | The initial rotation as Euler angles or a quaternion. If None, defaults to: `{"w": 1, "x": 0, "y": 0, "z": 0}` |
| kinematic | If True, the object will be [kinematic](../api/command_api.md#set_kinematic_state). |
| gravity | If True, the object won't respond to [gravity](../api/command_api.md#set_kinematic_state). |
| audio | If None, derive physics data from the audio data in `PyImpact.get_object_info()` (if the object isn't in this dictionary, this constructor will throw an error). If not None, use these values instead of the default audio values. |

***

#### `get_commands(self) -> Tuple[int, List[dict]]`

_Returns:_  Tuple: The ID of the object; a list of commands to create the object: `[add_object, rotate_object_to, scale_object, set_kinematic_state, set_object_collision_detection_mode, set_mass, set_physic_material]`

***

