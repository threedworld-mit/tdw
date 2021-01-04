# `tdw_utils.py`

## `TDWUtils`

`from tdw.tdw_utils import TDWUtils`

Utility functions for controllers.

Usage:

```python
from tdw.tdw_utils import TDWUtils
```

***

#### `vector3_to_array(vector3: Dict[str, float]) -> np.array`

_This is a static function._

Convert a Vector3 object to a numpy array.

| Parameter | Description |
| --- | --- |
| vector3 | The Vector3 object, e.g. `{"x": 0, "y": 0, "z": 0}` |

_Returns:_ A numpy array.

***

#### `array_to_vector3(arr: np.array) -> Dict[str, float]`

_This is a static function._

Convert a numpy array to a Vector3.

| Parameter | Description |
| --- | --- |
| arr | The numpy array. |

_Returns:_ A Vector3, e.g. `{"x": 0, "y": 0, "z": 0}`

***

#### `vector4_to_array(vector4: Dict[str, float]) -> np.array`

_This is a static function._

Convert a Vector4 to a numpy array.

| Parameter | Description |
| --- | --- |
| vector4 | The Vector4 object, e.g. `{"x": 0, "y": 0, "z": 0, "w": 0}` |

_Returns:_ A numpy array.

***

#### `array_to_vector4(arr: np.array) -> Dict[str, float]`

_This is a static function._

Convert a numpy array to a Vector4.

| Parameter | Description |
| --- | --- |
| arr | The numpy array. |

_Returns:_ A Vector4, e.g. `{"x": 0, "y": 0, "z": 0, "w": 0}`

***

#### `color_to_array(color: Dict[str, float]) -> np.array`

_This is a static function._

Convert a RGB Color to a numpy array.

| Parameter | Description |
| --- | --- |
| color | The Color object, e.g. `{"r": 0, "g": 0, "b": 0, "a": 1}` |

_Returns:_ A numpy array.

***

#### `array_to_color(arr: np.array) -> Dict[str, float]`

_This is a static function._

Convert a numpy array to a RGBA Color. If no A value is supplied it will default to 1.

| Parameter | Description |
| --- | --- |
| arr | The array. |

_Returns:_ A Color, e.g. `{"r": 0, "g": 0, "b": 0, "a": 1}`

***

#### `get_random_point_in_circle(center: np.array, radius: float) -> np.array`

_This is a static function._

Get a random point in a circle, defined by a center and radius.

| Parameter | Description |
| --- | --- |
| center | The center of the circle. |
| radius | The radius of the circle. |

_Returns:_ A numpy array. The y value (`arr[1]`) is always 0.

***

#### `get_magnitude(vector3: Dict[str, float]) -> float`

_This is a static function._

Get the magnitude of a Vector3.

| Parameter | Description |
| --- | --- |
| vector3 | The Vector3 object, e.g. `{"x": 0, "y": 0, "z": 0}` |

_Returns:_ The vector magnitude.

***

#### `extend_line(p0: np.array, p1: np.array, d: float, clamp_y=True) -> np.array`

_This is a static function._

Extend the line defined by p0 to p1 by distance d. Clamps the y value to 0.

| Parameter | Description |
| --- | --- |
| p0 | The origin. |
| p1 | The second point. |
| d | The distance of which the line is to be extended. |
| clamp_y | Clamp the y value to 0. |

_Returns:_  The position at distance d.

***

#### `get_distance(vector3_0: Dict[str, float], vector3_1: Dict[str, float]) -> float`

_This is a static function._

Calculate the distance between two Vector3 (e.g. `{"x": 0, "y": 0, "z": 0}`) objects.

| Parameter | Description |
| --- | --- |
| vector3_0 | The first Vector3. |
| vector3_1 | The second Vector3. |

_Returns:_ The distance.

***

#### `get_box(width: int, length: int) -> List[Dict[str, int]]`

_This is a static function._

Returns a list of x,y positions that can be used to create a box with the `create_exterior_walls` command.

| Parameter | Description |
| --- | --- |
| width | The width of the box. |
| length | The length of the box. |

_Returns:_ The box as represented by a list of `{"x": x, "y": y}` dictionaries.

***

#### `get_vector3(x, y, z) -> Dict[str, float]`

_This is a static function._


| Parameter | Description |
| --- | --- |
| x | The x value. |
| y | The y value. |
| z | The z value. |

_Returns:_  A Vector3: {"x": x, "y", y, "z": z}

***

#### `create_empty_room(width: int, length: int) -> dict`

_This is a static function._


| Parameter | Description |
| --- | --- |
| width | The width of the room. |
| length | The length of the room. |

_Returns:_  A `create_exterior_walls` command that creates a box with dimensions (width, length).

***

#### `create_room_from_image(filepath: str, exterior_color=(255, 0, 0), interior_color=(0, 0, 0)) -> List[dict]`

_This is a static function._

Load a .png file from the disk and use it to create a room. Each pixel on the image is a grid point.

| Parameter | Description |
| --- | --- |
| filepath | The absolute filepath to the image. |
| exterior_color | The color on the image marking exterior walls (default=red). |
| interior_color | The color on the image marking interior walls (default=black). |

_Returns:_  A list of commands: The first creates the exterior walls, and the second creates the interior walls.

***

#### `save_images(images: Images, filename: str, output_directory="dist", resize_to=None, append_pass: bool = True) -> None`

_This is a static function._

Save each image in the Images object.
The name of the image will be: pass_filename.extension, e.g.: `"0000"` -> `depth_0000.png`
The images object includes the pass and extension information.

| Parameter | Description |
| --- | --- |
| images | The Images object. Contains each capture pass plus metadata. |
| output_directory | The directory to write images to. |
| filename | The filename of each image, minus the extension. The image pass will be appended as a prefix. |
| resize_to | Specify a (width, height) tuple to resize the images to. This is slower than saving as-is. |
| append_pass | If false, the image pass will _not_ be appended to the filename as a prefix, e.g.: `"0000"`: -> "`0000.jpg"` |

***

#### `zero_padding(integer: int, width=4) -> str`

_This is a static function._


| Parameter | Description |
| --- | --- |
| integer | The integer being converted. |
| width | The total number of digits in the string. If integer == 3 and width == 4, output is: "0003". |

_Returns:_ A string representation of an integer padded with zeroes, e.g. converts `3` to `"0003"`.

***

#### `get_pil_image(images: Images, index: int) -> Image`

_This is a static function._

Converts Images output data to a PIL Image object.
Use this function to read and analyze an image in memory.
Do NOT use this function to save image data to disk; `save_image` is much faster.

| Parameter | Description |
| --- | --- |
| images | Images data from the build. |
| index | The index of the image in Images.get_image |

_Returns:_ A PIL image.

***

#### `get_random_position_on_nav_mesh(c: Controller, width: float, length: float, x_e=0, z_e=0, bake=True, rng=random.uniform) -> Tuple[float, float, float]`

_This is a static function._

Returns a random position on a NavMesh.

| Parameter | Description |
| --- | --- |
| c | The controller. |
| width | The width of the environment. |
| length | The length of the environment. |
| bake | If true, send bake_nav_mesh. |
| rng | Random number generator. |
| x_e | The x position of the environment. |
| z_e | The z position of the environment. |

_Returns:_ The coordinates as a tuple `(x, y, z)`

***

#### `set_visual_material(c: Controller, substructure: List[dict], object_id: int, material: str, quality="med") -> List[dict]`

_This is a static function._


| Parameter | Description |
| --- | --- |
| c | The controller. |
| substructure | The metadata substructure of the object. |
| object_id | The ID of the object in the scene. |
| material | The name of the new material. |
| quality | The quality of the material. |

_Returns:_ A list of commands to set ALL visual materials on an object to a single material.

***

#### `get_depth_values(image: np.array, depth_pass: str = "_depth", width: int = 256, height: int = 256, uv_starts_on_top: bool = True) -> np.array`

_This is a static function._

Get the depth values of each pixel in a _depth image pass.
The far plane is hardcoded as 100. The near plane is hardcoded as 0.1.
(This is due to how the depth shader is implemented.)

| Parameter | Description |
| --- | --- |
| image | The image pass as a numpy array. |
| depth_pass | The type of depth pass. This determines how the values are decoded. Options: `"_depth"`, `"_depth_simple"`. |
| width | The width of the screen in pixels. |
| height | The height of the screen in pixels. |
| uv_starts_on_top | If True, UV coordinates start at the top of the image. See the command `send_system_info`. |

_Returns:_ An array of depth values.

***

#### `get_point_cloud(depth, camera_matrix: Union[np.array, tuple], vfov: float = 54.43222, filename: str = None) -> np.array`

_This is a static function._

Create a point cloud from an numpy array of depth values.

| Parameter | Description |
| --- | --- |
| depth | Depth values converted from a depth pass. See: `TDWUtils.get_depth_values()` |
| camera_matrix | The camera matrix as a tuple or numpy array. See: [`send_camera_matrices`](https://github.com/threedworld-mit/tdw/blob/master/Documentation/api/command_api.md#send_camera_matrices). |
| vfov | The field of view. See: [`set_field_of_view`](https://github.com/threedworld-mit/tdw/blob/master/Documentation/api/command_api.md#set_field_of_view) |
| filename | If not None, the point cloud data will be written to this file. |

_Returns:_  An point cloud as a numpy array of `[x, y, z]` coordinates.

***

#### `create_avatar(avatar_type="A_Img_Caps_Kinematic", avatar_id="a", position=None, look_at=None) -> List[dict]`

_This is a static function._

This is a wrapper for `create_avatar` and, optionally, `teleport_avatar_to` and `look_at_position`.

| Parameter | Description |
| --- | --- |
| avatar_type | The type of avatar. |
| avatar_id | The avatar ID. |
| position | The position of the avatar. If this is None, the avatar won't teleport. |
| look_at | If this isn't None, the avatar will look at this position. |

_Returns:_ A list of commands to create theavatar.

***

#### `launch_build(listener_port: int, build_address: str, controller_address: str) -> dict`

_This is a static function._

Connect to a remote binary_manager daemon and launch an instance of a TDW build.
Returns the necessary information for a local controller to connect.
Use this function to automatically launching binaries on remote (or local) nodes, and to
automatically shut down the build after controller is finished. Call in the constructor
of a controller and pass the build_port returned in build_info to the parent Controller class.

| Parameter | Description |
| --- | --- |
| listener_port | The port launch_binaries is listening on. |
| build_address | Remote IP or hostname of node running launch_binaries. |
| controller_address | IP or hostname of node running controller. |

_Returns:_ The build_info dictionary containing build_port.

***

#### `get_unity_args(arg_dict: dict) -> List[str]`

_This is a static function._


| Parameter | Description |
| --- | --- |
| arg_dict | A dictionary of arguments. Key=The argument prefix (e.g. port) Value=Argument value. |

_Returns:_ The formatted command line string that is accepted by unity arg parser.

***

#### `find_free_port() -> int`

_This is a static function._

_Returns:_ a free port.

***

#### `get_unit_scale(record: ModelRecord) -> float`

_This is a static function._


| Parameter | Description |
| --- | --- |
| record | The model record. |

_Returns:_ The scale factor required to scale a model to 1 meter "unit scale".

***

#### `validate_amazon_s3() -> bool`

_This is a static function._

Validate that your local Amazon S3 credentials are set up correctly.

_Returns:_ True if everything is OK.

***

#### `get_base64_flex_particle_forces(forces: list) -> str`

_This is a static function._


| Parameter | Description |
| --- | --- |
| forces | The forces (see Flex documentation for how to arrange this array). |

_Returns:_  An array of Flex particle forces encoded in base64.

***

#### `color_to_hashable(color: Union[np.array, Tuple[int, int, int]]) -> int`

_This is a static function._


| Parameter | Description |
| --- | --- |
| color | The color as an RGB array or tuple, where each value is between 0 and 255. |

_Returns:_  A hashable integer representation of the color array.

***

#### `hashable_to_color(hashable: int) -> np.array`

_This is a static function._


| Parameter | Description |
| --- | --- |
| hashable | A hashable integer representing an RGB color. |

_Returns:_  A color as a numpy array of integers between 0 and 255: `[r, g, b]`

***

#### `get_collisions(resp: List[bytes]) -> Tuple[List[Collision], List[EnvironmentCollision]]`

_This is a static function._


| Parameter | Description |
| --- | --- |
| resp | The response from the build (a byte array). |

_Returns:_  Tuple: A list of collisions; a list of environment collisions.

***

#### `get_bounds_dict(bounds: Bounds, index: int) -> Dict[str, np.array]`

_This is a static function._


| Parameter | Description |
| --- | --- |
| bounds | Bounds output data. |
| index | The index in `bounds` of the target object. |

_Returns:_  A dictionary of the bounds. Key = the name of the position. Value = the position as a numpy array.

***

#### `get_closest_position_in_bounds(origin: np.array, bounds: Bounds, index: int) -> np.array`

_This is a static function._


| Parameter | Description |
| --- | --- |
| origin | The origin from which the distance is calculated. |
| bounds | Bounds output data. |
| index | The index in `bounds` of the target object. |

_Returns:_  The position on the object bounds that is closest to `origin`.

***

#### `get_angle(forward: np.array, origin: np.array, position: np.array) -> float`

_This is a static function._


| Parameter | Description |
| --- | --- |
| position | The target position. |
| origin | The origin position of the directional vector. |
| forward | The forward directional vector. |

_Returns:_  The angle in degrees between `forward` and the direction vector from `origin` to `position`.

***

#### `get_angle_between(v1: np.array, v2: np.array) -> float`

_This is a static function._


| Parameter | Description |
| --- | --- |
| v1 | The first directional vector. |
| v2 | The second directional vector. |

_Returns:_  The angle in degrees between two directional vectors.

***

#### `rotate_position_around(position: np.array, angle: float, origin: np.array = None) -> np.array`

_This is a static function._

Rotate a position by a given angle around a given origin.

| Parameter | Description |
| --- | --- |
| origin | The origin position.  If None, the origin is `[0, 0, 0]` |
| position | The point being rotated. |
| angle | The angle in degrees. |

_Returns:_  The rotated position.

***

## `AudioUtils`

`from tdw.tdw_utils import AudioUtils`

Utility class for recording audio in TDW using [fmedia](https://stsaz.github.io/fmedia/).

Usage:

```python
from tdw.tdw_utils import AudioUtils
from tdw.controller import Controller

c = Controller()

initialize_trial()  # Your code here.

# Begin recording audio. Automatically stop recording at 10 seconds.
AudioUtils.start(output_path="path/to/file.wav", until=(0, 10))

do_trial()  # Your code here.

# Stop recording.
AudioUtils.stop()
```

***

#### `get_system_audio_device() -> str`

_This is a static function._

_Returns:_  The audio device that can be used to capture system audio.

***

#### `start(output_path: Union[str, Path], until: Optional[Tuple[int, int]] = None) -> None`

_This is a static function._

Start recording audio.

| Parameter | Description |
| --- | --- |
| output_path | The path to the output file. |
| until | If not None, fmedia will record until `minutes:seconds`. The value must be a tuple of 2 integers. If None, fmedia will record until you send `AudioUtils.stop()`. |

***

#### `stop() -> None`

_This is a static function._

Stop recording audio (if any fmedia process is running).

***

#### `is_recording() -> bool`

_This is a static function._

_Returns:_  True if the fmedia recording process still exists.

***

## `QuaternionUtils`

`from tdw.tdw_utils import QuaternionUtils`

Helper functions for using quaternions.

Quaternions are always numpy arrays in the following order: `[x, y, z, w]`.
This is the order returned in all Output Data objects.

Vectors are always numpy arrays in the following order: `[x, y, z]`.

***

#### `get_inverse(q: np.array) -> np.array`

_This is a static function._

Source: https://referencesource.microsoft.com/#System.Numerics/System/Numerics/Quaternion.cs

| Parameter | Description |
| --- | --- |
| q | The quaternion. |

_Returns:_  The inverse of the quaternion.

***

#### `multiply(q1: np.array, q2: np.array) -> np.array`

_This is a static function._

Multiply two quaternions.
Source: https://stackoverflow.com/questions/4870393/rotating-coordinate-system-via-a-quaternion

| Parameter | Description |
| --- | --- |
| q1 | The first quaternion. |
| q2 | The second quaternion. |

_Returns:_  The multiplied quaternion: `q1 * q2`

***

#### `get_conjugate(q: np.array) -> np.array`

_This is a static function._

Source: https://stackoverflow.com/questions/4870393/rotating-coordinate-system-via-a-quaternion

| Parameter | Description |
| --- | --- |
| q | The quaternion. |

_Returns:_  The conjugate of the quaternion: `[-x, -y, -z, w]`

***

#### `multiply_by_vector(q: np.array, v: np.array) -> np.array`

_This is a static function._

Multiply a quaternion by a vector.
Source: https://stackoverflow.com/questions/4870393/rotating-coordinate-system-via-a-quaternion

| Parameter | Description |
| --- | --- |
| q | The quaternion. |
| v | The vector. |

_Returns:_  A directional vector calculated from: `q * v`

***

#### `world_to_local_vector(position: np.array, origin: np.array, rotation: np.array) -> np.array`

_This is a static function._

Convert a vector position in absolute world coordinates to relative local coordinates.
Source: https://answers.unity.com/questions/601062/what-inversetransformpoint-does-need-explanation-p.html

| Parameter | Description |
| --- | --- |
| position | The position vector in world coordinates. |
| origin | The origin vector of the local space in world coordinates. |
| rotation | The rotation quaternion of the local coordinate space. |

_Returns:_  `position` in local coordinates.

***

#### `get_up_direction(q: np.array) -> np.array`

_This is a static function._


| Parameter | Description |
| --- | --- |
| q | The rotation as a quaternion. |

_Returns:_  A directional vector corresponding to the "up" direction from the quaternion.

***

#### `euler_angles_to_quaternion(euler: np.array) -> np.array`

_This is a static function._

Convert Euler angles to a quaternion.

| Parameter | Description |
| --- | --- |
| euler | The Euler angles vector. |

_Returns:_  The quaternion representation of the Euler angles.

***

#### `quaternion_to_euler_angles(quaternion: np.array) -> np.array`

_This is a static function._

Convert a quaternion to Euler angles.

| Parameter | Description |
| --- | --- |
| quaternion | A quaternion as a nump array. |

_Returns:_  The Euler angles representation of the quaternion.

***

#### `get_y_angle(q1: np.array, q2: np.array) -> float`

_This is a static function._

Source: https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles

| Parameter | Description |
| --- | --- |
| q1 | The first quaternion. |
| q2 | The second quaternion. |

_Returns:_  The angle between the two quaternions in degrees around the y axis.

***

