# `robot_creator.py`

## `RobotCreator(AssetBundleCreatorBase)`

`from tdw.robot_creator import RobotCreator`

Download a .urdf or .xacro file and convert it into an asset bundle that is usable by TDW.

```python
from tdw.robot_creator import RobotCreator

r = RobotCreator()
record = r.create_asset_bundles(
    urdf_url="https://github.com/ros-industrial/robot_movement_interface/blob/master/dependencies/ur_description/urdf/ur5_robot.urdf",
    xacro_args=None,
    required_repo_urls=None,
    immovable=True,
    up="y")
print(record.name)
print(record.urls)
```

Note that most of the parameters are optional, so this can be simplified to:

```python
from tdw.robot_creator import RobotCreator

r = RobotCreator()
record = r.create_asset_bundles(urdf_url="https://github.com/ros-industrial/robot_movement_interface/blob/master/dependencies/ur_description/urdf/ur5_robot.urdf")
print(record.name)
print(record.urls)
```

***

# Functions

***

#### `__init__(self, quiet: bool = False, display: str = ":0")`


| Parameter | Description |
| --- | --- |
| quiet | If true, don't print any messages to console. |
| display | The display to launch Unity Editor on. Ignored if this isn't Linux. |

***

#### `create_asset_bundles(self, urdf_url: str, required_repo_urls: Dict[str, str] = None, xacro_args: Dict[str, str] = None, immovable: bool = True, up: str = "y") -> RobotRecord`

Given the URL of a .urdf file or a .xacro file, create asset bundles of the robot.
This is a wrapper function for:
1. `clone_repo()`
2. `copy_files()`
3. `urdf_to_prefab()`
4. `prefab_to_asset_bundles()`

| Parameter | Description |
| --- | --- |
| urdf_url | The URL of a .urdf or a .xacro file. |
| required_repo_urls | A dictionary of description folder names and repo URLs outside of the robot's repo that are required to create the robot. This is only required for .xacro files that reference outside repos. For example, the Sawyer robot requires this to add the gripper: `{"intera_tools_description": "https://github.com/RethinkRobotics/intera_common"}` |
| xacro_args | Names and values for the `arg` tags in the .xacro file (ignored if this is a .urdf file). For example, the Sawyer robot requires this to add the gripper: `{"electric_gripper": "true"}` |
| immovable | If True, the base of the robot is immovable. |
| up | The up direction. Used when importing the robot into Unity. Options: `"y"` or `"z"`. Usually, this should be the default value (`"y"`). |

_Returns:_  A `RobotRecord` object. The `urls` field contains the paths to each asset bundle.

***

#### `get_record(name: str, urdf_url: str, immovable: bool, asset_bundles: Dict[str, str]) -> RobotRecord`

_This is a static function._


| Parameter | Description |
| --- | --- |
| name | The name of the robot. |
| urdf_url | The URL to the .urdf or .xacro file. |
| immovable | If True, the base of the robot is immovable. |
| asset_bundles | The paths to the asset bundles. See `prefab_to_asset_bundles()`. |

_Returns:_  A `RobotRecord` metadata object.

***

#### `clone_repo(self, url: str) -> Path`

Clone a repo to a temporary directory.

| Parameter | Description |
| --- | --- |
| url | The URL to the .urdf or .xacro file or the repo. |

_Returns:_  The temporary directory.

***

#### `copy_files(self, urdf_url: str, local_repo_path: Path, repo_paths: Dict[str, Path], xacro_args: Dict[str, str] = None) -> Path`

Copy and convert files required to create a prefab.
1. If this is a .xacro file, convert it to a .urdf file.
2. Copy the .urdf file to the Unity project.
3. Copy all associated meshes to the .urdf project.

| Parameter | Description |
| --- | --- |
| urdf_url | The URL to the remote .urdf or .xacro file. |
| local_repo_path | The path to the local repo. |
| repo_paths | A dictionary of required repos (including the one that the .urdf or .xacro is in). Key = The description path infix, e.g. "sawyer_description". Value = The path to the local repo. |
| xacro_args | Names and values for the `arg` tags in the .xacro file. Can be None for a .urdf or .xacro file and always ignored for a .urdf file. |

_Returns:_  The path to the .urdf file in the Unity project.

***

#### `xacro_to_urdf(self, xacro_path: Path, repo_paths: Dict[str, Path], args: Dict[str, str] = None) -> Path`

Convert a local .xacro file to a .urdf file.

| Parameter | Description |
| --- | --- |
| xacro_path | The path to the local .xacro file. |
| args | Names and values for the `arg` tags in the .xacro file. |
| repo_paths | Local paths to all required repos. Key = The description infix. Value = The local repo path. |

_Returns:_  The path to the .urdf file.

***

#### `urdf_to_prefab(self, urdf_path: Path, immovable: bool = True, up: str = "y") -> Path`

Convert a .urdf file to Unity prefab.
The .urdf file must already exist on this machine and its meshes must be at the expected locations.

| Parameter | Description |
| --- | --- |
| urdf_path | The path to the .urdf file. |
| immovable | If True, the base of the robot will be immovable by default (see the `set_immovable` command). |
| up | The up direction. Used for importing the .urdf into Unity. Options: "y" or "z". |

_Returns:_  The path to the .prefab file.

***

#### `prefab_to_asset_bundles(self, name: str) -> Dict[str, Path]`

Create asset bundles from a prefab.

| Parameter | Description |
| --- | --- |
| name | The name of the robot (minus the .prefab extension). |

_Returns:_  A dictionary. Key = The system platform. Value = The path to the asset bundle as a Path object.

***

#### `get_unity_project(self) -> Path`

Build the asset_bundle_creator Unity project.

_Returns:_ The path to the asset_bundle_creator Unity project.

***

#### `get_project_path() -> Path`

_This is a static function._

_Returns:_  The expected path of the Unity project.

***

