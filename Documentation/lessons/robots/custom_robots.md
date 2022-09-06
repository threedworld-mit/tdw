##### Robots

# Add your own robots to TDW

It is possible to add your own robots into TDW from a .urdf or .xacro file. However, the robot must first be converted into an asset bundle (just like [objects](../3d_models/custom_models.md)). To do so, you'll need to use TDW's [`RobotCreator`](../../python/robot_creator.md).

The `RobotCreator` can download a .urdf or .xacro file plus all relevant textures, meshes, etc. or it can use local files.

## Requirements

- Windows 10, OS X, or Linux
- (Windows only) Visual C++ 2012 Redistributable
- The `tdw` module
- Python 3.6+
- Unity Hub
- Unity Editor 2020.3.24f1
  - Build options must enabled for Windows, OS X, and Linux (these can  be set when installing Unity).
  - Ideally, Unity Editor should be installed via Unity Hub; otherwise, you'll need to add the `unity_editor_path` parameter to the `AssetBundleCreator` constructor (see below).

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

To convert mesh files into asset bundles, TDW uses [Asset Bundle Creator](https://github.com/alters-mit/asset_bundle_creator), a Unity Editor project. It is possible to run the Unity project without any Python wrapper classes but there is usually no reason to do so.

Asset Bundle Creator will be  downloaded automatically the first time you use the Python wrapper class (see below).

## Usage

To create an asset bundle of the UR5 robot:

```python
from tdw.robot_creator import RobotCreator
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

There are optional parameters for setting the semantic category of the model, for controlling whether the root object is immovable. [Read the API document for more information.](../../python/asset_bundle_creator.md)

### Constructor parameters

`RobotCreator` has several optional constructor parameters:

#### 1. `quiet`

If True, suppress output messages.

### 2. `unity_editor_path`

If you installed Unity Editor via Unity Hub, `RobotCreator` should be able to automatically find the Unity Editor executable.

If the Unity Editor executable is in an unexpected location, you will need to explicitly set its location in the `RobotCreator` by setting the optional `unity_editor_path` parameter:

```python
from tdw.robot_creator import RobotCreator

a = RobotCreator(quiet=True, unity_editor_path="D:/Unity/2020.3.24f1/Editor/Unity.exe")
```

#### 3. `check_version`

When you create a new `RobotCreator` Python object, it automatically compares the version of your local Unity project to the one stored on GitHub. This requires an Internet connection and might not be desirable in all cases, especially on servers. To prevent the version check, set `check_version=False` in the constructor.

#### 4. `display`

This must be set on Linux machines, especially headless servers, and must match a valid X display.

### Intermediate API calls

It's possible to manually perform any of the operations involved in creating an asset bundle.

#### 1. `clone_repo()`

Clone a robot repo:

```python
from tdw.robot_creator import RobotCreator

r = RobotCreator()
url = "https://github.com/ros-industrial/robot_movement_interface/blob/master/dependencies/ur_description/urdf/ur5_robot.urdf"
repo_path = r.clone_repo(url=url)
```

#### 2. `get_urdf_path_from_local_repo()`

Find a .urdf file within a local repo:

```python
from tdw.robot_creator import RobotCreator

r = RobotCreator()
url = "https://github.com/ros-industrial/robot_movement_interface/blob/master/dependencies/ur_description/urdf/ur5_robot.urdf"
repo_path = r.clone_repo(url=url)
urdf_path = r.get_urdf_path_from_local_repo(url=url, local_repo_path=repo_path)
```

#### 3. `urdf_to_prefab()`

In many cases, a fully automated robot creation process will be faulty; you may need to adjust parameters for joints, or remove some redundant joints, and so on. It's usually worth creating, testing, and editing a prefab before finalizing the asset bundle. To create a prefab, call `urdf_to_prefab()`:

```python
from tdw.robot_creator import RobotCreator
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

#### 4. `prefab_to_asset_bundles()`

Having adjusted a prefab as needed, you can then convert it into asset bundles by calling `prefab_to_asset_bundles()`:

```python
from tdw.robot_creator import RobotCreator
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("ur5_asset_bundles")
print(f"Asset bundles will be saved to: {output_directory}")
r = RobotCreator()
r.prefab_to_asset_bundles(name="ur5", output_directory=output_directory)
```

#### 5. `create_record()`

**TODO**

#### 6. `xacro_to_urdf()`

**TODO**

#### 7. `fix_urdf()`

**TODO**

## Create an asset bundle from a prefab

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

## Store metadata

`RobotCreator.create_asset_bundles()` returns a [`RobotRecord`](../../python/librarian/robot_librarian.md) metadata object, which contains the files paths to the asset bundle.

You can store a `RobotRecord` object in a [`RobotLibrarian`](../../python/librarian/robot_librarian.md), which is saved as a JSON file.

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

## Add the robot to TDW

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

- [`RobotCreator`](../../python/robot_creator.md)
- [`RobotLibrarian`](../../python/librarian/robot_librarian.md)