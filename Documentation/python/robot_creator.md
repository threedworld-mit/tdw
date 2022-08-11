# RobotCreator

`from tdw.robot_creator import RobotCreator`

Download a .urdf or .xacro file and convert it into an asset bundle that is usable by TDW.

***

## Class Variables

| Variable | Type | Description | Value |
| --- | --- | --- | --- |
| `TEMP_ROOT` | Path | The root temporary directory. | `Path.home().joinpath("robot_creator/temp_robots")` |
| `UNITY_VERSION` | str | Use this version of Unity Editor to launch the asset bundle creator. | `"2020.3"` |

***

## Functions

#### \_\_init\_\_

**`RobotCreator()`**

**`RobotCreator(quiet=False, display="0", unity_editor_path=None)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| quiet |  bool  | False | If true, don't print any messages to console. |
| display |  str  | "0" | The display to launch Unity Editor on. Ignored if this isn't Linux. |
| unity_editor_path |  Union[Path, str] | None | The path to the Unity Editor executable, for example `C:/Program Files/Unity/Hub/Editor/2020.3.24f1/Editor/Unity.exe`. If None, this script will try to find Unity Editor automatically. |

#### get_base_unity_call

**`self.get_base_unity_call()`**

_Returns:_  The call to launch Unity Editor silently in batchmode, execute something, and then quit.

#### get_unity_project

**`self.get_unity_project()`**

Build the asset_bundle_creator Unity project.

_Returns:_  The path to the asset_bundle_creator Unity project.

#### get_project_path

**`RobotCreator.get_project_path()`**

_(Static)_

_Returns:_  The expected path of the Unity project.

#### create_asset_bundles

**`self.create_asset_bundles(urdf_url)`**

**`self.create_asset_bundles(urdf_url, required_repo_urls=None, xacro_args=None, immovable=True, up="y", description_infix=None, branch=None)`**

Given the URL of a .urdf file or a .xacro file, create asset bundles of the robot.

This is a wrapper function for:

1. `clone_repo()`
2. `copy_files()`
3. `urdf_to_prefab()`
4. `prefab_to_asset_bundles()`


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| urdf_url |  str |  | The URL of a .urdf or a .xacro file. |
| required_repo_urls |  Dict[str, str] | None | A dictionary of description folder names and repo URLs outside of the robot's repo that are required to create the robot. This is only required for .xacro files that reference outside repos. For example, the Sawyer robot requires this to add the gripper: `{"intera_tools_description": "https://github.com/RethinkRobotics/intera_common"}` |
| xacro_args |  Dict[str, str] | None | Names and values for the `arg` tags in the .xacro file (ignored if this is a .urdf file). For example, the Sawyer robot requires this to add the gripper: `{"electric_gripper": "true"}` |
| immovable |  bool  | True | If True, the base of the robot is immovable. |
| up |  str  | "y" | The up direction. Used when importing the robot into Unity. Options: `"y"` or `"z"`. Usually, this should be the default value (`"y"`). |
| description_infix |  str  | None | The name of the description infix within the .urdf URL, such as `fetch_description`. Only set this if the urdf URL is non-standard; otherwise `RobotCreator` should be able to find this automatically. |
| branch |  str  | None | The name of the branch of the repo. If None, defaults to `"master"`. |

_Returns:_  A `RobotRecord` object. The `urls` field contains the paths to each asset bundle.

#### get_record

**`RobotCreator.get_record(name, urdf_url, immovable, asset_bundles)`**

_(Static)_


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| name |  str |  | The name of the robot. |
| urdf_url |  str |  | The URL to the .urdf or .xacro file. |
| immovable |  bool |  | If True, the base of the robot is immovable. |
| asset_bundles |  Dict[str, str] |  | The paths to the asset bundles. See `prefab_to_asset_bundles()`. |

_Returns:_  A `RobotRecord` metadata object.

#### clone_repo

**`self.clone_repo(url)`**

Clone a repo to a temporary directory.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| url |  str |  | The URL to the .urdf or .xacro file or the repo. |

_Returns:_  The temporary directory.

#### copy_files

**`self.copy_files(urdf_url, local_repo_path, repo_paths)`**

**`self.copy_files(urdf_url, local_repo_path, repo_paths, xacro_args=None, branch=None)`**

Copy and convert files required to create a prefab.

1. If this is a .xacro file, convert it to a .urdf file.
2. Copy the .urdf file to the Unity project.
3. Copy all associated meshes to the .urdf project.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| urdf_url |  str |  | The URL to the remote .urdf or .xacro file. |
| local_repo_path |  Path |  | The path to the local repo. |
| repo_paths |  Dict[str, Path] |  | A dictionary of required repos (including the one that the .urdf or .xacro is in). Key = The description path infix, e.g. "sawyer_description". Value = The path to the local repo. |
| xacro_args |  Dict[str, str] | None | Names and values for the `arg` tags in the .xacro file. Can be None for a .urdf or .xacro file and always ignored for a .urdf file. |
| branch |  str  | None | The name of the branch of the repo. If None, defaults to `"master"`. |

_Returns:_  The path to the .urdf file in the Unity project.

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

**`self.urdf_to_prefab(urdf_path)`**

**`self.urdf_to_prefab(urdf_path, immovable=True, up="y")`**

Convert a .urdf file to Unity prefab.

The .urdf file must already exist on this machine and its meshes must be at the expected locations.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| urdf_path |  Path |  | The path to the .urdf file. |
| immovable |  bool  | True | If True, the base of the robot will be immovable by default (see the `set_immovable` command). |
| up |  str  | "y" | The up direction. Used for importing the .urdf into Unity. Options: "y" or "z". |

_Returns:_  The path to the .prefab file.

#### prefab_to_asset_bundles

**`self.prefab_to_asset_bundles(name)`**

Create asset bundles from a prefab.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| name |  str |  | The name of the robot (minus the .prefab extension). |

_Returns:_  A dictionary. Key = The system platform. Value = The path to the asset bundle as a Path object.