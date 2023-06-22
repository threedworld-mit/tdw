# RobotCreator

`from tdw.asset_bundle_creator.robot_creator import RobotCreator`

Download a .urdf or .xacro file and convert it into an asset bundle that is usable by TDW.

***

## Fields

- `quiet` If True, don't print any messages to console.

***

## Class Variables

| Variable | Type | Description | Value |
| --- | --- | --- | --- |
| `PROJECT_PATH` | Path | The path to the `asset_bundle_creator` Unity project. | `Path.home().joinpath("asset_bundle_creator")` |
| `TEMP_ROOT` | Path | The root temporary directory. | `AssetBundleCreator.PROJECT_PATH.joinpath("temp_robots")` |
| `UNITY_VERSION` | str | Use this version of Unity Editor to launch the asset bundle creator. | `"2020.3"` |

***

## Functions

#### \_\_init\_\_

\_\_init\_\_

**`RobotCreator()`**

**`RobotCreator(quiet=False, display="0", unity_editor_path=None, check_version=True)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| quiet |  bool  | False | If True, don't print any messages to console. |
| display |  str  | "0" | The display to launch Unity Editor on. Ignored if this isn't Linux. |
| unity_editor_path |  Union[Path, str] | None | The path to the Unity Editor executable, for example `C:/Program Files/Unity/Hub/Editor/2020.3.24f1/Editor/Unity.exe`. If None, this script will try to find Unity Editor automatically. |
| check_version |  bool  | True | If True, check if there is an update to the Unity Editor project. |

#### get_base_unity_call

**`self.get_base_unity_call()`**

_Returns:_  The call to launch Unity Editor silently in batchmode, execute something, and then quit.

#### call_unity

**`self.call_unity(method, args, log_path)`**

**`self.call_unity(method, args, log_path, class_name=None)`**

Execute a call to Unity Editor. If `self.quiet == False` this will continuously print the log file.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| method |  str |  | The name of the method. |
| args |  List[str] |  | Arguments to send to Unity Editor in addition to those send via `self.get_base_unity_call()` and `-executeMethod`. |
| log_path |  Union[str, Path] |  | The path to the log file as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). |
| class_name |  str  | None | The name of the Unity C# class. If None, a default class name will be used. See: `self.get_creator_class_name()`. |

#### prefab_to_asset_bundles

**`self.prefab_to_asset_bundles(name, output_directory)`**

Build asset bundles from a .prefab file. This is useful when you want to edit the .prefab file by hand, e.g.:

1. `self.source_file_to_prefab()`
2. Edit .prefab file
3. `self.prefab_to_asset_bundles()`

Example source:

```
~/asset_bundle_creator/
....Assets/
........prefabs/
............name.prefab
........source_files/
............name/
................name.obj
................Materials/
```

Example output:

```
output_directory/
....Darwin/
........name
....Linux/
........name
....Windows/
........name
....log.txt
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| name |  str |  | The name of the model (the name of the .prefab file, minus the extension). |
| output_directory |  Union[str, Path] |  | The root output directory as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If this directory doesn't exist, it will be created. |

#### cleanup

**`self.cleanup()`**

Delete any intermediary files in the `asset_bundle_creator` Unity Editor project such as .prefab files.

#### asset_bundles_exist

**`AssetBundleCreator.asset_bundles_exist(name, directory)`**

_(Static)_

Check whether asset bundles exist for all platforms in the source directory.

Expected directory structure:

```
directory/
....Darwin/
........name
....Linux/
........name
....Windows/
........name
```

...where `name` is an asset bundle file.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| name |  str |  | The name of the asset bundle. |
| directory |  Union[str, Path] |  | The source directory as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). |

_Returns:_  True if asset bundles exist for all platforms in the source directory.

#### get_creator_class_name

**`self.get_creator_class_name()`**

_Returns:_  The name of the Unity C# class, e.g. `ModelCreator`.

#### source_url_to_asset_bundles

**`self.source_url_to_asset_bundles(url, output_directory)`**

**`self.source_url_to_asset_bundles(url, output_directory, required_repo_urls=None, xacro_args=None, immovable=True, description_infix=None, branch=None, library_path=None, library_description=None, source_description=None)`**

Given the URL of a .urdf file or a .xacro file, create asset bundles of the robot.

This is a wrapper function for:

1. `self.clone_repo()`
2. `self.xacro_to_urdf()` (if applicable)
3. `self.urdf_to_prefab()`
4. `self.prefab_to_asset_bundles()`
5. `self.create_record()`

Example `urdf_url`:

```
https://github.com/ros-industrial/robot_movement_interface/blob/master/dependencies/ur_description/urdf/ur5_robot.urdf
```

Example `output_directory`:

```
output_directory/
....Darwin/
........robot
....Linux/
........robot
....Windows/
........robot
....log.txt
....record.json
....model.json
....library.json
```

- `Darwin/robot`, `Linux/robot` and `Windows/robot` are the platform-specific asset bundles.
- `log.txt` is a log from the `asset_bundle_creator` Unity Editor project.
- `record.json` is a serialized `RobotRecord`.
- `model.json` is a JSON dump of the converted .urdf file and mesh paths.
- `library.json` is a serialized `RobotLibrarian`. It will only be added/set if the optional `library_path` is set.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| url |  str |  | The URL of a .urdf or a .xacro file. |
| output_directory |  Union[str, Path] |  | The root output directory as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If this directory doesn't exist, it will be created. |
| required_repo_urls |  Dict[str, str] | None | A dictionary of description folder names and repo URLs outside of the robot's repo that are required to create the robot. This is only required for .xacro files that reference outside repos. For example, the Sawyer robot requires this to add the gripper: `{"intera_tools_description": "https://github.com/RethinkRobotics/intera_common"}` |
| xacro_args |  Dict[str, str] | None | Names and values for the `arg` tags in the .xacro file (ignored if this is a .urdf file). For example, the Sawyer robot requires this to add the gripper: `{"electric_gripper": "true"}` |
| immovable |  bool  | True | If True, the base of the robot is immovable. |
| description_infix |  str  | None | The name of the description infix within the .urdf URL, such as `fetch_description`. Only set this if the urdf URL is non-standard; otherwise `RobotCreator` should be able to find this automatically. |
| branch |  str  | None | The name of the branch of the repo. If None, defaults to `"master"`. |
| library_path |  Union[str, Path] | None | If not None, this is a path as a string or [`Path`](https://docs.python.org/3/library/pathlib.html) to a new or existing `RobotLibrarian` .json file. The record will be added to this file in addition to being saved to `record.json`. |
| library_description |  str  | None | A description of the library. Ignored if `library_path` is None. |
| source_description |  str  | None | A description of the source of the .urdf file, for example the repo URL. |

#### source_file_to_asset_bundles

**`self.source_file_to_asset_bundles(source_file, output_directory)`**

**`self.source_file_to_asset_bundles(source_file, output_directory, immovable=True, library_path=None, library_description=None, source_description=None)`**

Given a .urdf file plus its meshes, create asset bundles of the robot.

This is a wrapper function for:

1. `self.urdf_to_prefab()`
2. `self.prefab_to_asset_bundles()`
3. `self.create_record()`

Example source directory:

```
ur_description/
....urdf/
........ur5_robot.urdf
....meshes/
........ur5/
............visual/
................Base.dae
................Forearm.dae
................Shoulder.dae
................UpperArm.dae
................Wrist1.dae
................Wrist2.dae
................Wrist3.dae
```

- The directory structure must match that of the [source repo](https://github.com/ros-industrial/robot_movement_interface).
- Collision meshes are ignored; they will be generated when creating the prefab.

Example `output_directory`:

```
output_directory/
....Darwin/
........robot
....Linux/
........robot
....Windows/
........robot
....log.txt
....record.json
....model.json
....library.json
```

- `Darwin/robot`, `Linux/robot` and `Windows/robot` are the platform-specific asset bundles.
- `log.txt` is a log from the `asset_bundle_creator` Unity Editor project.
- `record.json` is a serialized `RobotRecord`.
- `model.json` is a JSON dump of the converted .urdf file and mesh paths.
- `library.json` is a serialized `RobotLibrarian`. It will only be added/set if the optional `library_path` is set.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| source_file |  Union[str, Path] |  | The path to the source .fbx or .obj file as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). |
| output_directory |  Union[str, Path] |  | The root output directory as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If this directory doesn't exist, it will be created. |
| immovable |  bool  | True | If True, the base of the robot is immovable. |
| library_path |  Union[str, Path] | None | If not None, this is a path as a string or [`Path`](https://docs.python.org/3/library/pathlib.html) to a new or existing `RobotLibrarian` .json file. The record will be added to this file in addition to being saved to `record.json`. |
| library_description |  str  | None | A description of the library. Ignored if `library_path` is None. |
| source_description |  str  | None | A description of the source of the .urdf file, for example the repo URL. |

#### clone_repo

**`self.clone_repo(url)`**

**`self.clone_repo(url, branch=None)`**

Clone a repo to a temporary directory.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| url |  str |  | The URL to the .urdf or .xacro file or the repo. |
| branch |  str  | None | The name of the branch of the repo. If None, defaults to `"master"`. |

_Returns:_  The temporary directory.

#### get_urdf_path_from_local_repo

**`self.get_urdf_path_from_local_repo(url, local_repo_path)`**

**`self.get_urdf_path_from_local_repo(url, local_repo_path, branch=None)`**


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| url |  str |  | The URL to a .urdf file. |
| local_repo_path |  Path |  | The path to a local repo. |
| branch |  str  | None | The branch. If None, defaults to `"master"`. |

_Returns:_  The path to the local .urdf file.

#### xacro_to_urdf

**`self.xacro_to_urdf(xacro_path, repo_paths)`**

**`self.xacro_to_urdf(xacro_path, args=None, repo_paths)`**

Convert a local .xacro file to a .urdf file.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| xacro_path |  Path |  | The path to the local .xacro file. |
| args |  Dict[str, str] | None | Names and values for the `arg` tags in the .xacro file. |
| repo_paths |  Dict[str, Path] |  | Local paths to all required repos. Key = The description infix. Value = The local repo path. |

_Returns:_  The path to the .urdf file.

#### urdf_to_prefab

**`self.urdf_to_prefab(urdf_path, output_directory)`**

**`self.urdf_to_prefab(urdf_path, output_directory, immovable=True)`**

Convert a .urdf file to Unity prefab.

The .urdf file must already exist on this machine and its meshes must be at the expected locations.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| urdf_path |  Union[str, Path] |  | The path to the .urdf file as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). |
| output_directory |  Union[str, Path] |  | The root output directory as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If this directory doesn't exist, it will be created. |
| immovable |  bool  | True | If True, the base of the robot will be immovable by default (see the `set_immovable` command). |

#### create_record

**`self.create_record(name, output_directory)`**

**`self.create_record(name, output_directory, library_path=None, library_description=None, source_description=None, immovable=True)`**

Create a model record and save it to disk. This requires asset bundles of the robot to already exist:

```
output_directory/
....Darwin/
........robot
....Linux/
........robot
....Windows/
........robot
....log.txt
```

Result:

```
output_directory/
....Darwin/
........robot
....Linux/
........robot
....Windows/
........robot
....record.json
....log.txt
library.json
```

- `record.json` is a serialized `RobotRecord`.
- `library.json` is a serialized `RobotLibrarian`. It will only be added/set if the optional `library_path` is set.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| name |  str |  | The name of the robot. |
| output_directory |  Union[str, Path] |  | The root output directory as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If this directory doesn't exist, it will be created. |
| library_path |  Union[str, Path] | None | If not None, this is a path as a string or [`Path`](https://docs.python.org/3/library/pathlib.html) to a new or existing `RobotLibrarian` .json file. The record will be added to this file in addition to being saved to `record.json`. |
| library_description |  str  | None | A description of the library. Ignored if `library_path` is None. |
| source_description |  str  | None | A description of the source of the .urdf file, for example the repo URL. |
| immovable |  bool  | True | If True, the base of the robot is immovable. |

#### get_name

**`RobotCreator.get_name(urdf_path)`**

_(Static)_


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| urdf_path |  Union[str, Path] |  | The path to the .urdf file as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). |

_Returns:_  The expected name of the robot.

#### fix_urdf

**`RobotCreator.fix_urdf(urdf_path)`**

**`RobotCreator.fix_urdf(urdf_path, remove_gazebo=True, simplify_namespaces=True, link_name_excludes_regex=None, link_exclude_types=None)`**

_(Static)_

"Fix" a .urdf file by removing extraneous information. This function will:

- Make the file easier to parse, for example by removing gazebo elements and simplifying XML namespaces.
- Remove unneeded links, for example laser or camera links.

This function won't alter the original .urdf file and will create a new .urdf file.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| urdf_path |  Union[str, Path] |  | The path to the .urdf file as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). |
| remove_gazebo |  bool  | True | If True, remove all `<gazebo>` elements. This should usually be True. |
| simplify_namespaces |  bool  | True | If True, simplify the XML namespaces. This should usually be True. |
| link_name_excludes_regex |  List[str] | None | A list of regular expressions to search for in links, for example `["_gazebo_"]`. Link names that match this will be removed. |
| link_exclude_types |  List[str] | None | Some links have a `type` attribute. Exclude links matching this types in this list, for example `["laser", "camera"]`. |

_Returns:_  The path to the "fixed" .urdf file.