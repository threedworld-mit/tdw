##### Robots

# Add your own robots to TDW

It is possible to add your own robots into TDW from a .urdf or .xacro file. However, the robot must first be converted into an asset bundle (just like [objects](../custom_models/custom_models.md)). To do so, you'll need to use TDW's [`RobotCreator`](../../python/asset_bundle_creator/robot_creator.md).

The `RobotCreator` can download a .urdf or .xacro file plus all relevant textures, meshes, etc. or it can use local files.

## Requirements

- Windows 10, OS X, or Linux
- (Windows only) Visual C++ 2012 Redistributable
- The `tdw` module
- Python 3.6+
- Unity Hub
- Unity Editor 2020.3.24f1
  - Build options must enabled for Windows, OS X, and Linux (these can  be set when installing Unity).
  - Ideally, Unity Editor should be installed via Unity Hub; otherwise, you'll need to set the `unity_editor_path` parameter in the `RobotCreator` constructor (see below).

- git

### ROS and .xacro file requirements

If you want to use a .xacro file, `RobotCreator` can convert it to a usable .urdf file, provided that you first install ROS. If you already have a .urdf file, you don't need to install ROS.

[This is the source of the installation instructions listed below.](http://wiki.ros.org/Installation/Ubuntu)

**On Linux:**

- `sudo apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654`
- `curl -sSL 'http://keyserver.ubuntu.com/pks/lookup?op=get&search=0xC1CF6E31E6BADE8868B172B4F42ED6FBAB17C654' | sudo apt-key add -`
- `sudo ros-melodic-ros-base`
- `sudo apt-get install rosbash`
- `sudo apt-get install ros-melodic-xacro`

**On Windows:**

- Install Ubuntu 18 on WSL 2
- `wsl sudo apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654`
- `wsl curl -sSL 'http://keyserver.ubuntu.com/pks/lookup?op=get&search=0xC1CF6E31E6BADE8868B172B4F42ED6FBAB17C654' | sudo apt-key add -`
- `wsl sudo ros-melodic-ros-base`
- `wsl sudo apt-get install rosbash`
- `wsl sudo apt-get install ros-melodic-xacro`

**On OS X:**

ROS isn't well-supported on OS X. You can try following installation instructions [here](http://wiki.ros.org/Installation/).

## The Asset Bundle Creator Unity project

To convert robot .urdf files and their referenced meshes into asset bundles, TDW uses [Asset Bundle Creator](https://github.com/alters-mit/asset_bundle_creator), a Unity Editor project. It is possible to run the Unity project without any Python wrapper classes but there is usually no reason to do so.

Asset Bundle Creator can be used not just for models, but for other types of asset bundles as well, such as [models](../custom_models/custom_models.md).

Asset Bundle Creator will be  downloaded automatically the first time you use the Python wrapper class (see below).

## Usage

To create an asset bundle of the UR5 robot:

```python
from tdw.asset_bundle_creator.robot_creator import RobotCreator
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("ur5_asset_bundles")
print(f"Asset bundles will be saved to: {output_directory}")
r = RobotCreator()
url = "https://github.com/ros-industrial/robot_movement_interface/blob/master/dependencies/ur_description/urdf/ur5_robot.urdf"
r.source_url_to_asset_bundles(url=url, output_directory=output_directory)
```

Output:

```
~/tdw_example_controller_output/ur5_asset_bundles/
....Darwin/
........ur5
....Linux/
........ur5
....Windows/
........ur5
....record.json
....log.txt
```

- `Darwin/ur5`, `Linux/ur5`, and `Windows/ur5` are platform-specific asset bundles.
- `record.json` is a serialized RobotRecord.
- `log.txt` is a log of the creation process.

There are optional parameters for setting the semantic category of the model, for controlling whether the root object is immovable. [Read the API document for more information.](../../python/asset_bundle_creator/robot_creator.md)

## Constructor parameters

`RobotCreator` has several optional constructor parameters:

#### 1. `quiet`

If True, suppress output messages.

#### 2. `unity_editor_path`

If you installed Unity Editor via Unity Hub, `RobotCreator` should be able to automatically find the Unity Editor executable.

If the Unity Editor executable is in an unexpected location, you will need to explicitly set its location in the `RobotCreator` by setting the optional `unity_editor_path` parameter:

```python
from tdw.asset_bundle_creator.robot_creator import RobotCreator

a = RobotCreator(quiet=True, unity_editor_path="D:/Unity/2020.3.24f1/Editor/Unity.exe")
```

#### 3. `check_version`

When you create a new `RobotCreator` Python object, it automatically compares the version of your local Unity project to the one stored on GitHub. This requires an Internet connection and might not be desirable in all cases, especially on servers. To prevent the version check, set `check_version=False` in the constructor.

#### 4. `display`

This must be set on Linux machines, especially headless servers, and must match a valid X display.

## Download remote repo

`source_url_to_asset_bundles()` automatically clones a repo and finds the local .urdf file. You can do these steps manually as well.

To clone a repo, call `clone_repo()`. Note that the URL is of the source URDF file, not the repo URL:

```python
from tdw.asset_bundle_creator.robot_creator import RobotCreator

r = RobotCreator()
url = "https://github.com/ros-industrial/robot_movement_interface/blob/master/dependencies/ur_description/urdf/ur5_robot.urdf"
repo_path = r.clone_repo(url=url)
```

Having cloned the repo, you can find the .urdf file via `get_urdf_path_from_local_repo()`:

```python
from tdw.asset_bundle_creator.robot_creator import RobotCreator

r = RobotCreator()
url = "https://github.com/ros-industrial/robot_movement_interface/blob/master/dependencies/ur_description/urdf/ur5_robot.urdf"
repo_path = r.clone_repo(url=url)
urdf_path = r.get_urdf_path_from_local_repo(url=url, local_repo_path=repo_path)
```

## Create asset bundles from a local .urdf file

Having downloaded or created a local .urdf file, you can call `source_file_to_asset_bundles()` to generate asset bundles.

## Create a prefab

When creating asset bundles, `RobotCreator`  needs to first create a Unity prefab, and then it can generate asset bundles of the prefab.

In many cases, a fully automated robot creation process will be faulty; you may need to adjust parameters for joints, or remove some redundant joints, and so on. It's usually worth creating, testing, and editing a prefab before finalizing the asset bundle. To create a prefab, call `urdf_to_prefab()`:

```python
from tdw.asset_bundle_creator.robot_creator import RobotCreator
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("ur5_asset_bundles")
print(f"Asset bundles will be saved to: {output_directory}")
r = RobotCreator()
url = "https://github.com/ros-industrial/robot_movement_interface/blob/master/dependencies/ur_description/urdf/ur5_robot.urdf"
repo_path = r.clone_repo(url=url)
urdf_path = r.get_urdf_path_from_local_repo(url=url, local_repo_path=repo_path)
r.urdf_to_prefab(urdf_path=urdf_path, output_directory=output_directory)
```

##### Common problems and solutions during prefab creation

| Problem | Solution |
| --- | --- |
| Prefab creation seems to hang. | This is because sometimes the physics hull collider meshes are very complicated and require more time to generate. Let the process run. |
| Got an error during prefab creation: `Root object of the robot doesn't have an ArticulationBody.` | Open the project, double-click the prefab, and add an ArticulationBody to the root object. Adjust the parenting hierarchy of the robot such that the ArticulationBodies beneath the root are direct children. This is bad: `root -> non-articulation -> articulation` and this is good: `root -> articulation` |

##### Common problems and solutions while testing a prefab in the Unity Editor project

| Problem | Solution |
| --- | --- |
| Arms are flailing. | Usually this is because the colliders are parented to the wrong object. Double-click the prefab and make sure each `Collisions` object is parented to the matching ArticulationBody object. |
| Robot falls apart and there are `AABB` errors | You have too many ArticulationBodies. Unity supports a maximum of 65 (1 parent, 64 children). Double-click the prefab and delete any redundant ArticulationBodies. |
| The base of the robot is below (0, 0, 0) | Double-click the prefab and adjust the y position of the child objects. |
| Joints snap to a weird angle. | Usually this is because there are overlapping physics colliders. Double-click the prefab and in the Hierarchy panel click the root object. The green wireframe meshes in the Scene View are the physics colliders. Try deleting or disabling colliders near the glitching joint. |
| The robot tips over. | Set `immovable=True` in your Python script. If that doesn't work, double-click the prefab. In the Hierarchy panel, click the ArticulationBody that you think is causing the robot to tilt. In the Inspector panel, click "Add Component". Add: `Center Of Mass`. Adjust the center of mass in the Inspector until the robot stops tipping. |

## Create asset bundles from a prefab

Having adjusted a prefab as needed, you can then convert it into asset bundles by calling `prefab_to_asset_bundles()`:

```python
from tdw.robot_creator import RobotCreator
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("ur5_asset_bundles")
print(f"Asset bundles will be saved to: {output_directory}")
r = RobotCreator()
r.prefab_to_asset_bundles(name="ur5", output_directory=output_directory)
```

## Create a record

`source_url_to_asset_bundles()` and `source_file_to_asset_bundles()` automatically create a new record.json file.

If you've called `source_file_to_prefab()` followed by `prefab_to_asset_bundles()`, you can create a record via `create_record()`:

```python
from json import loads
from tdw.asset_bundle_creator.robot_creator import RobotCreator
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from tdw.librarian import RobotRecord

output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("ur5_example")
a = RobotCreator()
a.create_record(name="ur5",
                output_directory=output_directory)
# Get the expected record path.
record_path = output_directory.joinpath("record.json")
# Load the record data.
record_data = loads(record_path.read_text())
# Load the record.
record = RobotRecord(record_data)
```

There are other optional parameters. [Read the API document for more information.](../../python/asset_bundle_creator/robot_creator.md)

## Create a custom robot library

If you want to create many asset bundles, it's usually convenient to create your own `RobotLibrarian` and store it as a local json file. This `RobotLibrarian` can contain any records including those of robots from other libraries.

To do this, set the `library_path` and, optionally, `library_description` parameters in either  `source_url_to_asset_bundles()`, `source_file_to_asset_bundles()` or `create_record()`:

```python
from pathlib import Path
from tdw.asset_bundle_creator.robot_creator import RobotCreator
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("robots")
print(f"Asset bundles will be saved to: {output_directory}")
RobotCreator().source_file_to_asset_bundles(source_file=Path("ur5.urdf").resolve(),
                                            output_directory=output_directory.joinpath("ur5"),
                                            library_path=output_directory.joinpath("library.json"),
                                            library_description="My custom library")
```

Output:

```
~/tdw_example_controller_output/robots/
....ur5/
........Darwin/
............ur5
........Linux/
............ur5
........Windows/
............ur5
........record.json
........log.txt
....library.json
```

Note that we set `output_directory` to be a subdirectory ending in `cube/`. This is because we might want to create multiple asset bundles and store all of their metadata in a shared `library.json` file.

You can load the custom library by setting the `library` parameter in RobotLibrarian:

```python
from tdw.backend.paths RobotLibrarian EXAMPLE_CONTROLLER_OUTPUT_PATH
from tdw.librarian import ModelLibrarian

output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("robots")
librarian = RobotLibrarian(library=str(output_directory.joinpath("library.json").resolve()))
```

## Cleanup

Call `cleanup()` to delete any intermediary mesh files and prefabs within the Unity Editor project created in the process of creating asset bundles. This will delete *all* intermediary files, including those of other models. This won't delete any of your original files (assuming that they weren't in the Unity Editor project).

## Convert a .xacro file

If you're using a .xacro file, it must be converted to a .urdf file. Call `xacro_to_urdf()`.

[Read the API document for more information.](../../python/asset_bundle_creator/robot_creator.md)

## "Fix" a .urdf file

In some cases, a .urdf file won't be useable as-is. This can happen if it has an unusual XML namespace convention, if it has too many joints, etc.

You can create a new, simplified, file via `fix_urdf()`:

```python
from pathlib import Path
from tdw.asset_bundle_creator.robot_creator import RobotCreator

urdf_path = Path.home().joinpath("robots/pr2/pr2.urdf")
urdf_path = RobotCreator.fix_urdf(urdf_path=urdf_path,
                                  link_name_excludes_regex=["_gazebo_", "_cam_", "world_link", "imu_link",
                                                            "sensor_mount_link", "head_plate_frame",
                                                            "_gripper_motor_accelerometer_link"],
                                  link_exclude_types=["camera", "laser"])
```

This will do the following:

- Simplify the XML namespaces.
- Remove all `<gazebo>` elements.
- Remove all links that have regular expression matches to any string in `link_name_exludes_regex`.
- Remove all links that have a `type` attribute, and if the `type` matches any string in `link_exclude_types`.

## Low-level functions

`get_base_unity_call()` returns a list of strings that can be used to call a Unity Editor function:

```python
from tdw.asset_bundle_creator.model_creator import ModelCreator

print(ModelCreator().get_base_unity_call())
```

Output:

```
['C:/Program Files/Unity/Hub/Editor/2020.3.24f1/Editor/Unity.exe', '-projectpath', 'C:/Users/USER Alter/asset_bundle_creator', '-quit', '-batchmode']
```

`call_unity()` will call the Asset Bundle Creator Unity project as a subprocess with command-line arguments. You can call arbitrary methods this way (assuming you know the [underlying C# API](https://github.com/alters-mit/asset_bundle_creator). This function is used by every function that communicates with Unity, for example `source_file_to_asset_bundles()`.

## Add a custom robot to a TDW simulation

To add the robot to a TDW scene, use a `Robot` add-on but set the `source` parameter to your custom `RobotLibrarian`:

```python
from pathlib import Path
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.librarian import RobotLibrarian
from tdw.add_ons.robot import Robot

lib_path = "my_robot_librarian.json"
# Create your robot library if it doesn't already exist.
if not Path(lib_path).exists():
    RobotLibrarian.create_library(path=lib_path, description="Custom Robot Librarian")
# Load your robot library.
lib = RobotLibrarian(lib_path)

robot_id = 0
robot = Robot(name="ur5",
              source=lib,
              robot_id=robot_id)
c = Controller()
c.add_ons.append(robot)
c.communicate(TDWUtils.create_empty_room(12, 12))
```

***

**Next: [Robotics API (low-level)](low_level_api.md)**

[Return to the README](../../../README.md)

***

Python API:

- [`RobotCreator`](../../python/asset_bundle_creator/robot_creator.md)
- [`RobotLibrarian`](../../python/librarian/robot_librarian.md)