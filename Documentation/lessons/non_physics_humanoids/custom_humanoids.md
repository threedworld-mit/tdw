##### Non-physics humanoids

# Create custom non-physics humanoids

It is possible to add your own non-physics humanoids into TDW from a .fbx file. However, the files must first be converted into an asset bundle (just like [objects](../custom_models/custom_models.md)). To do so, you'll need to use TDW's [`HumanoidCreator`](../../python/asset_bundle_creator/humanoid_creator.md).

The humanoid .fbx model must already be rigged. When it is converted into asset bundles, it won't receive colliders.

## Requirements

- The `tdw` module
- The Asset Bundle Creator Unity project. [Read this for a list of requirements.](https://github.com/alters-mit/asset_bundle_creator)

## The Asset Bundle Creator Unity project

To convert robot .urdf files and their referenced meshes into asset bundles, TDW uses [Asset Bundle Creator](https://github.com/alters-mit/asset_bundle_creator), a Unity Editor project. It is possible to run the Unity project without any Python wrapper classes but there is usually no reason to do so.

Asset Bundle Creator can be used not just for models, but for other types of asset bundles as well, such as [models](../custom_models/custom_models.md).

Asset Bundle Creator will be  downloaded automatically the first time you use the Python wrapper class (see below).

## Usage

To create an asset bundle of a humanoid:

```python
from pathlib import Path
from tdw.asset_bundle_creator.humanoid_creator import HumanoidCreator
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

source_file = Path.home().joinpath("humanoid.fbx")
output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("humanoid_asset_bundles")
print(f"Asset bundles will be saved to: {output_directory}")
r = HumanoidCreator()
r.source_file_to_asset_bundles(name="test_humanoid", 
                               source_file=source_file,
                               output_directory=output_directory)
```

Output:

```
~/tdw_example_controller_output/humanoid_asset_bundles/
....Darwin/
........test_humanoid
....Linux/
........test_humanoid
....Windows/
........test_humanoid
....record.json
....log.txt
```

- `Darwin/test_humanoid`, `Linux/test_humanoid`, and `Windows/test_humanoid` are platform-specific asset bundles.
- `record.json` is a serialized HumanoidRecord.
- `log.txt` is a log of the creation process.

## Constructor parameters

`HumanoidCreator` has several optional constructor parameters:

#### 1. `quiet`

If True, suppress output messages.

#### 2. `unity_editor_path`

If you installed Unity Editor via Unity Hub, `HumanoidCreator` should be able to automatically find the Unity Editor executable.

If the Unity Editor executable is in an unexpected location, you will need to explicitly set its location in the `HumanoidCreator` by setting the optional `unity_editor_path` parameter:

```python
from tdw.asset_bundle_creator.humanoid_creator import HumanoidCreator

a = HumanoidCreator(quiet=True, unity_editor_path="D:/Unity/2020.3.24f1/Editor/Unity.exe")
```

#### 3. `check_version`

When you create a new `HumanoidCreator` Python object, it automatically compares the version of your local Unity project to the one stored on GitHub. This requires an Internet connection and might not be desirable in all cases, especially on servers. To prevent the version check, set `check_version=False` in the constructor.

#### 4. `display`

This must be set on Linux machines, especially headless servers, and must match a valid X display.

## Create multiple asset bundles

You can feasibly create asset bundles for multiple models by calling `source_file_to_asset_bundles()` in a loop. **This is not a good idea.** Repeatedly calling Unity from a Python script is actually very slow. (It also appears to slow down over many consecutive calls). Instead, call `source_directory_to_asset_bundles()`:

```python
from pathlib import Path
from tdw.asset_bundle_creator.humanoid_creator import HumanoidCreator
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

h = HumanoidCreator()
h.source_directory_to_asset_bundles(source_directory=Path.home().joinpath("humanoid_fbx_files"),
                                    output_directory=EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("humanoids"))
```

There are many optional parameters not shown in this example. [Read the API document for more information.](../../python/asset_bundle_creator/humanoid_creator.md)

## Cleanup

Call `cleanup()` to delete any intermediary files within the Unity Editor project created in the process of creating asset bundles. This will delete *all* intermediary files, including those of other models. This won't delete any of your original files (assuming that they weren't in the Unity Editor project).

## Low-level functions

`get_base_unity_call()` returns a list of strings that can be used to call a Unity Editor function:

```python
from tdw.asset_bundle_creator.humanoid_creator import HumanoidCreator

print(HumanoidCreator().get_base_unity_call())
```

Output:

```
['C:/Program Files/Unity/Hub/Editor/2020.3.24f1/Editor/Unity.exe', '-projectpath', 'C:/Users/USER Alter/asset_bundle_creator', '-quit', '-batchmode']
```

`call_unity()` will call the Asset Bundle Creator Unity project as a subprocess with command-line arguments. You can call arbitrary methods this way (assuming you know the [underlying C# API](https://github.com/alters-mit/asset_bundle_creator). This function is used by every function that communicates with Unity, for example `source_file_to_asset_bundles()`.

## Add a custom humanoid to a TDW simulation

You can load a humanoid saved on a local machine with the [`add_humanoid` command](../../api/command_api.md#add_humanoid).

There are two ways to do this. First, you can just manually set the URL of the asset bundle. Be aware that you need to select the asset bundle for your operating system and you need to add `file:///` to the start of the URL.

The second, easier, way is to deserialize the record.json file, which includes the file paths:

```python
import json
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.librarian import HumanoidRecord

name = "humanoid_0"
# This assumes that you've already created asset bundles and a record.json file in this directory.
output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("humanoids").joinpath(name)
# Load the record.
record_path = output_directory.joinpath("record.json")
record_data = json.loads(record_path.read_text())
record = HumanoidRecord(record_data)

c = Controller()
c.communicate([TDWUtils.create_empty_room(12, 12),
               {"$type": "add_humanoid",
                "name": name,
                "url": record.get_url(),
                "id": c.get_unique_id()}])
```

***

**Next: [Create custom humanoid animations](custom_animations.md)**

[Return to the README](../../../README.md)

***

Python API:

- [`HumanoidCreator`](../../Python/asset_bundle_creator/humanoid_creator.md)
- [`HumanoidRecord`](../../python/librarian/humanoid_librarian.md)

Command API:

- [`add_humanoid`](../../api/command_api.md#add_humanoid)