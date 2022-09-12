##### 3D Model Libraries

# Add your own models to TDW

It is possible to add any 3D model to TDW. However, the underlying Unity engine can't directly import 3D model files at runtime. They must be converted into asset bundles (the binary format that all other TDW objects are stored as). A separate set of applications must also generate physics colliders for the model.

## Requirements

- Windows 10, OS X, or Linux
- (Windows only) Visual C++ 2012 Redistributable
- The `tdw` module
- Python 3.6+
- git
- Unity Hub
- Unity Editor 2020.3.24f1
  - Build options must enabled for Windows, OS X, and Linux (these can be set when installing Unity).
  - Ideally, Unity Editor should be installed via Unity Hub; otherwise, you'll need to set the `unity_editor_path` parameter in the `ModelCreator` constructor (see below). 
  - To install on a Linux server, [read this.](https://github.com/alters-mit/asset_bundle_creator/blob/main/doc/linux_server.md)

## The Asset Bundle Creator Unity project

To convert mesh files into asset bundles, TDW uses [Asset Bundle Creator](https://github.com/alters-mit/asset_bundle_creator), a Unity Editor project. It is possible to run the Unity project without any Python wrapper classes but there is usually no reason to do so.

Asset Bundle Creator can be used not just for models, but for other types of asset bundles as well, such as [robots](../robots/custom_robots.md).

Asset Bundle Creator will be  downloaded automatically the first time you use the Python wrapper class (see below).

## The `ModelCreator` Python class

The [`ModelCreator`](../../python/asset_bundle_creator/model_creator.md) Python class will convert an .fbx or .obj file into an asset bundle and generate physics colliders. Depending on the complexity of the base mesh, this can be a lengthy process, especially when generating physics colliders.

```python
from pathlib import Path
from tdw.asset_bundle_creator.model_creator import ModelCreator
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("local_object")
print(f"Asset bundles will be saved to: {output_directory}")
ModelCreator().source_file_to_asset_bundles(name="cube",
                                            source_file=Path("cube.fbx").resolve(),
                                            output_directory=output_directory)
```

Output:

```
~/tdw_example_controller_output/local_object/
....Darwin/
........cube
....Linux/
........cube
....Windows/
........cube
....record.json
....log.txt
```

- `Darwin/cube`, `Linux/cube`, and `Windows/cube` are platform-specific asset bundles.
- `record.json` is a serialized ModelRecord.
- `log.txt` is a log of the creation process.

There are optional parameters for setting the semantic category of the model, for controlling whether intermediary mesh files and prefabs are saved or deleted, and so on. [Read the API document for more information.](../../python/asset_bundle_creator/model_creator.md)

This example includes all optional parameters:

```python
from pathlib import Path
from tdw.asset_bundle_creator.model_creator import ModelCreator
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("local_object")
print(f"Asset bundles will be saved to: {output_directory}")
ModelCreator().source_file_to_asset_bundles(name="cube",
                                            source_file=Path("cube.fbx").resolve(),
                                            output_directory=output_directory,
                                            vhacd_resolution=800000,
                                            internal_materials=True,
                                            wnid="n02942699",
                                            wcategory="camera",
                                            scale_factor=1,
                                            library_path="library.json",
                                            library_description="My custom library",
                                            cleanup=True,
                                            write_physics_quality=False,
                                            validate=False)
```

## Constructor parameters

`ModelCreator` has several optional constructor parameters:

#### 1. `quiet`

If True, suppress output messages.

#### 2. `unity_editor_path`

If you installed Unity Editor via Unity Hub, `ModelCreator` should be able to automatically find the Unity Editor executable.

If the Unity Editor executable is in an unexpected location, you will need to explicitly set the optional `unity_editor_path` parameter:

```python
from tdw.asset_bundle_creator.model_creator import ModelCreator

a = ModelCreator(quiet=True, unity_editor_path="D:/Unity/2020.3.24f1/Editor/Unity.exe")
```

#### 3. `check_version`

When you create a new `ModelCreator` Python object, it automatically compares the version of your local Unity project to the one stored on GitHub. This requires an Internet connection and might not be desirable in all cases, especially on servers. To prevent the version check, set `check_version=False` in the constructor.

#### 4. `display`

This must be set on Linux machines, especially headless servers, and must match a valid X display.

## Create multiple asset bundles

You can feasibly create asset bundles for multiple models by calling `source_file_to_asset_bundles()` in a loop. **This is not a good idea.** Repeatedly calling Unity from a Python script is actually very slow. (It also appears to slow down over many consecutive calls).

There are two ways to generate asset bundles for multiple source files:

### Option 1: `source_directory_to_asset_bundles()`

This will read a source directory and convert every mesh file within it into asset bundles.

```python
from pathlib import Path
from tdw.asset_bundle_creator.model_creator import ModelCreator
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("local_object")
a = ModelCreator()
a.source_directory_to_asset_bundles(source_directory=Path.home().joinpath("tdw_asset_bundles"),
                                    output_directory=output_directory)
```

There are many optional parameters not shown in this example. [Read the API document for more information.](../../python/asset_bundle_creator/model_creator.md)

### Option 2: `metadata_file_to_asset_bundles()`

This will read a metadata.csv file and convert every mesh file listed into asset bundles:

```python
from pathlib import Path
from tdw.asset_bundle_creator.model_creator import ModelCreator
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("local_object")
a = ModelCreator()
a.metadata_file_to_asset_bundles(metadata_path=Path.home().joinpath("tdw_asset_bundles/metadata.csv"),
                                 output_directory=output_directory)
```

There are many optional parameters not shown in this example. [Read the API document for more information.](../../python/asset_bundle_creator/model_creator.md)

This is an example metadata file:

```
name,wnid,wcategory,scale_factor,path
model_0,n04148054,scissors,1,source_directory/model_0/model_0.obj
model_1,n03056701,coaster,1,source_directory/model_1/model_1.obj
```

The *disadvantage* to using this function is that you need to prep the .csv file manually, as opposed to `source_directory_to_asset_bundles()`, which requires no manual prep (other than placing the target source files in the directory).

The *advantage* to using this function is that you can specify metadata such as the `wnid` per model; this data will be included in the `record.json` and `library.json` files.

## Create a prefab and then asset bundles

When creating asset bundles, `ModelCreator` automatically converts the source .fbx or .obj file into a Unity prefab, and then creates asset bundles of the prefab.

Sometimes, it's useful to convert a 3D model to a [prefab](https://docs.unity3d.com/Manual/Prefabs.html), edit the prefab in Unity Editor (for example, to adjust the color or positions of the colliders), and then convert the prefab to an asset bundle. In that case, you can call `source_file_to_prefab()`:

```python
from pathlib import Path
from tdw.asset_bundle_creator.model_creator import ModelCreator
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

model_name = "chair"
model_path = Path(model_name + ".fbx")
a = ModelCreator()
a.source_file_to_prefab(name=model_name, 
                        source_file=model_path,
                        output_directory=EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("source_file_to_prefab"))
```

Then adjust the prefab in Unity Editor. It will be located at: `~/asset_bundle_creator/Assets/prefabs/chair/chair.prefab`.

Then do this:

```python
from tdw.asset_bundle_creator.model_creator import ModelCreator
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

model_name = "chair"
output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("prefab_to_asset_bundles")
a = ModelCreator()
a.prefab_to_asset_bundles(name=model_name, 
                         output_directory=output_directory)
```

## Create a record

`source_file_to_asset_bundles()` automatically creates a new record.json file.

If you've called `source_file_to_prefab()` followed by `prefab_to_asset_bundles()`, you can create a record via `create_record()`:

```python
from pathlib import Path
from json import loads
from tdw.asset_bundle_creator.model_creator import ModelCreator
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from tdw.librarian import ModelRecord

output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("chair_example")
model_name = "chair"
model_path = Path(model_name + ".fbx")
a = ModelCreator()
a.create_record(name=model_name,
                output_directory=output_directory)
# Get the expected record path.
record_path = output_directory.joinpath("record.json")
# Load the record data.
record_data = loads(record_path.read_text())
# Load the record.
record = ModelRecord(record_data)
```

##  Create a custom model library

If you want to create many asset bundles, it's usually convenient to create your own `ModelLibrarian` and store it as a local json file. This `ModelLibrarian` can contain any records including those of models from other libraries.

To do this, set the `library_path` and, optionally, `library_description` parameters in either `source_file_to_asset_bundles()` or `create_record()`:

```python
from pathlib import Path
from tdw.asset_bundle_creator.model_creator import ModelCreator
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("local_object")
print(f"Asset bundles will be saved to: {output_directory}")
ModelCreator().source_file_to_asset_bundles(name="cube",
                                            source_file=Path("cube.fbx").resolve(),
                                            output_directory=output_directory.joinpath("cube"),
                                            library_path=output_directory.joinpath("library.json"),
                                            library_description="My custom library")
```

Output:

```
~/tdw_example_controller_output/local_object/
....cube/
........Darwin/
............cube
........Linux/
............cube
........Windows/
............cube
........record.json
........log.txt
....library.json
```

Note that we set `output_directory` to be a subdirectory ending in `cube/`. This is because we might want to create multiple asset bundles and store all of their metadata in a shared `library.json` file.

You can load the custom library by setting the `library` parameter in ModelLibrarian:

```python
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from tdw.librarian import ModelLibrarian

output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("local_object")
librarian = ModelLibrarian(library=str(output_directory.joinpath("library.json").resolve()))
```

## Validate a model

`ModelCreator` includes two optional functions for "validating" a model.

- `write_physics_quality()` will check the quality of the hull mesh colliders, meaning the extent to which they match the visual geometry.
- `validate()` will check the asset bundles for any errors such as missing materials.

Both of these functions are optional. If called, they will update the record.json file and library.json file (if one exists).

[Read the API document for more information.](../../python/asset_bundle_creator/model_creator.md)

## Cleanup

Call `cleanup()` to delete any intermediary mesh files and prefabs within the Unity Editor project created in the process of creating asset bundles. This will delete *all* intermediary files, including those of other models. This won't delete any of your original files (assuming that they weren't in the Unity Editor project).

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

## Add a custom model to a TDW simulation

You can load a model saved on a local machine with the [`add_object` command](../../api/command_api.md#add_object) just like a model from one of TDW's model library.

There are two ways to do this. First, you can just manually set the URL of the asset bundle. Be aware that you need to select the asset bundle for your operating system and you need to add `file:///` to the start of the URL:

```python
from platform import system
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

model_name = "chair"
output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("prefab_to_asset_bundles")
asset_bundle_path = output_directory.joinpath(system()).joinpath(model_name)
asset_bundle_url = "file:///" + str(asset_bundle_path.resolve()).replace("\\", "/")
```

The `system()` call will return your OS as a string, for example `Windows`.

And then we can create an object instance of the model with the `add_object` command:

```python
from platform import system
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

model_name = "chair"
output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("prefab_to_asset_bundles")
asset_bundle_path = output_directory.joinpath(system()).joinpath(model_name)
asset_bundle_url = "file:///" + str(asset_bundle_path.resolve()).replace("\\", "/")

c = Controller()
c.communicate([TDWUtils.create_empty_room(12, 12),
               {"$type": "add_object",
                "name": model_name,
                "url": asset_bundle_url,
                "scale_factor": 1,
                "position": {"x": 0, "y": 0, "z": 0},
                "rotation": {"x": 0, "y": 0, "z": 0},
                "category": "chair",
                "id": c.get_unique_id()}])
```

Or, you can use the record data generated by the `ModelCreator`. `ModelRecord.get_url()` returns the URL for your operating system:

```python
from json import loads
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from tdw.librarian import ModelRecord

model_name = "chair"
output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("prefab_to_asset_bundles")
record_path = output_directory.joinpath("record.json")
record_data = loads(record_path.read_text())
record = ModelRecord(record_data)
print(record.get_url())
```

## Tips for creating custom models

### .fbx unit scale

The unit scale of the exported .fbx file must be meters. If not, the physics colliders will likely be at the wrong scale.

### Export .fbx files from Blender 2.8

Blender can be fussy when exporting to Unity. If you export a .obj, you shouldn't have any problems. If you export a .fbx, there may be problems with the model's scale, as well as the collider's scale.

To set correct .fbx model scaling in Blender:

1. Set the scale of your model to 0.5

![](images/custom_models/0_set_scale.png)

2. Making sure that the model is still selected, apply the scale: **ctrl+a+s**
3. Making sure that the model is still selected, export the .fbx file. Make sure you're exporting only the selected object, and set the scaling to "FBX Units Scale".

<img src="images/custom_models/1_export.png" style="zoom:50%;" />

## Troubleshooting

- Make sure that Unity Editor is _closed_ when running `ModelCreator`.
- If `ModelCreator` can't find Unity Editor, set `unity_editor_path` in the constructor.
- If you get this warning in the Editor log: `[warn] kq_init: detected broken kqueue; not using.: Undefined error: 0` it means that there's a problem with your Unity license. Make sure you have valid and active Unity credentials.

***

**Next: [Add ShapeNet models to TDW](shapenet.md)**

[Return to the README](../../../README.md)

***

Example controllers:

- [local_object.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/3d_models/local_object.py) Create a local asset bundle and load it into TDW.

Python API:

- [`ModelLibrarian`](../../python/librarian/model_librarian.md)
- [`ModelCreator`](../../python/asset_bundle_creator/model_creator.md)

Command API:

- [`add_object`](../../api/command_api.md#add_object)
