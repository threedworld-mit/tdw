##### 3D Model Libraries

# Add your own models to TDW

It is possible to add any 3D model to TDW. However, the underlying Unity engine can't directly import 3D model files at runtime. They must be converted into asset bundles (the binary format that all other TDW objects are stored as). A separate set of applications must also generate physics colliders for the model.

## Requirements

- Windows 10, OS X, or Linux
- (Windows only) Visual C++ 2012 Redistributable
- The `tdw` module
- Python 3.6+
- Unity Hub
- Unity Editor 2020.3.24f1
  - Build options must enabled for Windows, OS X, and Linux (these can  be set when installing Unity).
  - Ideally, Unity Editor should be installed via Unity Hub; otherwise, you'll need to add the `unity_editor_path` parameter to the `AssetBundleCreator` constructor (see below).
- A .fbx or .obj+.mtl model

## The Asset Bundle Creator Unity project

To convert mesh files into asset bundles, TDW uses [Asset Bundle Creator](https://github.com/alters-mit/asset_bundle_creator), a Unity Editor project. It is possible to run the Unity project without any Python wrapper classes but there is usually no reason to do so.

Asset Bundle Creator will be  downloaded automatically the first time you use the Python wrapper class (see below).

## The `AssetBundleCreator` Python class

The [`AssetBundleCreator`](../../python/asset_bundle_creator.md) Python class will convert an .fbx or .obj file into an asset bundle and generate physics colliders. Depending on the complexity of the base mesh, this can be a lengthy process, especially when generating physics colliders.

```python
from pathlib import Path
from tdw.asset_bundle_creator import AssetBundleCreator
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("local_object")
print(f"Asset bundles will be saved to: {output_directory}")
AssetBundleCreator().source_file_to_asset_bundles(name="cube",
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
```

`Darwin/cube`, `Linux/cube`, and `Windows/cube` are platform-specific asset bundles.

There are optional parameters for setting the semantic category of the model, for controlling whether intermediary mesh files and prefabs are saved or deleted, and so on. [Read the API document for more information.](../../python/asset_bundle_creator.md)

This example includes all optional parameters:

```python
from pathlib import Path
from tdw.asset_bundle_creator import AssetBundleCreator
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("local_object")
print(f"Asset bundles will be saved to: {output_directory}")
AssetBundleCreator().source_file_to_asset_bundles(name="cube",
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

### Unity Editor path

If you installed Unity Editor via Unity Hub, `AssetBundleCreator` should be able to automatically find the Unity Editor executable.

If the Unity Editor executable is in an unexpected location, you will need to explicitly set its location in the `AssetBundleCreator` by setting the optional `unity_editor_path` parameter:

```python
from tdw.asset_bundle_creator import AssetBundleCreator

a = AssetBundleCreator(quiet=True, unity_editor_path="D:/Unity/2020.3.24f1/Editor/Unity.exe")
```

### Intermediate API calls

It's possible to manually perform any of the operations involved in creating an asset bundle.

Sometimes, it's useful to convert a 3D model to a [prefab](https://docs.unity3d.com/Manual/Prefabs.html), edit the prefab in Unity Editor (for example, to adjust the color or positions of the colliders), and then convert the prefab to an asset bundle. In that case, you'd first do this:

```python
from pathlib import Path
from tdw.asset_bundle_creator import AssetBundleCreator
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

model_name = "chair"
model_path = Path(model_name + ".fbx")
a = AssetBundleCreator()
a.source_file_to_prefab(name=model_name, 
                        source_file=model_path,
                        output_directory=EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("source_file_to_prefab"))
```

Then adjust the prefab in Unity Editor. It will be located at: `~/asset_bundle_creator/Assets/prefabs/chair/chair.prefab`.

Then do this:

```python
from tdw.asset_bundle_creator import AssetBundleCreator
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

model_name = "chair"
output_directory = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("prefab_to_asset_bundles")
a = AssetBundleCreator()
a.prefab_to_asset_bundles(name=model_name, 
                         output_directory=output_directory)
```

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

Or, you can use the record data generated by the `AssetBundleCreator`. `ModelRecord.get_url()` returns the URL for your operating system:

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

##  Create a custom model library

If you want to create many asset bundles, it's usually convenient to create your own `ModelLibrarian` and store it as a local json file. This `ModelLibrarian` can contain any model records including models from other model libraries.

First, create the librarian json file by calling `ModelLibrarian.create_library()`:

```python
from tdw.librarian import ModelLibrarian

ModelLibrarian.create_library(description="Custom model librarian",
                              path="models_custom.json")
```

Then, load the librarian and add your model:

```python
from pathlib import Path
from json import loads
from tdw.librarian import ModelLibrarian, ModelRecord

# Convert from a relative to absolute path to load the librarian.
librarian = ModelLibrarian(library=str(Path("models_custom.json").resolve()))

record = ModelRecord(loads(Path.home().joinpath("tdw_asset_bundles/chair/record.json").read_text()))

librarian.add_or_update_record(record=record, overwrite=False, write=True)
```

You can add a record from another model library in nearly the same way:

```python
from pathlib import Path
from tdw.librarian import ModelLibrarian

custom_librarian = ModelLibrarian(library=str(Path("models_custom.json").resolve()))
core_librarian = ModelLibrarian("models_core.json")
record = core_librarian.get_record("rh10")
custom_librarian.add_or_update_record(record=record, overwrite=False, write=True)
```

## Creating Many Asset Bundles

You could convert many models to asset bundles by creating a loop that repeatedly calls `AssetBundleCreator.create_asset_bundles()`. **This is not a good idea.** Repeatedly calling Unity from a Python script is actually very slow. (It also appears to slow down over many consecutive calls).

Instead, consider using `create_many_asset_bundles(library_path)` for large numbers of models. This function will walk through `asset_bundle_creator/Assets/Resources/models/` searching for .obj and .fbx models. It will convert these models to asset bundles.

## .fbx unit scale

The unit scale of the exported .fbx file must be meters. If not, the physics colliders will likely be at the wrong scale.

## Export .fbx files from Blender 2.8

Blender can be fussy when exporting to Unity. If you export a .obj, you shouldn't have any problems. If you export a .fbx, there may be problems with the model's scale, as well as the collider's scale.

To set correct .fbx model scaling in Blender:

1. Set the scale of your model to 0.5

![](images/custom_models/0_set_scale.png)

2. Making sure that the model is still selected, apply the scale: **ctrl+a+s**
3. Making sure that the model is still selected, export the .fbx file. Make sure you're exporting only the selected object, and set the scaling to "FBX Units Scale".

<img src="images/custom_models/1_export.png" style="zoom:50%;" />

 ## Troubleshooting

- Make sure that Unity Editor and Visual Studio are _closed_ when running `AssetBundleCreator`.
- Make sure that you have installed the Editor _via Unity Hub_; the Python script assumes this when trying to find the editor .exe
- If `AssetBundleCreator` is crashing with errors, please let us know; copy+paste the error when you do.
- If you get this warning in the Editor log: `[warn] kq_init: detected broken kqueue; not using.: Undefined error: 0` it means that there's a problem with your Unity license. Make sure you have valid and active Unity credentials.

***

**Next: [Add ShapeNet models to TDW](shapenet.md)**

[Return to the README](../../../README.md)

***

Example controllers:

- [local_object.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/3d_models/local_object.py) Create a local asset bundle and load it into TDW.

Python API:

- [`ModelLibrarian`](../../python/librarian/model_librarian.md)
- [`AssetBundleCreator`](../../python/asset_bundle_creator.md)

Command API:

- [`add_object`](../../api/command_api.md#add_object)
