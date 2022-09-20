##### Read/Write to Disk

# Import .sdf and .lisdf files

*Please read the documentation for [custom models](../custom_models/custom_models.md), [custom robots](../robots/custom_robots.md), and [custom composite objects](../composite_objects/create_from_urdf.md).*

It is possible to import data from an [.sdf](http://sdformat.org/) or [.lisdf](https://learning-and-intelligent-systems.github.io/kitchen-worlds/tut-lisdf/) scene description file into TDW using the [`LisdfReader`](../../Python/add_ons/lisdf_reader.md)

As with all other import processes in TDW, objects referenced by .sdf and .lisdf file must be converted into asset bundles. We can do this by calling `LisdfReader.read()`:

```python
from pathlib import Path
from tdw.add_ons.lisdf_reader import LisdfReader
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

source_path = Path.home().joinpath("kitchen-worlds/assets/scenes/kitchen_basics.lisdf").resolve()
output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("")
lisdf_reader = LisdfReader()
lisdf_reader.read(lisdf_path=source_path, output_directory=output_directory)
```

The above example will take a long time to complete. However, once the asset bundles have been generated, subsequent `read()` calls will be nearly instantaneous.

The above example uses a .lisdf file from the [kitchen-worlds repo](https://github.com/Learning-and-Intelligent-Systems/kitchen-worlds/blob/main/assets/scenes/kitchen_basics.lisdf); there are issues with cloning this repo in Windows. The best way to clone the repo is with WSL: call `wsl git` instead of `git`.

## The Asset Bundle Creator Unity project

To create asset bundles, TDW uses [Asset Bundle Creator](https://github.com/alters-mit/asset_bundle_creator), a Unity Editor project. It is possible to run the Unity project without any Python wrapper classes but there is usually no reason to do so. In the Python class, `LisdfReader.read()` launches`LisdfReader.Read()` in the Unity project.

Asset Bundle Creator will be  downloaded automatically the first time you use the Python wrapper class (see below).

## Requirements

- Windows 10, OS X, or Linux
- (Windows only) Visual C++ 2012 Redistributable
- The `tdw` module
- Python 3.6+
- git
- Unity Hub
- Unity Editor 2020.3.24f1
  - Build options must enabled for Windows, OS X, and Linux (these can be set when installing Unity).
  - Ideally, Unity Editor should be installed via Unity Hub; otherwise, you'll need to set the `unity_editor_path` parameter (see below). 
  - To install on a Linux server, [read this.](https://github.com/alters-mit/asset_bundle_creator/blob/main/doc/linux_server.md)

## Unity Editor parameters

If you installed Unity Editor via Unity Hub, `LisdfReader` should be able to automatically find the Unity Editor executable.

If the Unity Editor executable is in an unexpected location, you will need to explicitly set the optional `unity_editor_path` parameter:

```python
from pathlib import Path
from tdw.add_ons.lisdf_reader import LisdfReader
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

source_path = Path.home().joinpath("kitchen-worlds/assets/scenes/kitchen_basics.lisdf").resolve()
output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("")
lisdf_reader = LisdfReader()
lisdf_reader.read(lisdf_path=source_path,
                  output_directory=output_directory,
                  unity_editor_path="D:/Unity/2020.3.24f1/Editor/Unity.exe")
```

When you call `read()`, it automatically compares the version of your local Unity project to the one stored on GitHub. This requires an Internet connection and might not be desirable in all cases, especially on servers. To prevent the version check, set `check_version=False`:

```python
from pathlib import Path
from tdw.add_ons.lisdf_reader import LisdfReader
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

source_path = Path.home().joinpath("kitchen-worlds/assets/scenes/kitchen_basics.lisdf").resolve()
output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("")
lisdf_reader = LisdfReader()
lisdf_reader.read(lisdf_path=source_path,
                  output_directory=output_directory,
                  check_version=False)
```

On Linux servers, set `display` to the correct X display:

```python
from pathlib import Path
from tdw.add_ons.lisdf_reader import LisdfReader
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

source_path = Path.home().joinpath("kitchen-worlds/assets/scenes/kitchen_basics.lisdf").resolve()
output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("")
lisdf_reader = LisdfReader()
lisdf_reader.read(lisdf_path=source_path,
                  output_directory=output_directory,
                  display=":0")
```

## Objects, composite objects, and robots

Within the Asset Bundle Creator Unity project, the parser reads a .lisdf file and builds asset bundles as objects, composite objects, and robots depending on the description:

- If the model is described within the root file, it is assumed to be a static model, and will be generated using ModelCreator.
- If the model is described in a referenced .urdf file, it is assumed to be a composite object and will be generated using CompositeObjectCreator.
- [Composite objects and robots are not the same in TDW.](../composite_objects/create_from_urdf.md) If a referenced .urdf file is describes a *robot*, you need to set this manually in your Python class, in which case asset bundles will be generated using RobotCreator.

To manually specify which .urdf files are robots, as opposed to articulated objects, set the `robot_metadata` parameter in `read()`, which accepts a list of [`LisdfRobotMetadata`](../../python/lisdf_data/lisdf_robot_metadata.md):

```python
from pathlib import Path
from tdw.add_ons.lisdf_reader import LisdfReader
from tdw.lisdf_data.lisdf_robot_metadata import LisdfRobotMetadata
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

# Define a robot.
pr2 = LisdfRobotMetadata(name="pr2",
                         link_name_excludes_regex=["_gazebo_", "_cam_", "world_link", "imu_link",
                                                   "sensor_mount_link", "head_plate_frame",
                                                   "_gripper_motor_accelerometer_link"],
                         link_exclude_types=["camera", "laser"])

source_path = Path.home().joinpath("kitchen-worlds/assets/scenes/kitchen_basics.lisdf").resolve()
output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("")
lisdf_reader = LisdfReader()

# Read the .lisdf file. PR2 will be a robot.
lisdf_reader.read(lisdf_path=source_path, output_directory=output_directory, robot_metadata=[pr2])
```

`link_name_excludes_regex` and `link_exclude_types` are parameters used  to "fix" an overly complicated .urdf file; [read this for more information](../robots/custom_robots.md).

## Overwrite and cleanup

If there are problems with the asset bundles, you may wish to regenerate them. In that case, set `overwrite=true` in `read()`:

```python
from pathlib import Path
from tdw.add_ons.lisdf_reader import LisdfReader
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

source_path = Path.home().joinpath("kitchen-worlds/assets/scenes/kitchen_basics.lisdf").resolve()
output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("")
lisdf_reader = LisdfReader()
lisdf_reader.read(lisdf_path=source_path, output_directory=output_directory, overwrite=True)
```

You might want to adjust or test the model and robot prefabs. To do this, set `cleanup=False` in `read()`:

```python
from pathlib import Path
from tdw.add_ons.lisdf_reader import LisdfReader
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

source_path = Path.home().joinpath("kitchen-worlds/assets/scenes/kitchen_basics.lisdf").resolve()
output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("")
lisdf_reader = LisdfReader()
lisdf_reader.read(lisdf_path=source_path, output_directory=output_directory, cleanup=False)
```

Having set `cleanup=False`, you can manually create asset bundles from the prefabs using [ModelCreator](../custom_models/custom_models.md), [RobotCreator](../robots/custom_robots.md), and [CompositeObjectCreator](../composite_objects/create_from_urdf.md).

## Write and send commands

After parsing a .sdf or .lisdf file and generating asset bundles, `LisdfReader` will also generate a `commands.json` file that contains a list of commands that can create the scene in TDW:

```python
from pathlib import Path
import json
from tdw.add_ons.lisdf_reader import LisdfReader
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

source_path = Path.home().joinpath("kitchen-worlds/assets/scenes/kitchen_basics.lisdf").resolve()
output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("")
lisdf_reader = LisdfReader()
lisdf_reader.read(lisdf_path=source_path,
                  output_directory=output_directory)
commands_path = output_directory.joinpath("commands.json")
commands = json.loads(commands_path.read_text())
```

If you append `LisdfReader` to a controller, you don't need to read  the commands manually; as an add-on, `LisdfReader` will automatically send the commands:

```python
from pathlib import Path
from tdw.controller import Controller
from tdw.add_ons.lisdf_reader import LisdfReader
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

source_path = Path.home().joinpath("kitchen-worlds/assets/scenes/kitchen_basics.lisdf").resolve()
output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("")

# Create a controller.
c = Controller()
# Create an LISDF reader.
lisdf_reader = LisdfReader()
# Append the LISDF reader as an add-on.
c.add_ons.append(lisdf_reader)
# Read the .lisdf file. Create asset bundles if needed.
lisdf_reader.read(lisdf_path=source_path,
                  output_directory=output_directory)
# This will send the commands generated by `lisdf_reader`.
c.communicate([])
```

***

**This is the last document in the "Read/Write to Disk" tutorial.**

[Return to the README](../../../README.md)

***

Python API:

- [`LisdfReader`](../../python/add_ons/lisdf_reader.md)
- [`LisdfRobotMetadata`](../../python/lisdf_data/lisdf_robot_metadata.md)
