# CHANGELOG

# v1.6.x

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