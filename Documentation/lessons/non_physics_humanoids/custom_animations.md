##### Non-physics humanoids

# Create custom humanoid animations

It is possible to add your own humanoid animations into TDW from either a .anim file or a .fbx file. However, the files must first be converted into an asset bundle (just like [humanoids](custom_humanoids.md)). (In the case of a .fbx file, the animation will automatically be extracted into a .anim file and then converted.)  To do so, you'll need to use TDW's [`AnimationCreator`](../../python/asset_bundle_creator/animation_creator.md).

## Requirements

- Windows 10, OS X, or Linux
- (Windows only) Visual C++ 2012 Redistributable
- The `tdw` module
- Python 3.6+
- Unity Hub
- Unity Editor 2020.3.24f1
  - Build options must enabled for Windows, OS X, and Linux (these can  be set when installing Unity).
  - Ideally, Unity Editor should be installed via Unity Hub; otherwise, you'll need to set the `unity_editor_path` parameter in the `AnimationCreator` constructor (see below).
- git

## The Asset Bundle Creator Unity project

To convert robot .urdf files and their referenced meshes into asset bundles, TDW uses [Asset Bundle Creator](https://github.com/alters-mit/asset_bundle_creator), a Unity Editor project. It is possible to run the Unity project without any Python wrapper classes but there is usually no reason to do so.

Asset Bundle Creator can be used not just for models, but for other types of asset bundles as well, such as [humanoids](custom_humanoids.md).

Asset Bundle Creator will be  downloaded automatically the first time you use the Python wrapper class (see below).

## Usage

To create an asset bundle of a humanoid animation:

```python
from pathlib import Path
from tdw.asset_bundle_creator.animation_creator import AnimationCreator
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

source_file = Path.home().joinpath("walking.fbx")
output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("animations")
print(f"Asset bundles will be saved to: {output_directory}")
r = AnimationCreator()
r.source_file_to_asset_bundles(name="walking", 
                               source_file=source_file,
                               output_directory=output_directory)
```

Output:

```
~/tdw_example_controller_output/animations/
....Darwin/
........walking
....Linux/
........walking
....Windows/
........walking
....record.json
....log.txt
```

- `Darwin/walking`, `Linux/walking`, and `Windows/walking` are platform-specific asset bundles.
- `record.json` is a serialized HumanoidAnimationRecord.
- `log.txt` is a log of the creation process.

## Constructor parameters

`AnimationCreator` has several optional constructor parameters:

#### 1. `quiet`

If True, suppress output messages.

#### 2. `unity_editor_path`

If you installed Unity Editor via Unity Hub, `AnimationCreator` should be able to automatically find the Unity Editor executable.

If the Unity Editor executable is in an unexpected location, you will need to explicitly set its location in the `AnimationCreator` by setting the optional `unity_editor_path` parameter:

```python
from tdw.asset_bundle_creator.animation_creator import AnimationCreator

a = AnimationCreator(quiet=True, unity_editor_path="D:/Unity/2020.3.24f1/Editor/Unity.exe")
```

#### 3. `check_version`

When you create a new `AnimationCreator` Python object, it automatically compares the version of your local Unity project to the one stored on GitHub. This requires an Internet connection and might not be desirable in all cases, especially on servers. To prevent the version check, set `check_version=False` in the constructor.

#### 4. `display`

This must be set on Linux machines, especially headless servers, and must match a valid X display.

## Create multiple asset bundles

You can feasibly create asset bundles for multiple models by calling `source_file_to_asset_bundles()` in a loop. **This is not a good idea.** Repeatedly calling Unity from a Python script is actually very slow. (It also appears to slow down over many consecutive calls). Instead, call `source_directory_to_asset_bundles()`:

```python
from pathlib import Path
from tdw.asset_bundle_creator.animation_creator import AnimationCreator
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

h = AnimationCreator()
h.source_directory_to_asset_bundles(source_directory=Path.home().joinpath("animation_source_files"),
                                    output_directory=EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("animations"))
```

There are many optional parameters not shown in this example. [Read the API document for more information.](../../python/asset_bundle_creator/animation_creator.md)

## Cleanup

Call `cleanup()` to delete any intermediary files within the Unity Editor project created in the process of creating asset bundles. This will delete *all* intermediary files, including those of other models. This won't delete any of your original files (assuming that they weren't in the Unity Editor project).

## Low-level functions

`get_base_unity_call()` returns a list of strings that can be used to call a Unity Editor function:

```python
from tdw.asset_bundle_creator.animation_creator import AnimationCreator

print(AnimationCreator().get_base_unity_call())
```

Output:

```
['C:/Program Files/Unity/Hub/Editor/2020.3.24f1/Editor/Unity.exe', '-projectpath', 'C:/Users/USER Alter/asset_bundle_creator', '-quit', '-batchmode']
```

`call_unity()` will call the Asset Bundle Creator Unity project as a subprocess with command-line arguments. You can call arbitrary methods this way (assuming you know the [underlying C# API](https://github.com/alters-mit/asset_bundle_creator). This function is used by every function that communicates with Unity, for example `source_file_to_asset_bundles()`.

## Add a custom humanoid to a TDW simulation

You can load a humanoid saved on a local machine with the [`add_humanoid_animation` command](../../api/command_api.md#add_humanoid_animation).

There are two ways to do this. First, you can just manually set the URL of the asset bundle. Be aware that you need to select the asset bundle for your operating system and you need to add `file:///` to the start of the URL.

The second, easier, way is to deserialize the record.json file, which includes the file paths:

```python
import json
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.librarian import HumanoidAnimationRecord

name = "walking"
humanoid_id = 0
# This assumes that you've already created asset bundles and a record.json file in this directory.
output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("animations").joinpath(name)
# Load the record.
record_path = output_directory.joinpath("record.json")
record_data = json.loads(record_path.read_text())
record = HumanoidAnimationRecord(record_data)

c = Controller()
c.communicate([TDWUtils.create_empty_room(12, 12),
               Controller.get_add_humanoid(humanoid_name="man_casual_1",
                                           object_id=humanoid_id),
               {"$type": "add_humanoid_animation",
                "name": name,
                "url": record.get_url()},
               {"$type": "set_target_framerate",
                "framerate": record.framerate},
               {"$type": "play_humanoid_animation",
                "name": name,
                "id": humanoid_id,
                "framerate": record.framerate}])
```

***

**This is the last document in the "Non-physics humanoids" tutorial.**

[Return to the README](../../../README.md)

***

Python API:

- [`Controller.get_add_humanoid()`](../../python/controller.md)
- [`AnimationCreator`](../../python/asset_bundle_creator/animation_creator.md)
- [`HumanoidAnimationRecord`](../../python/librarian/humanoid_animation_librarian.md)

Command API:

- [`add_humanoid_animation`](../../api/command_api.md#add_humanoid_animation)
- [`set_target_framerate`](../../api/command_api.md#set_target_framerate)
- [`play_humanoid_animation`](../../api/command_api.md#play_humanoid_animation)
