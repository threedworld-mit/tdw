# CHANGELOG

# v1.7.x

To upgrade from TDW v1.6 to v1.7, read [this guide](Documentation/v1.6_to_v1.7).

## v1.7.8

### Build

- Fixed: Output from the NavMeshAvatar isn't synced with TDW's simulation steps.

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
