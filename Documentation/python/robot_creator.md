# `robot_creator.py`

## `RobotCreator(AssetBundleCreatorBase)`

`from tdw.robot_creator import RobotCreator`

Download a .urdf or .xacro file and convert it into an asset bundle that is usable by TDW.

# Requirements

- Windows 10, OS X, or Linux
  - On a remote Linux server, you'll need a valid virtual display (see the `display` parameter of the constructor)
- Unity Editor 2020.2 (must be installed via Unity Editor)
- Python3 and the `tdw` module.

### ROS and .xacro file requirements

If you want to use a .xacro file, `RobotCreator` can convert it to a usable .urdf file, provided that you first install ROS.

On Linux:

- [Install ROS base](http://wiki.ros.org/Installation/Ubuntu) (Melodic version)
- `sudo apt-get install rosbash`
- `sudo apt-get install ros-melodic-xacro`

On Windows:

- Install Ubuntu 18 on WSL 2
- [Install ROS base on WSL 2](http://wiki.ros.org/Installation/Ubuntu) (Melodic version)
- `wsl sudo apt-get install rosbash`
- `wsl sudo apt-get install ros-melodic-xacro`

# Usage

To create an asset bundle of the UR5 robot:

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

The first time that this script is run, it will create a new `robot_creator` Unity project from a file in the `tdw` Python module. The original repo is [here](https://github.com/alters-mit/robot_creator).

### Edit the prefab

`RobotCreator.create_asset_bundles()` creates a .prefab file in the `robot_creator` Unity project. This is an intermediate file that is required for building the asset bundle.

It's usually worth testing and editing the prefab before finalizing the asset bundle. To do this, first run `RobotCreator` as described above, and then do the following:

1. Create a prefab of the robot.
2. Open robot_creator Unity project in Unity 2020.2; the project is located at `~/robot_creator` (where `~` is your home directory).
3. In the Unity Editor project window, double-click `Scenes -> SampleScene`
4. In the Unity Editor project window, search for the name of the robot. Click the file and drag it into the scene view.
5. Press play.


Common problems and solutions during prefab creation:

| Problem | Solution |
| --- | --- |
| Prefab creation seems to hang. | This is because sometimes the physics hull collider meshes are very complicated and require more time to generate. Let the process run. |
| Got an error during prefab creation: `Root object of the robot doesn't have an ArticulationBody.` | Open the project, double-click the prefab, and add an ArticulationBody to the root object. Adjust the parenting hierarchy of the robot such that the ArticulationBodies beneath the root are direct children. This is bad: `root -> non-articulation -> articulation` and this is good: `root -> articulation` |

Common problems and solutions while testing a prefab in the Unity Editor project:

| Problem | Solution |
| --- | --- |
| Arms are flailing. | Usually this is because the colliders are parented to the wrong object. Double-click the prefab and make sure each `Collisions` object is parented to the matching ArticulationBody object. |
| Robot falls apart and there are `AABB` errors | You have too many ArticulationBodies. Unity supports a maximum of 65 (1 parent, 64 children). Double-click the prefab and delete any redundant ArticulationBodies. |
| The base of the robot is below (0, 0, 0) | Double-click the prefab and adjust the y position of the child objects. |
| Joints snap to a weird angle. | Usually this is because there are overlapping physics colliders. Double-click the prefab and in the Hierarchy panel click the root object. The green wireframe meshes in the Scene View are the physics colliders. Try deleting or disabling colliders near the glitching joint. |
| The robot tips over. | Set `immovable=True` in `create_asset_bundles()`. If that doesn't work, double-click the prefab. In the Hierarchy panel, click the ArticulationBody that you think is causing the robot to tilt. In the Inspector panel, click "Add Component". Add: `Center Of Mass`. Adjust the center of mass in the Inspector until the robot stops tipping. |

### Create an asset bundle from a prefab

Once the robot prefab is working correctly, you can create asset bundles without overwriting the prefab:

```python
from tdw.robot_creator import RobotCreator

r = RobotCreator()
urdf_url = "https://github.com/ros-industrial/robot_movement_interface/blob/master/dependencies/ur_description/urdf/ur5_robot.urdf"
record = r.create_asset_bundles(urdf_url=urdf_url)
print(record.name)
print(record.urls)

asset_bundles = rc.prefab_to_asset_bundles(name=name)
record = RobotCreator.get_record(name=record.name, urdf_url=urdf_url, immovable=True, asset_bundles=asset_bundles)
```

### Store metadata

`RobotCreator.create_asset_bundles()` returns a `RobotRecord` metadata object, which contains the files paths to the asset bundle.
You can store a `RobotRecord` object in a `RobotLibrarian`, which is saved as a JSON file.

To create a `RobotLibrarian`:

```python
from tdw.librarian import RobotLibrarian

RobotLibrarian.create_library(path="my_robot_librarian.json", description="Custom Robot Librarian")
```

To create asset bundles and save the `RobotRecord` metadata:

```python
from tdw.robot_creator import RobotCreator
from tdw.librarian import RobotLibrarian

r = RobotCreator()

# Create the asset bundles and generate a metadata record.
record = r.create_asset_bundles(urdf_url="https://github.com/ros-industrial/robot_movement_interface/blob/master/dependencies/ur_description/urdf/ur5_robot.urdf")

# Add the record to the local library.
lib = RobotLibrarian("my_robot_librarian.json")
lib.add_or_update_record(record=record, overwrite=False, write=True)
```

### Load the robot into TDW

To add the robot to a TDW scene:

```python
from pathlib import Path
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.librarian import RobotLibrarian
from tdw.robot_creator import RobotCreator

lib_path = "my_robot_librarian.json"
# Create your robot library if it doesn't already exist.
if not Path(lib_path).exists():
    RobotLibrarian.create_library(path=lib_path, description="Custom Robot Librarian")
# Load your robot library.
lib = RobotLibrarian(lib_path)

robot_name = "ur5"
# If there isn't a metadata record yet for this robot, create asset bundles and add the record.
if lib.get_record(robot_name) is None:
    r = RobotCreator()
    record = r.create_asset_bundles(urdf_url="https://github.com/ros-industrial/robot_movement_interface/blob/master/dependencies/ur_description/urdf/ur5_robot.urdf")
    # Add the record if it doesn't already exist.
    lib.add_or_update_record(record=record, overwrite=False, write=True)

# Launch the controller.
c = Controller(launch_build=False)
c.start()
robot_id = 0
commands = [TDWUtils.create_empty_room(12, 12),
            c.get_add_robot(name=robot_name, robot_id=robot_id, library=lib_path)]
commands.extend(TDWUtils.create_avatar(look_at=TDWUtils.VECTOR3_ZERO, position={"x": -0.881, "y": 0.836, "z": -1.396}))
c.communicate(commands)
```

For a more complete example of how to use the robot in TDW (i.e. find all of its joints and set target angles or positions), see: `twd/Python/example_controllers/robot_arm.py` Note that in this example, there isn't any code to build the asset bundles or update the metadata. This is because UR5 is already in the default TDW robot library (on our remote S3 server) and the metadata record is already stored in the default metadata librarian.

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

#### `import_unity_package(self, unity_project_path: Path) -> None`

Import the .unitypackage file into the Unity project. Add the .urdf importer package.

| Parameter | Description |
| --- | --- |
| unity_project_path | The path to the Unity project. |

***

#### `get_unity_package() -> str`

_This is a static function._

_Returns:_  The name of the .unitypackage file.

***

#### `get_project_path() -> Path`

_This is a static function._

_Returns:_  The expected path of the Unity project.

***

