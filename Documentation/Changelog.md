# CHANGELOG

# v1.8.x

To upgrade from TDW v1.7 to v1.8, read [this guide](Documentation/upgrade_guides/v1.7_to_v1.8).

## v1.8.7

### Command API

#### Modified Commands

| Command         | Modification                                                 |
| --------------- | ------------------------------------------------------------ |
| `follow_object` | Added optional parameter `rotation`. If True, set the avatar's rotation to the object's rotation. |

## v1.8.6

### `tdw` module

#### `PyImpact`

- Fixed: PyImpact sometimes creates a droning audio effect or distorts audio due to the same object having more than one collision in a given frame. PyImpact will only select one collision event per object per frame, and can filter out events in which (`enter` and `stay`) or (`enter` and `exit`) occurred on the same frame for the same object.

### Output Data

#### Modified Output Data

| Output Data    | Description                                                  |
| -------------- | ------------------------------------------------------------ |
| `ImageSensors` | Added: `get_sensor_forward()` Returns the forward directional vector of the sensor. |

## v1.8.5

### Command API

#### New Commands

| Command                  | Description                              |
| ------------------------ | ---------------------------------------- |
| `apply_torque_to_object` | Apply a torque to an object's rigidbody. |

#### Modified Commands

| Command              | Description                                                  |
| -------------------- | ------------------------------------------------------------ |
| `send_version`       | Added optional parameter `log` to log the TDW version in the Player or Editor log (default value is True). |
| `add_fixed_joint`    | Un-deprecated because it's still being used.                 |
| `detach_from_magnet` | Fixed: Kinematic objects attached to the magnet become non-kinematic when dropped. |

### Model Library

- Marked refridgerator_slim as do_not_use (colliders are rotated)
- Added: 4ft_wood_shelving, 5ft_shelf_metal, 5ft_wood_shelving, 6ft_shelf_metal, 6ft_wood_shelving

### Scene Library

- Added: mm_craftroom_1a, mm_craftroom_1b, mm_craftroom_2a, mm_craftroom_2b, mm_craftroom_3a, mm_craftroom_3b, mm_craftroom_4a, mm_craftroom_4b

### `tdw` module

#### `PyImpact`

- Added and update many object audio values in objects.csv
- Fixed: PyImpact sometimes creates a droning audio effect. To prevent this, PyImpact will ignore collision events if the same pair of objects registers an `enter` and `stay` collision event on the same frame.

### Documentation

#### Modified Documentation

| Document           | Description                                                  |
| ------------------ | ------------------------------------------------------------ |
| `impact_sounds.md` | Added a section and code example for how to prevent audio droning. |

## v1.8.4

### Command API

#### Modified Commands

| Command                   | Description                                                  |
| ------------------------- | ------------------------------------------------------------ |
| `set_reverb_space_simple` | Added optional parameters `min_room_volume` and `max_room_volume`. |

### `tdw` module

#### `PyImpact`

- Added: `get_audio_commands(resp, wall, floor)`. This *greatly* simplifies PyImpact by doing all collision detection and command creation under the hood using default audio values.
- Added: `set_default_audio_info(object_names)`. Set the default audio values and cache the names of each object in the scene.  
- Added fields: `object_info` (cached default object info), `object_names` (cached object IDs and their names in the current scene), `env_id` (dummy ID for the environment)
- Fixed: Objects not present in the Rigidbody output data don't create audio. (This can happen if  your controller set the `ids` value in `send_rigidbodies` to exclude some objects, or if there is a robot in the scene.) As a fallback, PyImpact will try to use default audio values.
- Fixed: Distorted sound if an object scrapes along a wall. Now, scrapes on walls are ignored.
- Fixed: Distorted sound if the sound's amp is <= -1
- Fixed: Distorted sound if an object scrapes along a floor.

### Scene Library

- Added: mm_kitchen_1b, mm_kitchen_2a, mm_kitchen_2b, mm_kitchen_3a, mm_kitchen_3b, mm_kitchen_4a, mm_kitchen_4b

### Example Controllers

- Re-wrote `impact_sounds.py` to use the simplified PyImpact API (i.e. `get_audio_commands()`).

### Build

- Upgraded to Unity 2020.2.7
- Fixed: `rotate_sensor_container_by` rotations around a local axis instead of a world axis
- Fixed: If `set_kinematic_state` is sent more than once in a row to the same object with `kinematic=True`, the collision detection mode will be set incorrectly.
- Fixed: Audio glitches when using Resonance Audio because the playback is doubled.
- Fixed: ZMQ error if the build is launched a few seconds before the controller is launched.
- Fixed: Can't draw Flex particles in Linux (see note in upgrade guide).
- Fixed: A potential rare infinite loop if a JSON message can't be deserialized.

### Documentation

#### Modified Documentation

| Document           | Description                                                  |
| ------------------ | ------------------------------------------------------------ |
| `impact_sounds.md` | Added a "simple usage" section and updated the example controller code. |

## v1.8.3

### Command API

### New Commands

| Command                    | Description                                                  |
| -------------------------- | ------------------------------------------------------------ |
| `set_ambient_light`        | Set how much the ambient light from the source affects the scene. |
| `set_hdri_skybox_exposure` | Set the exposure of the HDRI skybox to a given value.        |

#### Modified Commands

| Command                                                | Modification                                                 |
| ------------------------------------------------------ | ------------------------------------------------------------ |
| `set_reverb_space_expert`<br>`set_reverb_space_simple` | Added new materials: `"metal"` and `"wood"`<br>Set the default value of `env_id` to -1 (was 0).<br>If `env_id == -1`, the reverb space will encapsulate the entire scene. |
| `add_position_marker`                                  | Added new shapes: `"circle"` and `"square"`                  |

### Build

- **Fixed: A major bug that causes the build to hang. You are STRONGLY encouraged to upgrade to this version of TDW!**

### Model Library

- Added: basic_cork_2, button_two_hole_green_mottled, square_coaster_001_cork, shoebox_fused, key_dull_metal, round_coaster_indent_wood, square_coaster_001_marble, button_two_hole_red_wood, round_coaster_cherry, button_two_hole_grey, square_coaster_rubber, 4ft_shelf_metal, button_four_hole_red_plastic, key_shiny, tapered_cork, cork_plastic_black, square_coaster_wood, button_four_hole_wood, champagne_cork, round_coaster_indent_stone, aaa_battery, square_coaster_stone, button_four_hole_white_plastic, button_four_hole_mottled, button_four_hole_large_black, bung, basic_cork, round_coaster_indent_rubber, round_coaster_stone, square_coaster_001_wood, 9v_battery, button_four_hole_large_wood, key_brass, tapered_cork_w_hole, round_coaster_stone_dark, button_two_hole_red_mottled, cork_plastic

### Scene Library

- Added: mm_kitchen_1a

## v1.8.2

### `tdw` module

### `Controller`

- Fixed: When checking for TDW updates, the recommendation to upgrade gives the incorrect release version if the third number in the version is above 9 (e.g. 1.7.16)

#### `RobotCreator`

- Added: `robot_creator.py` **Frontend users can now add robots to TDW, given the URL of a .urdf or .xacro file.** See: `tdw/Documenation/misc_frontend/robotics.md` and `tdw/Documentation/python/robot_creator.md`

#### Backend

- Added: `asset_bundle_creator_base.py` Shared code between `asset_bundle_creator.py` and `robot_creator.py`

### Robot Library

- Added new robots: Baxter, Sawyer, Niryo One, Fetch, Shadowhand, UR5, and UR10

### Build

- Upgraded to Unity 2020.2.5

### Example Controllers

- `robot_arm.py` uses the UR5 robot instead of the UR3 robot

### Documentation

#### New Documentation

| Document | Description |
| --- | --- |
| `robot_creator.md`             | API documentation for `RobotCreator` as well as installation instructions and troubleshooting tips. |
| `asset_bundle_creator_base.md` | API documentation for `AssetBundleCreatorBase`               |

#### Modified Documentation

| Document                       | Modification                                                 |
| ------------------------------ | ------------------------------------------------------------ |
| `robots.md`                    | Added a section for how to start using the new `RobotCreator` |

## v1.8.1

### Command API

#### New Commands

| Command              | Description                                                  |
| -------------------- | ------------------------------------------------------------ |
| `set_socket_timeout` | Set the timeout duration for the socket used to communicate with the controller. |

### `tdw` module

#### `Controller`

- **Fixed: The connection to the build will occasionally fail, causing the controller to hang indefinitely.** Now, the build will close its socket, open a new socket, and alert the controller that it should re-send the previous message. This won't advance the simulation in any way but you might notice a few-second hiccup between messages.

### Benchmarking

- Increased the default number of trials from `benchmarker.py` from 10,000 to 50,000
- Fixed: `build_simulator.py` doesn't terminate automatically.
- Fixed: `controller_simulator.py` doesn't work.
- Removed: `req_test_controller.py` because ReqTest isn't supported in TDW anymore.
- Removed: `req_test_builder.py`

### Documentation

#### Modified Documentation

| Document        | Modification                                                 |
| --------------- | ------------------------------------------------------------ |
| `unity_loop.md` | Removed test results that involve ReqTest because they aren't actually that meaningful. |
| `debug_tdw.md`  | Added some information about what to do if the network connection hangs. |

## v1.8.0

### New Features

- Added a [robotics API](misc_frontend/robots.md) to TDW. For now, the total number of robots is small, but we'll add more over time.
  - Added the [Magnebot](misc_frontend/magnebot.md) to TDW.
  - Deprecated the Sticky Mitten Avatar (see [upgrade guide](Documentation/upgrade_guides/v1.7_to_v1.8)).
- Significant graphics improvements in certain scenes because many models didn't cast shadows or reflect light correctly.
- Updated Unity Engine from 2019.4 to 2020.2
- Fixed: OS X and Linux builds don't have executable flags. In order to preserve permissions, they are now stored online as .tar.gz files instead of .zip files.

### Known bugs

#### Bug: Can't create a Linux build without deleting some Flex shader files

_(This is relevant only to users who have access to the C# source code in the private TDWBase repo.)_

To create a Linux build, delete all Flex shaders located in `TDWBase/Assets/NVIDIA/Flex/Resources/Shaders` that have `DrawParticles` or `Fluid` in their name. Otherwise, the Editor will crash to desktop. This is handled automatically when we build and upload TDW releases to GitHub.

#### Bug: Can't draw Flex particles on Linux

It's currently not possible to draw Flex particles (`"draw_particles"` in the Command API) in Linux. Attempting to create a build with the Flex particle shaders for Linux results in a crash-to-desktop. This is new as of Unity 2020.2.2 and it is likely that a future Unity Engine upgrade (i.e. to Unity 2020.2.x) will fix it. As a matter of course, we apply minor Unity Engine updates to TDW whenever they're available. Should one of these updates fix this particular issue, we'll note it in the changelog.

### Command API

#### New Commands

| Command                    | Description                                                  |
| -------------------------- | ------------------------------------------------------------ |
| `add_magnebot`             | Add a Magnebot to the scene.                                 |
| `add_robot`                | Add a robot to the scene.                                    |
| `destroy_robot`            | Destroy a robot in the scene.                                |
| `parent_avatar_to_robot`   | Parent an avatar to a robot.                                 |
| `set_immovable`            | Set whether or not the root object of the robot is immovable. |
| `teleport_robot`           | Teleport the robot to a new position and rotation.           |
| `detach_from_magnet`       | Detach an object from a Magnebot magnet.                     |
| `set_magnet_targets`       | Set the objects that the Magnebot magnet will try to pick up. |
| `set_robot_joint_drive`    | Set static joint drive parameters for a robot joint.         |
| `set_robot_joint_mass`     | Set the mass of a robot joint.                               |
| `set_prismatic_target`     | Set the target position of a prismatic robot joint.          |
| `set_revolute_target`      | Set the target angle of a revolute robot joint.              |
| `set_spherical_target`     | Set the target angles (x, y, z) of a spherical robot joint.  |
| `send_magnebots`           | Send data for each Magnebot in the scene.                    |
| `send_robots`              | Send dynamic data (position, rotation, velocity, etc.) of each robot and each robot's body parts in the scene. |
| `send_static_robots`       | Send static data that doesn't update per frame (such as segmentation colors) for each robot in the scene. |
| `add_trigger_color`        | Add a non-physics trigger collider to an object.             |
| `set_legacy_shaders`       | Set whether TDW should use legacy shaders (pre-v1.8) for its models. |
| `enable_reflection_probes` | Enable or disable the reflection probes in the scene.        |

#### Modified Commands

| Command | Modification |
| --- | --- |
| `set_vingette` | By default, the post-processing vignette is disabled, i.e. the parameter  `enabled = False` (was `True`). |
| `rotate_object_to_euler_angles` | Added optional parameter `use_centroid` |
| `rotate_object_to` | Added optional parameter `use_centroid` |

#### Removed Commands

| Command               | Reason                                                   |
| --------------------- | -------------------------------------------------------- |
| `toggle_image_sensor` | Deprecated in v1.7<br>Use `enable_image_sensor` instead. |

#### Deprecated Commands

| Command                                                      | Reason                                                       |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| `set_avatar_rigidbody_constraints`<br>`rotate_head_by`<br>`rotate_waist`<br>`set_sticky_mitten_profile`<br>`stop_arm_joint`<br>`bend_arm_joint_by`<br>`bend_arm_joint_to`<br>`adjust_joint_angular_drag_by`<br>`set_joint_angular_drag`<br>`adjust_joint_damper_by`<br>`adjust_joint_force_by`<br>`set_joint_damper`<br>`set_joint_force`<br>`put_down`<br>`set_stickiness`<br>`pick_up`<br>`pick_up_proximity` | The Sticky Mitten Avatar has been deprecated (see "Features"). |
| `add_fixed_joint`                                            | Very buggy and used only in the Sticky Mitten Avatar high-level API, which has been deprecated. |
| `set_proc_gen_reflection_probe`                              | Use `enable_reflection_probes` instead.                      |

### Output Data

#### New Output Data

| Output Data        | Description                                     |
| ------------------ | ----------------------------------------------- |
| `Magnebot`         | Data for a Magnebot.                            |
| `Robot`            | Data for a robot.                               |
| `StaticRobot`      | Static data for a robot.                        |
| `TriggerCollision` | Data for a non-physics trigger collision event. |

### Modified Output Data

| Output Data            | Modification            |
| ---------------------- | ----------------------- |
| `EnvironmentCollision` | Added: `get_is_floor()` |

### `tdw` module

#### `Controller`

- Added: `get_add_robot()`. Returns a valid `add_robot` command.

#### `FloorplanController`

- Updated floorplans to allow the Magnebot to move around. Removed rugs.
- Made some more objects kinematic.
- Replaced white_shopping_bag with blue_satchal.

#### `TDWUtils`

- Removed: `get_collisions()`

#### `QuaternionUtils`

- Renamed `_UP` to `UP`
- Added: `FORWARD` and `IDENTITY`

#### `AssetBundleCreator`

- Now requires Unity 2020.2

#### Misc.

- Added: `collisions.py` A useful wrapper for collision data.
- Added: `int_pair.py` A pair of unordered hashable integers. Use this class for dictionary keys.
- Added: `RobotLibrarian` and `RobotRecord`.
- Fixed: `missing_materials.py` will launch the build (which isn't useful for tests).
- Updated `build.py` to download OS X and Linux builds correctly. Removed the `chmod()` function because it's no longer needed.

### Model Library

- Fixed: sixty-four models in `models_full.json`(*not* `models_core.json`) have `flex == True` in the metadata record but have non-readable meshes (meaning that they can't be used in Flex). They now have `flex == False` in the metadata record. 

### Scene Library

- Updated the asset bundle for `archviz_house_2018` and renamed it to `archviz_house`.
- Updated the asset bundle for `tdw_room_2018` and renamed it to `tdw_room`.

### Build

- Image capture is slightly faster.
- Log messages written to the player log (and console log in Unity Editor) include the type of object that logged the message. This doesn't affect the text sent by `send_log_messages`.
- Fixed: Many models don't cast shadows or reflect light correctly.
- Fixed: The bounds of objects aren't set correctly if `add_object["rotation"]` isn't (0, 0, 0)
- Fixed: The build often returns `EnvironmentCollision` data when it should return `Collision` data.
- Fixed: `_normals` pass is inaccurate.

### Example Controllers

- Added: `collisions.py`  Receive collision output data and read it as a `Collisions` object.
- Added: `magnebot.py` Example of how to use the Magnebot.
- Added: `robot_arm.py` Add a robot to the scene and bend its arm.
- Added: `robot_camera.py` Add a camera to a Magnebot.
- Removed: `open_box.py` (it uses the Sticky Mitten Avatar, which has been deprecated).
- Removed: `sticky_mitten_avatar.py` (it uses the Sticky Mitten Avatar, which has been deprecated).
- Fixed: `avatar_drag.py` doesn't work.
- Fixed: `composite_object.py` doesn't work on OS X.

### Documentation

#### New Documentation

| Document             | Description                             |
| -------------------- | --------------------------------------- |
| `v1.7_to_v1.8.md`    | Upgrade guide.                          |
| `robots.md`          | Overview of the robotics API.           |
| `robot_librarian.md` | API documentation for `RobotLibrarian`. |

### Benchmarking

- Removed `variance_avatar.py` test because the Sticky Mitten Avatar has been deprecated.

# v1.7.x

To upgrade from TDW v1.6 to v1.7, read [this guide](Documentation/upgrade_guides/v1.6_to_v1.7).

## v1.7.16

### Command API

#### Modified Commands

| Command            | Modification                            |
| ------------------ | --------------------------------------- |
| `rotate_object_by` | Added optional parameter `use_centroid` |

### `tdw` module

#### `Controller`

- Fixed: Crash at start in certain Pyhon environments because there is no version number at the expected position of a string from PyPi.

#### Model Library

- Fixed: The colliders of pipe, torus, bowl, and dumbbell in `models.flex.json` are single convex meshes instead of a group of convex hulls.

## v1.7.15

### Output Data

#### Modified Output Data

| Output Data | Modification                                                 |
| ----------- | ------------------------------------------------------------ |
| `Images`    | Removed: `get_uv_starts_at_top()` (it's not actually useful). |

### `tdw` module

#### `TDWUtils`

- Added optional parameters `far_plane` and `near_plane` to `get_depth_values()`.
- Added optional parameters `far_plane` and `near_plane` to `get_point_cloud()`.

### Build

- **Fixed: `_depth` and `_depth_simple` passes are inaccurate.** Both passes now correctly encode depth values.

### Documentation

#### New Documentation

| Document   | Description                   |
| ---------- | ----------------------------- |
| `depth.md` | How to use depth maps in TDW. |

#### Modified Documentation

| Document             | Description                                                  |
| -------------------- | ------------------------------------------------------------ |
| `getting_started.md` | Fixed: Instructions for how to run TDW on a remote server are incorrect. |

## v1.7.14

### Output Data

#### Modified Output Data

| Output Data | Modification                                                 |
| ----------- | ------------------------------------------------------------ |
| `Images`    | Added: `get_width()`, `get_height()`, and `get_uv_starts_at_top()`<br>The `_depth` and `_depth_simple` passes are now raw RGB render texture data instead of png files (they can still be saved as png files via `TDWUtils.save_images()`). |

### `tdw` module

#### `TDWUtils`

- Added optional parameters `width`, `height`, and `uv_starts_at_top` to `get_depth_values()`.
- Added: `get_point_cloud()`. Create a point cloud from an numpy array of depth values.
- Added: `get_shaped_depth_pass()`. Reshape a depth pass into a 2D RGB array.

### Build

- Fixed: `_depth` and `_depth_simple` passes are (still) inaccurate.

### Example Controllers

- `depth_shader.py` generates a depth values plot and saves out a point cloud file.

## v1.7.13

### `tdw` module

#### `TDWUtils`

- Added optional parameter `depth_pass` to `get_depth_values()` to allow the function to decode data from a `_depth_simple` pass.

### Build

- Fixed: `_depth` and `_depth_simple` passes are inaccurate.

## v1.7.12

### Command API

#### New Commands

| Command         | Description                                                  |
| --------------- | ------------------------------------------------------------ |
| `follow_object` | Teleport the avatar to a position relative to a target. This must be sent per-frame to continuously follow the target. |

### `tdw` module

#### `QuaternionUtils`

- Added: `get_inverse()` Returns the inverse quaternion.
- Added: `world_to_local_vector()` Convert a vector position in absolute world coordinates to relative local coordinates.

## v1.7.11

### Command API

#### New Commands

| Command                 | Description                                                  |
| ----------------------- | ------------------------------------------------------------ |
| `send_screen_positions` | Given a list of worldspace positions, return the screenspace positions according to each of the avatar's camera. |

#### Modified Commands

| Command               | Modification                                                 |
| --------------------- | ------------------------------------------------------------ |
| `add_position_marker` | Fixed: The `a` value of `color` doesn't adjust the transparency.<br>Added: optional parameter `shape`. |

### Output Data

#### New Output Data

| Output Data      | Description                                       |
| ---------------- | ------------------------------------------------- |
| `ScreenPosition` | A worldspace position in screenspace coordinates. |

## v1.7.10

### Command API

#### Modified Commands

| Command          | Description                                                  |
| ---------------- | ------------------------------------------------------------ |
| `set_pass_masks` | Added `_albedo` pass. This only color and texture,  as if lit with only ambient light. |

### `tdw` module

#### `QuaternionUtils`

- Added: `get_y_angle()` The angle between two quaternions in degrees around the y axis.

## v1.7.9

### Command API

#### New Commands

| Command         | Description                  |
| --------------- | ---------------------------- |
| `send_keyboard` | Request keyboard input data. |

### Output Data

#### New Output Data

| Output Data | Description          |
| ----------- | -------------------- |
| `Keyboard`  | Keyboard input data. |

### `tdw` module

- Removed `keyboard` as a required module.

#### `KeyboardController`

- Controller now uses `Keyboard` output data from the simulator to detect keyboard input instead of the Python `keyboard` module, which is less reliable and doesn't work on OS X.

## v1.7.8

### Python

#### `AssetBundleCreator`

- **`AssetBundleCreator` works on Linux.**
- Added optional `display` parameter to constructor.

### Build

- Fixed: Output from the NavMeshAvatar isn't synced with TDW's simulation steps.

### Benchmark

- Added: `benchmarking/variance.py` Test how deterministic the physics simulation is.
- Added: `benchmarking/variance_avatar.py` Test how deterministic the physics simulation with a Sticky Mitten Avatar is.

### Documentation

#### New Documentation

| Document         | Description                    |
| ---------------- | ------------------------------ |
| `determinism.md` | Physics determinism benchmark. |

#### Modified Documentation

| Document    | Modification                                                 |
| ----------- | ------------------------------------------------------------ |
| `README.md` | Fixed: Some links aren't full URLs (this is ok for GitHub but results in dead links on the PyPi page). |

## v1.7.7

### Build

- When the build fails to deserialize a list of commands, the error message is more informative.
- Fixed: Various graphics glitches when enabling/disabling cameras.
- Fixed: `Bounds` output data is incorrect.

### Documentation

#### Modified Documentation

| Document       | Modification                                       |
| -------------- | -------------------------------------------------- |
| `debug_tdw.md` | Added a section for JSON serialization exceptions. |

## v1.7.6

### Command API

#### New Commands

| Command                            | Description                                              |
| ---------------------------------- | -------------------------------------------------------- |
| `set_avatar_rigidbody_constraints` | Set the rigidbody constraints of a Sticky Mitten Avatar. |
| `add_fixed_joint`                  | Attach one object to another.                            |

#### Modified Commands

| Command            | Modification                        |
| ------------------ | ----------------------------------- |
| `rotate_object_to` | Added optional `physics` parameter. |

### `tdw` module

#### `TDWUtils`

- Added: `get_collisions()` Returns a list of collisions on this frame.
- Added: `get_bounds_dict()` Converts bounds data to a dictionary.
- Added: `get_closest_position_in_bounds()` Returns the position on the object bounds closest to `origin`.
- Added: `get_angle()` Returns the angle in degrees between `forward` and the direction vector from `origin` to `position`.
- Added: `get_angle_between()` Returns the angle in degrees between two directional vectors.
- Added: `rotate_position_around()` Returns a position rotated by a given angle around a given origin.

### Benchmarking

- Benchmark controllers no longer automatically launches the build.

## v1.7.5

### Command API

#### New Commands

| Command               | Modification             |
| --------------------- | ------------------------ |
| `enable_image_sensor` | Turn a sensor on or off. |

#### Modified Commands

| Command              | Modification                                                 |
| -------------------- | ------------------------------------------------------------ |
| `send_nav_mesh_path` | Removed parameter `frequency`.<br/>Fixed: Can only receive one `NavMeshPath` output data object. |

#### Deprecated Commands

| Command               | Reason                                                       |
| --------------------- | ------------------------------------------------------------ |
| `toggle_image_sensor` | Functionality can be replicated with `enable_image_sensor` (which is easier to use). |

## v1.7.4

### `tdw` module

#### `FloorplanController`

- Replaced some furniture in floorplan layouts.

### Command API

#### New Commands

| Command                  | Description                                                  |
| ------------------------ | ------------------------------------------------------------ |
| `make_nav_mesh_obstacle` | Make a specific object a NavMesh obstacle.                   |
| `send_nav_mesh_path`     | Tell the build to send data of a path on the NavMesh from the origin to the destination. |

#### Modified Commands

| Command           | Modification                            |
| ----------------- | --------------------------------------- |
| `send_spherecast` | Added optional parameter `id`.          |
| `send_raycast`    | Renamed parameter `raycast_id` to `id`. |

### Output Data

#### New Output Data

| Output Data   | Description                    |
| ------------- | ------------------------------ |
| `NavMeshPath` | A path on the scene's NavMesh. |

## v1.7.3

### `tdw` module

#### `TDWUtils`

- Added: `color_to_hashable()`. Convert a color to a hashable integer.
- Added: `hashable_to_color()`. Convert a hashable integer to a color.

### Model Library

- Added to `models_core.json`:
  - hexagonal_toy

### Build

- Fixed: The objects created by `add_position_marker` initially have colliders, potentially causing physics interactions.

## v1.7.2

### Command API

#### New Commands

| Command                        | Description                                                  |
| ------------------------------ | ------------------------------------------------------------ |
| `adjust_joint_angular_drag_by` | Adjust the angular drag of a joint of a Sticky Mitten Avatar by a delta. |
| `set_joint_angular_drag`       | Set the angular drag of a joint of a Sticky Mitten Avatar.   |
| `set_joint_damper`             | Set the current damper of a joint of a Sticky Mitten Avatar. |
| `set_joint_force`              | Set the force of a joint of a Sticky Mitten Avatar.          |

#### Modified Commands

| Command                     | Modification                                  |
| --------------------------- | --------------------------------------------- |
| `set_sticky_mitten_profile` | Added parameter `angular_drag` to each joint. |

### `tdw` module

#### `FloorplanController`

- Removed the floor and objects from the "patio" area of floorplan_4a, floorplan_4b, and floorplan_4c
- Removed "container" objects from all layouts.

### Model Library

- Added to `models_core.json`:
  - h-shape_wood_block
  - half_circle_wood_block
  - pentagon_wood_block
  - t-shape_wood_block
  - square_wood_block
  - star_wood_block
  - rectangle_wood_block
  - l-shape_wood_block

### Documentation

#### Modified Documentation

| Document                  | Modification                                        |
| ------------------------- | --------------------------------------------------- |
| `sticky_mitten_avatar.md` | Updated example JSON for the sticky mitten profile. |

## v1.7.1

### Command API

#### Modified Commands

| Command                     | Modification                                                 |
| --------------------------- | ------------------------------------------------------------ |
| `set_sticky_mitten_profile` | Fixed: This command doesn't work.<br>Removed `mitten` (redundant because of `wrist_pitch`). |

### Python

#### Use Cases

- Fixed: `rube_goldberg.py` doesn't work.

#### Benchmarking

- Added: `struct_deserialization.py` Test the speed of deserializing structs such as Vector3 and Quaternion.

### Build

- Increased deserialization speed of many commands.

### Documentation

#### Modified Documentation

| Document                     | Modification                                 |
| ---------------------------- | -------------------------------------------- |
| `command_deserialization.md` | Added results of `struct_deserialization.py` |

## v1.7.0

### Command API

#### New Commands

| Command                | Description                                      |
| ---------------------- | ------------------------------------------------ |
| `send_overlap_box`     | Check what a box-shaped space overlaps with.     |
| `send_overlap_capsule` | Check what a capsule-shaped space overlaps with. |
| `send_overlap_sphere`  | Check what a sphere-shaped space overlaps with.  |

#### Modified Commands

| Command                               | Modification                                                 |
| ------------------------------------- | ------------------------------------------------------------ |
| `set_avatar_collision_detection_mode` | Default value of `mode` is `"continuous_dynamic"` (was `"continuous_speculative"`).<br>Added additional values for `mode`: `"continuous"` and `"discrete"`. |
| `set_object_collision_detection_mode` | Default value of `mode` is `"continuous_dynamic"` (was `"continuous_speculative"`).<br/>Added additional values for `mode`: `"continuous"` and `"discrete"`. |

### Output Data

#### New Output Data

| Output Data | Description                                    |
| ----------- | ---------------------------------------------- |
| `Overlap`   | The IDs of every object that a shape overlaps. |

### `tdw` module

#### `TDWUtils`

- Fixed: `get_depth_values()` is inaccurate due to overflow errors.

#### `AssetBundleCreator`

- Upgraded the `asset_bundle_creator` Unity project from Unity 2019.2 to Unity 2019.4 (see `v1.6_to_v1.7.md`).

### Scene Library

- Removed: `roman_villa`

### Use Cases

- Removed `roman_villa` from scenes that `humanoid_video.py` will use.

### Build

- **Upgraded Unity3D Engine from 2019.2 to 2019.4**
  - Upgrade PhysX, which overall improves the quality of physics simulations.
  - Enabled "Enhanced Determinism". Physics is much more deterministic.
- Set the default collision detection mode of all objects and avatars to `continuous_dynamic` (was `continuous_speculative`, which is less accurate.)

### Documentation

#### New Documentation

| Document          | Description    |
| ----------------- | -------------- |
| `v1.6_to_v1.7.md` | Upgrade guide. |

#### Modified Documentation

| Document       | Description                                                  |
| -------------- | ------------------------------------------------------------ |
| `debug_tdw.md` | Clarified where to find the player log.<br>Added a section for network errors. |

# v1.6.x

## v1.6.14

### `tdw` module

- Added: `tdw.tdw_utils.QuaternionUtils` Utility functions for quaternions.

#### `TDWUtils`

- Moved `euler_to_quaternion()` to `QuaternionUtils`
  - Renamed function to `euler_angles_to_quaternion()`
  - Parameter `euler` is a numpy array (was a tuple).
  - Return type is a numpy array (was a list of floats).
- Moved `quaternion_to_euler_angles()` to `QuaternionUtils`

#### `PyImpact`

 - Fixed:  relative amp values aren't handled correctly.

### Python

- Fixed: `screenshotter.py` and `empty_scene` don't work on Linux.

### Scene Library

- Fixed: `box_room_2018` doesn't have colliders on the walls or ceiling.

### Build

- Fixed: `send_collisions` doesn't reset correctly when sent multiple times with different values for `enter`, `exit`, or `stay`.

## v1.6.13

### `tdw` module

#### `PyImpact`

- Added audio values for more objects.

#### `FloorplanController`

- Updated floorplan 4, layout 0
- Added scenes `1a`, `1b`, and `1c`, which have layouts `1`, `2`, and `3`.
- Added scenes `5a`, `5b`, and `5c`, which have layouts `1`, `2`, and `3`.

### Scene Library

- Added scenes:
  - floorplan_1a
  - floorplan_1b
  - floorplan_1c

## v1.6.12

### Command API

#### New Commands

| Command           | Description                                                  |
| ----------------- | ------------------------------------------------------------ |
| `send_spherecast` | Cast a sphere along a direction and return the results. The can be multiple hits, each of which will be sent to the controller as Raycast data. |

### Output Data

#### Modified Output Data

| Output Data | Modification                                                 |
| ----------- | ------------------------------------------------------------ |
| `Raycast`   | Added: `get_hit_object()` Returns true if the raycast hit an object. |

### `tdw module`

#### `PyImpact`

- Added parameter `resonance` to `ObjectInfo`.
- Added optional parameter `logging` to PyImpact's constructor.
- Added: `PyImpact.get_log()`
- Added: `PyImpact.log_modes()`
- Added parameter `resonance` to `PyImpact.get_sound()`,   `PyImpact.get_impact_sound_command()`, `PyImpact.make_impact_audio()`, `PyImpact.get_impulse_response()`,  and`PyImpact.synth_impact_modes()`
- Added resonance values to `objects.csv`.

#### `FloorplanController`

- For scenes `2a`, `2b`, and `2c`, added layouts `1` and `2`
- Added scenes `4a`, `4b`, and `4c`, which have layouts `1`, `2`, and `3`.

### Model Library

- Added to `models_core.json` and `models_full.json`:
  - basket_18inx18inx12iin
  - basket_18inx18inx12iin_bamboo
  - basket_18inx18inx12iin_plastic_lattice
  - basket_18inx18inx12iin_wicker
  - basket_18inx18inx12iin_wood_mesh
  - box_18inx18inx12in_cardboard
  - box_24inx18inx12in_cherry
  - box_tapered_beech
  - box_tapered_white_mesh
  - round_bowl_large_metal_perf
  - round_bowl_large_padauk
  - round_bowl_large_thin
  - round_bowl_small_beech
  - round_bowl_small_walnut
  - round_bowl_talll_wenge
  - shallow_basket_white_mesh
  - shallow_basket_wicker
- In `models_core.json` and `models_full.json`, flagged `rope_table_lamp`, `salt`, and `jigsaw_puzzle_composite` as `do_not_use` due to bad physics behavior.

### Build

- Fixed: `Environments.get_center()` (output data) is sometimes inaccurate. 

### Use Cases

- `rube_goldberg.py` logs audio mode data.

## v1.6.11

### `tdw` module

- Added: `FloorplanController`. Load a interior environment scene and populate it with furniture and props.
- Added: object initialization data classes:
  - `TransformInitData`: Create object and set their positions, rotations, etc.
  - `RigidbodyInitData`: Create objects and set their positions, rotations, and physics properties.
  - `AudioInitData`: Create objects and set their positions, rotations, and physics properties from their PyImpact audio values.
- Added: `floorplan_layouts.json` Floorplan layouts recipes are stored in this file.

#### `PyImpact`

- Added default audio values for many more objects.

### Model Library

- Added to `models_core.json` and `models_full.json`:
  - 24_in_wall_cabinet_white_wood
  - 24_in_wall_cabinet_wood_beach_honey
  - 36_in_wall_cabinet_white_wood
  - 36_in_wall_cabinet_wood_beach_honey
  - bed01
  - bed01_blue
  - bed01_red
  - blue_rug
  - cabinet_24_door_drawer_wood_beach_honey
  - cabinet_24_singledoor_wood_beach_honey
  - cabinet_24_two_drawer_white_wood
  - cabinet_24_two_drawer_wood_beach_honey
  - cabinet_24_white_wood
  - cabinet_24_wood_beach_honey
  - cabinet_36_white_wood
  - cabinet_36_wood_beach_honey
  - cabinet_full_height_white_wood
  - cabinet_full_height_wood_beach_honey
  - carpet_rug
  - elf_painting
  - flat_woven_rug
  - fruit_basket
  - its_about_time_painting
  - purple_woven_rug
  - silver_frame_painting
  - sink_base_white_wood
  - sink_base_wood_beach_honey
- Removed from `models_core.json` and `models_full.json`:
  - `flat-woven-rug`

### Scene Library

- Added new scenes:
  - floorplan_2a
  - floorplan_2b
  - floorplan_2c
  - floorplan_3a
  - floorplan_3b
  - floorplan_3c
  - floorplan_4a
  - floorplan_4b
  - floorplan_4c
  - floorplan_5a
  - floorplan_5b
  - floorplan_5c

### Documentation

#### New Documentation

| Document                  | Description                                                  |
| ------------------------- | ------------------------------------------------------------ |
| `floorplan_controller.md` | API document for `FloorplanController`                       |
| `object_init_data.md`     | API document for `TransformInitData`, `RigidbodyInitData`, and `AudioInitData` |

## v1.6.10

### Command API

#### New Commands

| Command        | Description                                    |
| -------------- | ---------------------------------------------- |
| `send_raycast` | Cast a ray from the origin to the destination. |

#### Modified Commands

| Command          | Modification                                                 |
| ---------------- | ------------------------------------------------------------ |
| `set_pass_masks` | Added `_depth_simple` pass. This is a grayscale image that is less precise than the `_depth` pass, but is faster and easier to use. |

### Output Data

#### New Output Data

| Output Data | Description                                                  |
| ----------- | ------------------------------------------------------------ |
| `Raycast`   | A ray cast from an origin to a destination and what, if anything, it hit. |

### Model Libraries

- Added to `models_core.json` and `models_full.json`:
  - dining_room_table
  - flat-woven-rug
  - framed_painting

## v1.6.9

### Build

- Fixed: `pick_up` and `pick_up_proximity` sometimes try to pick up StickyMittenAvatar body parts.
- Fixed: In `AvatarSegmentationColor` output data, the ID of the root object of a StickyMittenAvatar (`A_StickyMitten_Adult(Clone)_<id>_` or `A_StickyMitten_Baby(Clone)_<id>_`) doesn't match `AvatarSegmentationColor.get_id()`.
- Fixed: Collisions between two body parts of a StickyMittenAvatar are processed as `EnvironmentCollision` output data (they are now ignored).
- Fixed: `teleport_object` doesn't update the positions of an object's `Bounds` data.

## v1.6.8

### Output Data

#### Modified Output Data

| Output Data          | Modification                                                 |
| -------------------- | ------------------------------------------------------------ |
| `AvatarStickyMitten` | Added functions to get the position, rotation, and forward of the center of the mittens (as opposed to the joint location. |

### Example Controllers

- Added: `pass_masks.py` Generate each pass mask.

### Build

- Fixed: `_mask` image pass doesn't work.

### Documentation

#### Modified Documentation

| Document | Modification |
| --- | --- |
| `command_api.md` | Added explanations and images for each `PassMask` in `set_pass_masks`. |
| `observation_data.md` | Added a link to `set_pass_masks` documentation in the Command API. |

## v1.6.7

### `tdw` module

#### `Controller`

- Fixed: Build doesn't launch in Windows.

#### `AssetBundleCreator`

- Fixed: `AssetBundleCreator.get_local_urls()` doesn't add the OS X URL.
- Fixed: `AssetBundleCreator.get_local_urls()` generates paths with `\` instead of `/`.

#### `TDWUtils`

- Added: `quaternion_to_euler_angles()` Convert a quaternion to Euler angles.

#### `PyImpact`

- Added: `get_impulse_response()` Generate an impulse response from specified modes for two objects.

#### `Base64Sound` (in `tdw.py_impact`)

- Added new field: `bytes` The byte data before it is encoded to base64.

#### Librarian (`tdw.librarian`)

- Fixed: Relative URLs in records don't work as expected.

### `asset_bundle_creator` (Unity project)

- Fixed: The names of objects in the substructure data always include the suffix `(Clone)`. To apply this bug fix, delete the directory `~/asset_bundle_creator` where `~` is your home directory. The next time you create a local asset bundle, the Unity project will be recreated.

## v1.6.6

### Command API

#### New Commands

| Command                               | Description                                       |
| ------------------------------------- | ------------------------------------------------------------ |
| `look_at_avatar`                       | Look at another avatar. |
| `add_position_marker` | Create a non-physics, non-interactive sphere to mark a position in the scene. |
| `remove_position_markers` | Remove all position markers from the scene. |

#### Modified Commands

| Command | Modification |
| --- | --- |
| `set_stickiness` | Added optional parameter `show`. If true, colorize the sides of the mitten that are sticky. |

#### Deprecated Commands

| Command | Reason |
| --- | --- |
| `send_avatar_children_names` | This info can be found via `send_avatar_segmentation_colors` |

### Output Data

#### Modified Output Data

| Output Data | Modification |
| --- | --- |
| `AvatarStickyMitten` | Added: `get_angles_left()` and `get_angles_right()` Returns current joint angles. |

### `tdw` module

#### `Controller`

- Fixed: Controller tries to launch a build, then check the version, and then delete the build if the version is out of date (all builds now include a `version.txt` file that the controller will read before trying to launch a build).

#### `AssetBundleCreator`

- **Added support for OS X.**

#### Backend

  - Moved Windows binaries used in `AssetBundleCreator` from `exe/` to `binaries/Windows`
  - Added OS X binaries for `AssetBundleCreator`: `binaries/Darwin`

### Example Controllers

- `local_object.py` works in OS X (previously it only worked in Windows)

### Build

- Fixed: The `scale_object` command doesn't update the object's `Bounds` data.

### Documentation

#### Modified Documentation

| Document       | Description                                                  |
| -------------- | ------------------------------------------------------------ |
| `debug_tdw.md` | Added a section on common problems when installing TDW. Reorganized the list of player log messages. Added a section for Unity credential problems. |
| `add_local_object.md` | Added note that AssetBundleCreator works in OS X. |
| `shapenet.md` | Added note that shapenet.py runs in OS X. |

## v1.6.5

### `tdw` module

- Added required modules: `pyinstaller` and `keyboard`
- Added `tdw.keyboard_controller` A controller that can listen to keyboard input.

#### `Controller`

- Removed optional `display` parameter. It doesn't actually work; Linux users should instead launch the controller with a `DISPLAY` environment variable.

#### Backend

- Adjusted how Flatbuffers imports numpy so that frozen controller code works.

### Example Controllers

- Renamed `keyboard.py` to `keyboard_controller.py` to avoid a name clash with the `keyboard` module. Rewrote the code to use the `KeyboardController` class.

### Build

- Fixed: Segmentation colors are often non-unique.

### Misc.

- Added `freeze.py`. "Freeze" your controller into a portable binary executable.
  - Added `controller.spec` (used for freezing controller code).

### Documentation

#### New Documentation

| Document                 | Description                                                  |
| ------------------------ | ------------------------------------------------------------ |
| `freeze.md`              | How to freeze your controller code into a binary executable. |
| `keyboard_controller.md` | API for KeyboardController.                                  |

#### Modified Documentation

| Document             | Description                                                |
| -------------------- | ---------------------------------------------------------- |
| `getting_started.md` | Fixed instructions for how to start a controller in Linux. |
| `docker.md`          | Fixed some broken links.                                   |

## v1.6.4

### `tdw` module

#### `Controller`

- Don't check the version of the build or download a new build if `launch_build == False`
- Edited the message for when you are using code from the tdw repo that is ahead of PyPi.

#### `TDWUtils`

- Fixed: `validate_amazon_s3()` raises exceptions even if credentials are valid.

#### `PyImpact`

- Added backend code for differentiating between an impact, a scrape, and a roll.
  - `py_impact.CollisionType` An enum of different collision "types"
  - `py_impact.CollisionTypesOnFrame` Contains each type of  collision that a "collider" object experiences in a given frame (for  example, impacts one object while scraping another)

#### `AssetBundleCreator`

- Removed parameter `build_path` from `write_physics_quality()` (obsolete; build is launched automatically)
- Removed parameter `build_path` from `validate()` (obsolete; build is launched automatically)

#### Backend

- Removed parameter `build_path` from `Validator` constructor and `--build_path` command line argument from `validator.py`.
- Removed `--build_path` command line argument from `write_physics_quality.py`.

### Example Controllers

- Added `getting_started.py` This is the controller in the Getting Started guide.

### Docker

- Fixed: Docker file doesn't work.
- Added audio libraries and ffmpeg to the Docker container.
- Updated `docker_controller.py`
- [**Added Docker container to DockerHub**](https://hub.docker.com/r/alters/tdw)
- Added scripts:
  - `docker_tag.sh`: Get the tag for the Docker image installed on this machine.
  - `pull.sh`: Check if your Docker image matches your installed TDW version. If not, pull the correct image.
  - `record_audio_video.sh`: Copied into the container for recording video+audio.
  - `start_container_audio_video.sh`: Start the container and record video+audio.
  - `tdw_version.py`: Print the TDW version.
- Revised `start_container.sh` and `start_container_xpra.sh` to use the new Docker container.

### Documentation

#### New Documentation

| Document             | Description                                             |
| -------------------- | ------------------------------------------------------- |
| `c_sharp_sources.md` | When, and how, to request access to the C# source code. |

#### Modified Documentation

| Document             | Modification                                                 |
| -------------------- | ------------------------------------------------------------ |
| `README.md`          | Removed BinaryManager from `tdw` module table (it's not part of the `tdw` module). |
| `tdw.md`             | Updated for v1.6 and expanded table(s) of contents.          |
| `getting_started.md` | The initial test for new users is `getting_started.py` instead of `objects_and_images.py`.<br/>Added a link to `getting_started.py`.<br/>Edited the example controller code (`getting_started.py`) for clarity. |
| `docker.md` | Rewrote requirements and contents of the container.<br>Added instructions for how to pull the image.<br>Added a list of bash scripts included in the repo. |
| `video.md` | Added better instructions for setting the simulation framerate.<br>**Added instructions for how to record audio+video on a headless server.**<br>Added instructions for using ffmpeg on Windows and OS X. |

## v1.6.3

### `tdw` module

#### `Controller`

- Fixed: Permissions error when launching the build in OS X.

### Build

- Fixed: Non-`_img` pass images don't align with the `_img` pass if the screen size isn't a square.

## v1.6.2

### `tdw` module

- Fixed: `tdw` module doesn't work in virtualenv.

#### `DebugController`

- Added parameters `launch_build` and `display`.

### Build

- Fixed: Downloaded builds don't have execute permissions in OS X or Linux (the downloader now runs `chmod` after extracting the .zip file)
- Fixed: `NullReferenceException` when Sticky Mitten Avatar tries to put down an object that was never held.

### Documentation

#### Modified Documentation

| Document             | Description                                                  |
| -------------------- | ------------------------------------------------------------ |
| `getting_started.md` | 1. The example uses `models_core.json` so it works for everybody.<br>2. Better explanation for how to get object IDs.<br>3. Added image saving to the example. |

## v1.6.1

### New Features

- **Added a working pip module.** It is no longer necessary to download the whole repo to use TDW.
- **The build will automatically launch when you launch a controller.** 
- When you launch a controller, it will automatically check to make sure that your local TDW install it is up-to-date and, if not, offer suggestions for how to upgrade.

For more information, please read [Getting Started](getting_started.md).

### `tdw` module

- `setup.py` now actually works when doing a `pip install`.
- Removed `pymongo` requirement.
- Added `requests` requirement.
- Added `__init__.py` files in `tdw/` and in subdirectories.
- Added new scripts:
    - `tdw/release/build.py` Helper functions for downloading a build from the repo.
    - `tdw/release/pypi.py` Helper functions for version checks vs. PyPi.

#### `Controller`

- Added new constructor parameters:
    - `launch_build` If `True`, the controller will automatically launch a build. If there is no build at the expected location, the controller will download one. Default = `True`
    - `display` If not `None`, and if this is a Linux machine, and if `launch_build == True`, this will launch the build on the matching display.
- If `check_version == True`:
    - The controller will compare the installed `tdw` Python module to the latest PyPi version. If there is a mis-match, it will recommend upgrading; the recommendation it gives will depend on the mismatch (`1.6.0` vs. `1.6.1`; `1.6.1` vs. `1.7.0`, etc.)
    - The controller will compare the version of the downloaded build to the version of the install `tdw` Python module. If they are different versions, it will show the user how to upgrade/downgrade.
- Added: `Controller.launch_build()` Launch the build. If there is no build in the expected location, download one.

#### `tdw.backend.paths`

- Added: `SYSTEM_TO_EXECUTABLE` and `SYSTEM_TO_RELEASE`

### Example Controllers

- `minimal.py` terminates the build after its test.

### Backend

- Added `MANIFEST.in` to `tdw` module.
- Removed `Python/README.md` (this was a copy of the repo's README and is not actually needed for PyPi).
- Removed `tdw.version.last_stable_version` (not needed)

### Documentation

#### New Documentation

| Document | Description |
| --- | --- |
| `build.md` | `Build` class API. |
| `pypi.md` | `PyPi` class API. |

#### Modified Documentation

| Document | Modification |
| --- | --- |
| `getting_started.md` | 1. Added a section for expected coding knowledge.<br>2. Re-wrote instructions for how to install TDW using the pip module.<br>3. Expanded installation instructions for remote servers.<br>4. Explicitly mention when it is required to clone this repo. |
| `releases.md` | Added a section about how version-checking works. |

## v1.6.0

This changelog is only for the _frontend_ of TDW. If you are a backend developer, or are looking for changes prior to v1.6.0, please refer to the changelog in TDWBase.

### New Features

- **Began new `tdw` repo (split from the private dev `TDWBase` repo).**
  - Removed backend scripts and documentation (they are still in `TDWBase`).

### Command API

#### Modified Commands

| Command                               | Modification                                                 |
| ------------------------------------- | ------------------------------------------------------------ |
| `create_avatar`                       | Parameter `id` now has a default value: `"a"`.               |
| `set_rendering_quality`               | Parameter `render_quality` now has a default value: `5`      |
| `scale_avatar`                        | Parameter `scale_factor` now has a default value: `{"x": 1, "y": 1, "z": 1}` |
| `set_avatar_collision_detection_mode` | Parameter `mode` now has a default value: `"continuous_speculative"`. |
| `set_avatar_forward`                  | Parameter `forward` now has a default value: `{"x": 0, "y": 0, "z": 1}` |
| `set_field_of_view`                   | Parameter `field_of_view` now has a default value: `35`      |
| `apply_force_to_avatar`               | Parameter `direction` now has a default value: `{"x": 0, "y": 0, "z": 1}` |
| `apply_force_to_object`               | Parameter `force` now has a default value: `{"x": 0, "y": 0, "z": 1}` |
| `scale_object`                        | Parameter `scale_factor` now has a default value: `{"x": 1, "y": 1, "z": 1}` |
| `set_object_collision_detection_mode` | Parameter `mode` now has a default value: `"continuous_speculative"`. |
| `send_collisions`                     | Default values for `stay` and `exit` are `False` (both were `True`) |
| `bake_nav_mesh` | Replaced parameters `carve` and `carve_only_stationary` with new parameter `carve_type`. |

#### Removed Commands

| Command                       | Reason                                                       |
| ----------------------------- | ------------------------------------------------------------ |
| `set_day_night`               | This command enabled/disabled all lights in the scene; HDRI skyboxes can be used for *far* better results. |
| `set_material_from_resources` | Only usable in forked versions of TDWBase with extra materials in Resources/. Functionality can be replicated with local material asset bundles. |
| `set_semantic_material`       | Always sets the material as `"undefined"` (because visual materials are, as yet, unclassified). Note: `set_semantic_material_to` is still in the Command API. |
| `update_flex_container`       | Deprecated in v1.5                                           |
| `set_gravity` | Doesn't work as advertised (it makes objects kinematic too).<br>Functionality overlaps with `set_kinematic_state`, `simulate_physics`, and `set_gravity_vector`. |
| `set_shadows` | Functionality can be replicated via: `{"$type": "set_render_quality", "render_quality": 0}`<br>Note: `set_shadow_strength`, a different command, hasn't been removed. |

### Asset Bundle Libraries

- **Updated asset bundle URLs for every asset bundle.** The URLs now point towards binaries stored in the `tdw-public` and `tdw-private` S3 buckets.

#### Models

##### `models_full.json`

- **All models in `models_full.json` that are not also in `models_core.json` ("non-free models") now require S3 access keys in order to download.**

### Python

- Set default `--library` value in `multi_env.py` to `models_full.json` (was `models_core.json`)
- Slight efficiency improvements in `single_object.py`

### Docker

- Updated Docker file, bash scripts, controller, and documentation for v1.6
- Docker file always downloads the latest TDW release.

### Documentation

#### New Documentation

| Document      | Description                                        |
| ------------- | -------------------------------------------------- |
| `releases.md` | Overview of how TDW releases and versioning works. |

#### Modified Documentation

| Document | Modification |
| -------- | ------------ |
| `command_api.md` | _Many_ adjustments to the command descriptions, such as removing obsolete or misleading info, links to other docs, and minor clarifications.<br>Added a reference for all Asset Bundle Commands to their associated wrapper functions (e.g. `add_object` -> `Controller.get_add_object`).<br>Added a note for how to format the URL of a local asset bundle.<br>Clarified which "destroy" commands (e.g. `destroy_object`) retain the cached asset bundle in memory.<br>Grouped humanoid commands into a "Humanoid Command" section.<br>Converted many references to other documents into URLs. |
| `README.md` | Removed links to backend documentation. |
| `getting_started.md` | Updated for `v1.6.0` |
| `command_api_guide.md` | Added a few more examples.<br>Added a section explaining default parameter values. |
| `models_full.md` | Added optional instruction to run the screenshotter. |
| `doc_gen.md` | Extensive rewrite based on the new functionality. |
| `machine_performance.md` | Removed links to TDWBase Issues. |
| `flex.md` | Removed links to TDWBase Issues. |
| `impact_sounds.md` | Fixed a bad link. |
| `shapenet.md` | Fixed a bad link. |
| `video.md` | Fixed a bad link. |

#### Removed Documentation

- Removed all backend documentation from this repo.
