# Controller

`from tdw.controller import Controller`

Base class for all controllers.

Usage:

```python
from tdw.controller import Controller
c = Controller()
```

***

## Functions

#### \_\_init\_\_

**`Controller()`**

**`Controller(port=1071, check_version=True, launch_build=True)`**

Create the network socket and bind the socket to the port.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| port |  int  | 1071 | The port number. |
| check_version |  bool  | True | If true, the controller will check the version of the build and print the result. |
| launch_build |  bool  | True | If True, automatically launch the build. If one doesn't exist, download and extract the correct version. Set this to False to use your own build, or (if you are a backend developer) to use Unity Editor. |

#### communicate

**`self.communicate(commands)`**

Send commands and receive output data in response.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| commands |  Union[dict, List[dict] |  | A list of JSON commands. |

_Returns:_  The output data from the build.

#### get_add_object

**`Controller.get_add_object(model_name, object_id)`**

**`Controller.get_add_object(model_name, position=None, rotation=None, library="", object_id)`**

_(Static)_

Returns a valid add_object command.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| model_name |  str |  | The name of the model. |
| position |  Dict[str, float] | None | The position of the model. If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| rotation |  Dict[str, float] | None | The starting rotation of the model, in Euler angles. If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| library |  str  | "" | The path to the records file. If left empty, the default library will be selected. See `ModelLibrarian.get_library_filenames()` and `ModelLibrarian.get_default_library()`. |
| object_id |  int |  | The ID of the new object. |

_Returns:_  An add_object command that the controller can then send via [`self.communicate(commands)`](#communicate).

#### get_add_physics_object

**`Controller.get_add_physics_object(model_name, object_id)`**

**`Controller.get_add_physics_object(model_name, position=None, rotation=None, library="", object_id, scale_factor=None, kinematic=False, gravity=True, default_physics_values=True, mass=1, dynamic_friction=0.3, static_friction=0.3, bounciness=0.7, scale_mass=True)`**

_(Static)_

Add an object to the scene with physics values (mass, friction coefficients, etc.).


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| model_name |  str |  | The name of the model. |
| position |  Dict[str, float] | None | The position of the model. If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| rotation |  Dict[str, float] | None | The starting rotation of the model, in Euler angles. If None, defaults to `{"x": 0, "y": 0, "z": 0}`. |
| library |  str  | "" | The path to the records file. If left empty, the default library will be selected. See `ModelLibrarian.get_library_filenames()` and `ModelLibrarian.get_default_library()`. |
| object_id |  int |  | The ID of the new object. |
| scale_factor |  Dict[str, float] | None | The [scale factor](../api/command_api.md#scale_object). |
| kinematic |  bool  | False | If True, the object will be [kinematic](../api/command_api.md#set_kinematic_state). |
| gravity |  bool  | True | If True, the object won't respond to [gravity](../api/command_api.md#set_kinematic_state). |
| default_physics_values |  bool  | True | If True, use default physics values. Not all objects have default physics values. To determine if object does: `has_default_physics_values = model_name in DEFAULT_OBJECT_AUDIO_STATIC_DATA`. |
| mass |  float  | 1 | The mass of the object. Ignored if `default_physics_values == True`. |
| dynamic_friction |  float  | 0.3 | The [dynamic friction](../api/command_api.md#set_physic_material) of the object. Ignored if `default_physics_values == True`. |
| static_friction |  float  | 0.3 | The [static friction](../api/command_api.md#set_physic_material) of the object. Ignored if `default_physics_values == True`. |
| bounciness |  float  | 0.7 | The [bounciness](../api/command_api.md#set_physic_material) of the object. Ignored if `default_physics_values == True`. |
| scale_mass |  bool  | True | If True, the mass of the object will be scaled proportionally to the spatial scale. |

_Returns:_  A **list** of commands to add the object and apply physics values that the controller can then send via [`self.communicate(commands)`](#communicate).

#### get_add_material

**`Controller.get_add_material(material_name)`**

**`Controller.get_add_material(material_name, library="")`**

_(Static)_

Returns a valid add_material command.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| material_name |  str |  | The name of the material. |
| library |  str  | "" | The path to the records file. If left empty, the default library will be selected. See `MaterialLibrarian.get_library_filenames()` and `MaterialLibrarian.get_default_library()`. |

_Returns:_  An add_material command that the controller can then send via [`self.communicate(commands)`](#communicate).

#### get_add_scene

**`Controller.get_add_scene(scene_name)`**

**`Controller.get_add_scene(scene_name, library="")`**

_(Static)_

Returns a valid add_scene command.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| scene_name |  str |  | The name of the scene. |
| library |  str  | "" | The path to the records file. If left empty, the default library will be selected. See `SceneLibrarian.get_library_filenames()` and `SceneLibrarian.get_default_library()`. |

_Returns:_  An add_scene command that the controller can then send via [`self.communicate(commands)`](#communicate).

#### get_add_hdri_skybox

**`Controller.get_add_hdri_skybox(skybox_name)`**

**`Controller.get_add_hdri_skybox(skybox_name, library="")`**

_(Static)_

Returns a valid add_hdri_skybox command.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| skybox_name |  str |  | The name of the skybox. |
| library |  str  | "" | The path to the records file. If left empty, the default library will be selected. See `HDRISkyboxLibrarian.get_library_filenames()` and `HDRISkyboxLibrarian.get_default_library()`. |

_Returns:_  An add_hdri_skybox command that the controller can then send via [`self.communicate(commands)`](#communicate).

#### get_add_humanoid

**`Controller.get_add_humanoid(humanoid_name, object_id)`**

**`Controller.get_add_humanoid(humanoid_name, position=None, rotation=None, library="", object_id)`**

_(Static)_

Returns a valid add_humanoid command.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| humanoid_name |  str |  | The name of the humanoid. |
| position |  Dict[str, float] | None | The position of the humanoid. |
| rotation |  Dict[str, float] | None | The starting rotation of the humanoid, in Euler angles. |
| library |  str  | "" | The path to the records file. If left empty, the default library will be selected. See `HumanoidLibrarian.get_library_filenames()` and `HumanoidLibrarian.get_default_library()`. |
| object_id |  int |  | The ID of the new object. |

_Returns:_  An add_humanoid command that the controller can then send via [`self.communicate(commands)`](#communicate).

#### get_add_humanoid_animation

**`Controller.get_add_humanoid_animation(humanoid_animation_name)`**

**`Controller.get_add_humanoid_animation(humanoid_animation_name, library="")`**

_(Static)_

Returns a valid add_humanoid_animation command and the record (which you will need to play an animation).


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| humanoid_animation_name |  str |  | The name of the animation. |
| library |  | "" | The path to the records file. If left empty, the default library will be selected. See `HumanoidAnimationLibrarian.get_library_filenames()` and `HumanoidAnimationLibrarian.get_default_library()`. |

_Returns:_  An add_humanoid_animation command that the controller can then send via [`self.communicate(commands)`](#communicate).

#### get_add_robot

**`Controller.get_add_robot(name, robot_id)`**

**`Controller.get_add_robot(name, robot_id, position=None, rotation=None, library="")`**

_(Static)_

Returns a valid add_robot command.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| name |  str |  | The name of the robot. |
| robot_id |  int |  | A unique ID for the robot. |
| position |  Dict[str, float] | None | The initial position of the robot. If None, the position will be (0, 0, 0). |
| rotation |  Dict[str, float] | None | The initial rotation of the robot in Euler angles. |
| library |  str  | "" | The path to the records file. If left empty, the default library will be selected. See `RobotLibrarian.get_library_filenames()` and `RobotLibrarian.get_default_library()`. |

_Returns:_  An `add_robot` command that the controller can then send via [`self.communicate(commands)`](#communicate).

#### get_version

**`self.get_version()`**

Send a send_version command to the build.

_Returns:_  The TDW version and the Unity Engine version.

#### get_unique_id

**`Controller.get_unique_id()`**

_(Static)_

Generate a unique integer. Useful when creating objects.

_Returns:_  The new unique ID.

#### get_frame

**`Controller.get_frame(frame)`**

_(Static)_

Converts the frame byte array to an integer.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| frame |  bytes |  | The frame as bytes. |

_Returns:_  The frame as an integer.

#### launch_build

**`Controller.launch_build()`**

**`Controller.launch_build(port=1071)`**

_(Static)_

Launch the build. If a build doesn't exist at the expected location, download one to that location.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| port |  int  | 1071 | The socket port. |

