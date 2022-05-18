# TDWUtils

`from tdw.tdw_utils import TDWUtils`

Utility functions for controllers.

Usage:

```python
from tdw.tdw_utils import TDWUtils
```

***

## Functions

#### vector3_to_array

**`TDWUtils.vector3_to_array(vector3)`**

_(Static)_

Convert a Vector3 object to a numpy array.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| vector3 |  Dict[str, float] |  | The Vector3 object, e.g. `{"x": 0, "y": 0, "z": 0}` |

_Returns:_  A numpy array.

#### array_to_vector3

**`TDWUtils.array_to_vector3(arr)`**

_(Static)_

Convert a numpy array to a Vector3.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| arr |  np.array |  | The numpy array. |

_Returns:_  A Vector3, e.g. `{"x": 0, "y": 0, "z": 0}`

#### vector4_to_array

**`TDWUtils.vector4_to_array(vector4)`**

_(Static)_

Convert a Vector4 to a numpy array.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| vector4 |  Dict[str, float] |  | The Vector4 object, e.g. `{"x": 0, "y": 0, "z": 0, "w": 0}` |

_Returns:_  A numpy array.

#### array_to_vector4

**`TDWUtils.array_to_vector4(arr)`**

_(Static)_

Convert a numpy array to a Vector4.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| arr |  np.array |  | The numpy array. |

_Returns:_  A Vector4, e.g. `{"x": 0, "y": 0, "z": 0, "w": 0}`

#### color_to_array

**`TDWUtils.color_to_array(color)`**

_(Static)_

Convert a RGB Color to a numpy array.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| color |  Dict[str, float] |  | The Color object, e.g. `{"r": 0, "g": 0, "b": 0, "a": 1}` |

_Returns:_  A numpy array.

#### array_to_color

**`TDWUtils.array_to_color(arr)`**

_(Static)_

Convert a numpy array to a RGBA Color. If no A value is supplied it will default to 1.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| arr |  np.array |  | The array. |

_Returns:_  A Color, e.g. `{"r": 0, "g": 0, "b": 0, "a": 1}`

#### get_random_point_in_circle

**`TDWUtils.get_random_point_in_circle(center, radius)`**

_(Static)_

Get a random point in a circle, defined by a center and radius.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| center |  np.array |  | The center of the circle. |
| radius |  float |  | The radius of the circle. |

_Returns:_  A numpy array. The y value (`arr[1]`) is always 0.

#### get_magnitude

**`TDWUtils.get_magnitude(vector3)`**

_(Static)_

Get the magnitude of a Vector3.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| vector3 |  Dict[str, float] |  | The Vector3 object, e.g. `{"x": 0, "y": 0, "z": 0}` |

_Returns:_  The vector magnitude.

#### extend_line

**`TDWUtils.extend_line(p0, p1, d)`**

**`TDWUtils.extend_line(p0, p1, d, clamp_y=True)`**

_(Static)_

Extend the line defined by p0 to p1 by distance d. Clamps the y value to 0.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| p0 |  np.array |  | The origin. |
| p1 |  np.array |  | The second point. |
| d |  float |  | The distance of which the line is to be extended. |
| clamp_y |  | True | Clamp the y value to 0. |

_Returns:_  The position at distance d.

#### get_distance

**`TDWUtils.get_distance(vector3_0, vector3_1)`**

_(Static)_

Calculate the distance between two Vector3 (e.g. `{"x": 0, "y": 0, "z": 0}`) objects.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| vector3_0 |  Dict[str, float] |  | The first Vector3. |
| vector3_1 |  Dict[str, float] |  | The second Vector3. |

_Returns:_  The distance.

#### get_box

**`TDWUtils.get_box(width, length)`**

_(Static)_

Returns a list of x,y positions that can be used to create a box with the `create_exterior_walls` command.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| width |  int |  | The width of the box. |
| length |  int |  | The length of the box. |

_Returns:_  The box as represented by a list of `{"x": x, "y": y}` dictionaries.

#### get_vector3

**`TDWUtils.get_vector3(x, y, z)`**

_(Static)_


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| x |  |  | The x value. |
| y |  |  | The y value. |
| z |  |  | The z value. |

_Returns:_  A Vector3: {"x": x, "y", y, "z": z}

#### create_empty_room

**`TDWUtils.create_empty_room(width, length)`**

_(Static)_


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| width |  int |  | The width of the room. |
| length |  int |  | The length of the room. |

_Returns:_  A `create_exterior_walls` command that creates a box with dimensions (width, length).

#### create_room_from_image

**`TDWUtils.create_room_from_image(filepath)`**

**`TDWUtils.create_room_from_image(filepath, exterior_color=(255, interior_color=(0)`**

_(Static)_

Load a .png file from the disk and use it to create a room. Each pixel on the image is a grid point.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| filepath |  str |  | The absolute filepath to the image. |
| exterior_color |  | (255 | The color on the image marking exterior walls (default=red). |
| interior_color |  | (0 | The color on the image marking interior walls (default=black). |

_Returns:_  A list of commands: The first creates the exterior walls, and the second creates the interior walls.

#### save_images

**`TDWUtils.save_images(images, filename)`**

**`TDWUtils.save_images(images, output_directory="dist", filename, resize_to=None, append_pass=True)`**

_(Static)_

Save each image in the Images object.
The name of the image will be: pass_filename.extension, e.g.: `"0000"` -> `depth_0000.png`
The images object includes the pass and extension information.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| images |  Images |  | The Images object. Contains each capture pass plus metadata. |
| output_directory |  | "dist" | The directory to write images to. |
| filename |  str |  | The filename of each image, minus the extension. The image pass will be appended as a prefix. |
| resize_to |  | None | Specify a (width, height) tuple to resize the images to. This is slower than saving as-is. |
| append_pass |  bool  | True | If false, the image pass will _not_ be appended to the filename as a prefix, e.g.: `"0000"`: -> "`0000.jpg"` |

#### get_shaped_depth_pass

**`TDWUtils.get_shaped_depth_pass(images, index)`**

_(Static)_

The `_depth` and `_depth_simple` passes are a 1D array of RGB values, as oppposed to a png or jpg like every other pass.
This function reshapes the array into a 2D array of RGB values.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| images |  Images |  | The `Images` output data. |
| index |  int |  | The index in `Images` of the depth pass. See: `Images.get_pass_mask()`. |

_Returns:_  A reshaped depth pass. Shape is: `(height, width, 3)`.

#### zero_padding

**`TDWUtils.zero_padding(integer)`**

**`TDWUtils.zero_padding(integer, width=4)`**

_(Static)_


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| integer |  int |  | The integer being converted. |
| width |  | 4 | The total number of digits in the string. If integer == 3 and width == 4, output is: "0003". |

_Returns:_  A string representation of an integer padded with zeroes, e.g. converts `3` to `"0003"`.

#### get_pil_image

**`TDWUtils.get_pil_image(images, index)`**

_(Static)_

Converts Images output data to a PIL Image object.
Use this function to read and analyze an image in memory.
Do NOT use this function to save image data to disk; `save_image` is much faster.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| images |  Images |  | Images data from the build. |
| index |  int |  | The index of the image in Images.get_image |

_Returns:_  A PIL image.

#### get_segmentation_colors

**`TDWUtils.get_segmentation_colors(id_pass)`**

_(Static)_


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| id_pass |  np.array |  | The ID pass image as a numpy array. |

_Returns:_  A list of unique colors in the ID pass.

#### get_random_position_on_nav_mesh

**`TDWUtils.get_random_position_on_nav_mesh(c, width, length)`**

**`TDWUtils.get_random_position_on_nav_mesh(c, width, length, bake=True, rng=random.uniform, x_e=0, z_e=0)`**

_(Static)_

Returns a random position on a NavMesh.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| c |  Controller |  | The controller. |
| width |  float |  | The width of the environment. |
| length |  float |  | The length of the environment. |
| bake |  | True | If true, send bake_nav_mesh. |
| rng |  | random.uniform | Random number generator. |
| x_e |  | 0 | The x position of the environment. |
| z_e |  | 0 | The z position of the environment. |

_Returns:_  The coordinates as a tuple `(x, y, z)`

#### set_visual_material

**`TDWUtils.set_visual_material(c, substructure, object_id, material)`**

**`TDWUtils.set_visual_material(c, substructure, object_id, material, quality="med")`**

_(Static)_


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| c |  Controller |  | The controller. |
| substructure |  List[dict] |  | The metadata substructure of the object. |
| object_id |  int |  | The ID of the object in the scene. |
| material |  str |  | The name of the new material. |
| quality |  | "med" | The quality of the material. |

_Returns:_  A list of commands to set ALL visual materials on an object to a single material.

#### get_depth_values

**`TDWUtils.get_depth_values(image)`**

**`TDWUtils.get_depth_values(image, depth_pass="_depth", width=256, height=256, near_plane=0.1, far_plane=100)`**

_(Static)_

Get the depth values of each pixel in a _depth image pass.
The far plane is hardcoded as 100. The near plane is hardcoded as 0.1.
(This is due to how the depth shader is implemented.)


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| image |  np.array |  | The image pass as a numpy array. |
| depth_pass |  str  | "_depth" | The type of depth pass. This determines how the values are decoded. Options: `"_depth"`, `"_depth_simple"`. |
| width |  int  | 256 | The width of the screen in pixels. See output data `Images.get_width()`. |
| height |  int  | 256 | The height of the screen in pixels. See output data `Images.get_height()`. |
| near_plane |  float  | 0.1 | The near clipping plane. See command `set_camera_clipping_planes`. The default value in this function is the default value of the near clipping plane. |
| far_plane |  float  | 100 | The far clipping plane. See command `set_camera_clipping_planes`. The default value in this function is the default value of the far clipping plane. |

_Returns:_  An array of depth values.

#### get_point_cloud

**`TDWUtils.get_point_cloud(depth, camera_matrix)`**

**`TDWUtils.get_point_cloud(depth, camera_matrix, vfov=54.43222, filename=None, near_plane=0.1, far_plane=100)`**

_(Static)_

Create a point cloud from an numpy array of depth values.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| depth |  |  | Depth values converted from a depth pass. See: `TDWUtils.get_depth_values()` |
| camera_matrix |  Union[np.array, tuple] |  | The camera matrix as a tuple or numpy array. See: [`send_camera_matrices`](https://github.com/threedworld-mit/tdw/blob/master/Documentation/api/command_api.md#send_camera_matrices). |
| vfov |  float  | 54.43222 | The field of view. See: [`set_field_of_view`](https://github.com/threedworld-mit/tdw/blob/master/Documentation/api/command_api.md#set_field_of_view) |
| filename |  str  | None | If not None, the point cloud data will be written to this file. |
| near_plane |  float  | 0.1 | The near clipping plane. See command `set_camera_clipping_planes`. The default value in this function is the default value of the near clipping plane. |
| far_plane |  float  | 100 | The far clipping plane. See command `set_camera_clipping_planes`. The default value in this function is the default value of the far clipping plane. |

_Returns:_  An point cloud as a numpy array of `[x, y, z]` coordinates.

#### create_avatar

**`TDWUtils.create_avatar()`**

**`TDWUtils.create_avatar(avatar_type="A_Img_Caps_Kinematic", avatar_id="a", position=None, look_at=None)`**

_(Static)_

This is a wrapper for `create_avatar` and, optionally, `teleport_avatar_to` and `look_at_position`.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| avatar_type |  | "A_Img_Caps_Kinematic" | The type of avatar. |
| avatar_id |  | "a" | The avatar ID. |
| position |  | None | The position of the avatar. If this is None, the avatar won't teleport. |
| look_at |  | None | If this isn't None, the avatar will look at this position. |

_Returns:_  A list of commands to create theavatar.

#### get_unit_scale

**`TDWUtils.get_unit_scale(record)`**

_(Static)_


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| record |  ModelRecord |  | The model record. |

_Returns:_  The scale factor required to scale a model to 1 meter "unit scale".

#### validate_amazon_s3

**`TDWUtils.validate_amazon_s3()`**

_(Static)_

Validate that your local Amazon S3 credentials are set up correctly.

_Returns:_  True if everything is OK.

#### get_base64_flex_particle_forces

**`TDWUtils.get_base64_flex_particle_forces(forces)`**

_(Static)_


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| forces |  list |  | The forces (see Flex documentation for how to arrange this array). |

_Returns:_  An array of Flex particle forces encoded in base64.

#### color_to_hashable

**`TDWUtils.color_to_hashable(color)`**

_(Static)_


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| color |  Union[np.array, Tuple[int, int, int] |  | The color as an RGB array or tuple, where each value is between 0 and 255. |

_Returns:_  A hashable integer representation of the color array.

#### hashable_to_color

**`TDWUtils.hashable_to_color(hashable)`**

_(Static)_


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| hashable |  int |  | A hashable integer representing an RGB color. |

_Returns:_  A color as a numpy array of integers between 0 and 255: `[r, g, b]`

#### get_bounds_dict

**`TDWUtils.get_bounds_dict(bounds, index)`**

_(Static)_


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| bounds |  Bounds |  | Bounds output data. |
| index |  int |  | The index in `bounds` of the target object. |

_Returns:_  A dictionary of the bounds. Key = the name of the position. Value = the position as a numpy array.

#### get_bounds_extents

**`TDWUtils.get_bounds_extents(bounds)`**

**`TDWUtils.get_bounds_extents(bounds, index=0)`**

_(Static)_


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| bounds |  Union[Bounds, Dict[str, Dict[str, float] |  | Bounds output data or cached bounds data from a record (`record.bounds`). |
| index |  int  | 0 | The index in `bounds` of the target object. Ignored if `bounds` is a dictionary. |

_Returns:_  The width (left to right), height (top to bottom), and length (front to back), of the bounds as a numpy array.

#### get_closest_position_in_bounds

**`TDWUtils.get_closest_position_in_bounds(origin, bounds, index)`**

_(Static)_


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| origin |  np.array |  | The origin from which the distance is calculated. |
| bounds |  Bounds |  | Bounds output data. |
| index |  int |  | The index in `bounds` of the target object. |

_Returns:_  The position on the object bounds that is closest to `origin`.

#### get_angle

**`TDWUtils.get_angle(position, origin, forward)`**

_(Static)_


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| position |  np.array |  | The target position. |
| origin |  np.array |  | The origin position of the directional vector. |
| forward |  np.array |  | The forward directional vector. |

_Returns:_  The angle in degrees between `forward` and the direction vector from `origin` to `position`.

#### get_angle_between

**`TDWUtils.get_angle_between(v1, v2)`**

_(Static)_


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| v1 |  np.array |  | The first directional vector. |
| v2 |  np.array |  | The second directional vector. |

_Returns:_  The angle in degrees between two directional vectors.

#### rotate_position_around

**`TDWUtils.rotate_position_around(position, angle)`**

**`TDWUtils.rotate_position_around(origin=None, position, angle)`**

_(Static)_

Rotate a position by a given angle around a given origin.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| origin |  np.array  | None | The origin position.  If None, the origin is `[0, 0, 0]` |
| position |  np.array |  | The point being rotated. |
| angle |  float |  | The angle in degrees. |

_Returns:_  The rotated position.

#### euler_angles_to_rpy

**`TDWUtils.euler_angles_to_rpy(euler_angles)`**

_(Static)_

Convert Euler angles to ROS RPY angles.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| euler_angles |  np.array |  | A numpy array: `[x, y, z]` Euler angles in degrees. |

_Returns:_  A numpy array: `[r, p, y]` angles in radians.

#### bytes_to_megabytes

**`TDWUtils.bytes_to_megabytes(b)`**

_(Static)_


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| b |  int |  | A quantity of bytes. |

_Returns:_  A quantity of megabytes.

#### get_circle_mask

**`TDWUtils.get_circle_mask(shape, row, column, radius)`**

_(Static)_

Get elements in an array within a circle.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| shape |  Tuple[int, int] |  | The shape of the source array as (rows, columns). |
| row |  int |  | The row (axis 0) of the center of the circle. |
| column |  int |  | The column (axis 1) of the circle. |
| radius |  int |  | The radius of the circle in indices. |

_Returns:_  A boolean array with shape `shape`. Elements that are True are within the circle.

#### download_asset_bundles

**`TDWUtils.download_asset_bundles(path, models, scenes, materials, hdri_skyboxes, robots, humanoids, humanoid_animations)`**

_(Static)_

Download asset bundles from TDW's remote S3 server. Create local librarian .json files for each type (models, scenes, etc.).
This can be useful to speed up the process of scene creation; it is always faster to load local asset bundles though it still takes time to load them into memory.

Note that if you wish to download asset bundles from tdw-private (`models_full.json`) you need valid S3 credentials.

For each parameter (`models`, `scenes`, etc.), if the value is `None`, no asset bundles will be downloaded.

Asset bundles will only be downloaded for your operating system. For example, if you want Linux asset bundles, call this function on Linux.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| path |  Union[str, Path] |  | The root directory of all of the asset bundles and librarian files. |
| models |  Dict[str, List[str] |  | A dictionary of models. Key = The model library, for example `"models_core.json"`. Value = A list of model names. |
| scenes |  Dict[str, List[str] |  | A dictionary of scenes. Key = The model library, for example `"scenes.json"`. Value = A list of scene names. |
| materials |  Dict[str, List[str] |  | A dictionary of materials. Key = The material library, for example `"materials_med.json"`. Value = A list of material names. |
| hdri_skyboxes |  Dict[str, List[str] |  | A dictionary of HDRI skyboxes. Key = The HDRI skybox library, for example `"hdri_skyboxes.json"`. Value = A list of HDRI skybox names. |
| robots |  Dict[str, List[str] |  | A dictionary of robots. Key = The robot library, for example `"robots.json"`. Value = A list of robot names. |
| humanoids |  Dict[str, List[str] |  | A dictionary of humanoids. Key = The model library, for example `"humanoids.json"`. Value = A list of humanoid names. |
| humanoid_animations |  Dict[str, List[str] |  | A dictionary of humanoid animations. Key = The model library, for example `"humanoid_animations.json"`. Value = A list of humanoid animation names. |

#### set_default_libraries

**`TDWUtils.set_default_libraries()`**

**`TDWUtils.set_default_libraries(model_library=None, scene_library=None, material_library=None, hdri_skybox_library=None, robot_library=None, humanoid_library=None, humanoid_animation_library=None)`**

_(Static)_

Set the path to the default libraries.

If any of the parameters of this function are left as `None`, the default remote S3 librarian will be used.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| model_library |  Union[str, Path] | None | The absolute path to a local model library file. |
| scene_library |  Union[str, Path] | None | The absolute path to a local scene library file. |
| material_library |  Union[str, Path] | None | The absolute path to a local material library file. |
| hdri_skybox_library |  Union[str, Path] | None | The absolute path to a local HDRI skybox library file. |
| robot_library |  Union[str, Path] | None | The absolute path to a local robot library file. |
| humanoid_library |  Union[str, Path] | None | The absolute path to a local humanoid library file. |
| humanoid_animation_library |  Union[str, Path] | None | The absolute path to a local humanoid animation library file. |

#### get_corners_from_wall

**`TDWUtils.get_corners_from_wall(wall)`**

_(Static)_


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| wall |  CardinalDirection |  | The wall as a [`CardinalDirection`](cardinal_direction.md). |

_Returns:_  The corners of the wall as a 2-element list of [`OrdinalDirection`](ordinal_direction.md).

#### get_direction_from_corner

**`TDWUtils.get_direction_from_corner(corner, wall)`**

_(Static)_

Given an corner an a wall, get the direction that a lateral arrangement will run along.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| corner |  OrdinalDirection |  | The corner as an [`OrdinalDirection`](ordinal_direction.md). |
| wall |  CardinalDirection |  | The wall as a [`CardinalDirection`](cardinal_direction.md). |

_Returns:_  Tuple: direction, wall

