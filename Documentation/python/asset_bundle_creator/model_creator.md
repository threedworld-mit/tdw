# ModelCreator

`from tdw.asset_bundle_creator.model_creator import ModelCreator`

Given a .fbx file or a .obj file, and (optionally) Materials and/or Textures folder adjacent to that file, create asset bundles for Windows, OS X, and Linux.

Usage:

```python
from tdw.asset_bundle_creator.model_creator import ModelCreator
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

a = ModelCreator()
a.source_file_to_asset_bundles(name="cube",
                               source_file="cube.fbx",
                               output_directory=EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("cube"))
```

[For more information, read this.](../../lessons/custom_models/custom_models.md)

## Class Variables

| Variable | Type | Description | Value |
| --- | --- | --- | --- |
| `PROJECT_PATH` | Path | The path to the `asset_bundle_creator` Unity project. | `Path.home().joinpath("asset_bundle_creator")` |
| `UNITY_VERSION` | str | Use this version of Unity Editor to launch the asset bundle creator. | `"2020.3"` |

***

## Fields

- `quiet` If True, don't print any messages to console.

***

## Functions

#### \_\_init\_\_

\_\_init\_\_

**`ModelCreator()`**

**`ModelCreator(quiet=False, display="0", unity_editor_path=None, check_version=True)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| quiet |  bool  | False | If True, don't print any messages to console. |
| display |  str  | "0" | The display to launch Unity Editor on. Ignored if this isn't Linux. |
| unity_editor_path |  Union[Path, str] | None | The path to the Unity Editor executable, for example `C:/Program Files/Unity/Hub/Editor/2020.3.24f1/Editor/Unity.exe`. If None, this script will try to find Unity Editor automatically. |
| check_version |  bool  | True | If True, check if there is an update to the Unity Editor project. |

#### get_base_unity_call

**`self.get_base_unity_call()`**

_Returns:_  The call to launch Unity Editor silently in batchmode, execute something, and then quit.

#### call_unity

**`self.call_unity(method, args, log_path)`**

**`self.call_unity(method, args, log_path, class_name=None)`**

Execute a call to Unity Editor. If `self.quiet == False` this will continuously print the log file.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| method |  str |  | The name of the method. |
| args |  List[str] |  | Arguments to send to Unity Editor in addition to those send via `self.get_base_unity_call()` and `-executeMethod`. |
| log_path |  Union[str, Path] |  | The path to the log file as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). |
| class_name |  str  | None | The name of the Unity C# class. If None, a default class name will be used. See: `self.get_creator_class_name()`. |

#### prefab_to_asset_bundles

**`self.prefab_to_asset_bundles(name, output_directory)`**

Build asset bundles from a .prefab file. This is useful when you want to edit the .prefab file by hand, e.g.:

1. `self.source_file_to_prefab()`
2. Edit .prefab file
3. `self.prefab_to_asset_bundles()`

Example source:

```
~/asset_bundle_creator/
....Assets/
........prefabs/
............name.prefab
........source_files/
............name/
................name.obj
................Materials/
```

Example output:

```
output_directory/
....Darwin/
........name
....Linux/
........name
....Windows/
........name
....log.txt
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| name |  str |  | The name of the model (the name of the .prefab file, minus the extension). |
| output_directory |  Union[str, Path] |  | The root output directory as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If this directory doesn't exist, it will be created. |

#### cleanup

**`self.cleanup()`**

Delete any intermediary files in the `asset_bundle_creator` Unity Editor project such as .prefab files.

#### asset_bundles_exist

**`AssetBundleCreator.asset_bundles_exist(name, directory)`**

_(Static)_

Check whether asset bundles exist for all platforms in the source directory.

Expected directory structure:

```
directory/
....Darwin/
........name
....Linux/
........name
....Windows/
........name
```

...where `name` is an asset bundle file.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| name |  str |  | The name of the asset bundle. |
| directory |  Union[str, Path] |  | The source directory as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). |

_Returns:_  True if asset bundles exist for all platforms in the source directory.

#### get_creator_class_name

**`self.get_creator_class_name()`**

_Returns:_  The name of the Unity C# class, e.g. `ModelCreator`.

#### source_file_to_asset_bundles

**`self.source_file_to_asset_bundles(name, source_file, output_directory)`**

**`self.source_file_to_asset_bundles(name, source_file, output_directory, vhacd_resolution=800000, internal_materials=False, wnid=None, wcategory=None, scale_factor=1, library_path=None, library_description=None, cleanup=True, write_physics_quality=False, validate=False)`**

Convert a source .obj or .fbx file into 3 asset bundle files (Windows, OS X, and Linux).

This is equivalent to, *but significantly faster than*, a combination of:

- `self.source_file_to_prefab()`
- `self.prefab_to_asset_bundles()`
- `self.create_record()`
- `self.cleanup()`
- `self.write_physics_quality()`
- `self.validate()`

Example source directory:

```
model.obj
model.mtl
Textures/
```

Example `output_directory`:

```
output_directory/
....Darwin/
........model
....Linux/
........model
....Windows/
........model
....record.json
....log.txt
library.json
```

- `Darwin/model`, `Linux/model` and `Windows/model` are the platform-specific asset bundles.
- `log.txt` is a log from the `asset_bundle_creator` Unity Editor project.
- `record.json` is a serialized `ModelRecord`.
- `library.json` is a serialized `ModelLibrarian`. It will only be added/set if the optional `library_path` is set.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| name |  str |  | The name of the model. This can be the same as the source file name minus the extension. |
| source_file |  Union[str, Path] |  | The path to the source .fbx or .obj file as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). |
| output_directory |  Union[str, Path] |  | The root output directory as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If this directory doesn't exist, it will be created. |
| vhacd_resolution |  int  | 800000 | The default resolution of VHACD. A lower value will make VHACD run faster but will create simpler collider mesh shapes. |
| internal_materials |  bool  | False | If True, the visual materials of the model are located within the source file. If False, the materials are located in `Materials/` directory next to the source file. |
| wnid |  str  | None | The WordNet ID of the model. Can be None. |
| wcategory |  str  | None | The WordNet category of the model. Can be None. |
| scale_factor |  float  | 1 | The model will be scaled by this factor. |
| library_path |  Union[str, Path] | None | If not None, this is a path as a string or [`Path`](https://docs.python.org/3/library/pathlib.html) to a new or existing `ModelLibrarian` .json file. The record will be added to this file in addition to being saved to `record.json`. |
| library_description |  str  | None | A description of the library. Ignored if `library_path` is None. |
| cleanup |  bool  | True | If True, delete intermediary files such as the prefab in the `asset_bundle_creator` Unity Editor project. |
| write_physics_quality |  bool  | False | If True, launch a controller and build to calculate the hull collider accuracy. Write the result to `output_directory/record.json` and to `library_path` if `library_path` is not None. |
| validate |  bool  | False | If True, launch a controller and build to validate the model, checking it for any errors. Write the result to `output_directory/record.json` and to `library_path` if `library_path` is not None. |

#### source_directory_to_asset_bundles

**`self.source_directory_to_asset_bundles(source_directory, output_directory)`**

**`self.source_directory_to_asset_bundles(source_directory, output_directory, library_description=None, vhacd_resolution=800000, internal_materials=False, overwrite=False, continue_on_error=True, search_pattern=None, cleanup=True)`**

Convert a directory of source .fbx and/or .obj models to asset bundles.

Calling this is *significantly* faster than calling `self.source_file_to_asset_bundles()` multiple times.

Example `source_directory`:

```
source_directory/
....model_0/
........model_0.obj
........model_0.mtl
........Textures/
....model_1/
........model_1.obj
........model_1.mtl
........Textures/
```

Example `output_directory`:

```
output_directory/
....model_0/
........Darwin/
............model_0
........Linux/
............model_0
........Windows/
............model_0
........record.json
........log.txt
....model_1/
........Darwin/
............model_1
........Linux/
............model_1
........Windows/
............model_1
........record.json
........log.txt
```

- `Darwin/model_0`, `Linux/model_0`, etc. are the platform-specific asset bundles.
- `record.json` is a JSON dictionary of the `ModelRecord`.
- `log.txt` is a log from the `asset_bundle_creator` Unity Editor project.

Note: This method does *not* call `self.write_physics_quality()` or `self.validate()`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| source_directory |  Union[str, Path] |  | The root directory of the source files as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). |
| output_directory |  Union[str, Path] |  | The root directory of the output files as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). |
| library_description |  str  | None | An optional description of the `ModelLibrarian` that will be included in the `library.json` file. |
| vhacd_resolution |  int  | 800000 | The default resolution of VHACD. A lower value will make VHACD run faster but will create simpler collider mesh shapes. |
| internal_materials |  bool  | False | If True, the visual materials of the models are located within the source file. If False, the materials are located in `Materials/` directory next to each source file. |
| overwrite |  bool  | False | If True, overwrite existing asset bundles. If this is set to False (the default value), you can stop/resume the processing of a directory's contents. |
| continue_on_error |  bool  | True | If True, continue generating asset bundles even if there is a problem with one model. If False, stop the process if there's an error. |
| search_pattern |  str  | None | A search pattern for files, for example `"*.obj"`. All subdirectories will be recursively searched. |
| cleanup |  bool  | True | If True, delete intermediary files such as the prefabs in the `asset_bundle_creator` Unity Editor project. |

#### metadata_file_to_asset_bundles

**`self.metadata_file_to_asset_bundles(metadata_path, output_directory)`**

**`self.metadata_file_to_asset_bundles(metadata_path, output_directory, library_description=None, vhacd_resolution=800000, internal_materials=False, overwrite=False, continue_on_error=True, cleanup=True)`**

Given a metadata .csv file within an output directory, generate asset bundles.

This is similar to `self.source_directory_to_asset_bundles()` but it reads a single .csv file instead of a directory structure, which allows you to specify record data per source file.

Calling this is *significantly* faster than calling `self.source_file_to_asset_bundles()` multiple times.

Example metadata .csv file:

```
name,wnid,wcategory,scale_factor,path
model_0,n04148054,scissors,1,source_directory/model_0/model_0.obj
model_1,n03056701,coaster,1,source_directory/model_1/model_1.obj
```

Example `output_directory`:

```
output_directory/
....model_0/
........Darwin/
............model_0
........Linux/
............model_0
........Windows/
............model_0
........record.json
........log.txt
....model_1/
........Darwin/
............model_1
........Linux/
............model_1
........Windows/
............model_1
........record.json
........log.txt
```

- `Darwin/model_0`, `Linux/model_0`, etc. are the platform-specific asset bundles.
- `record.json` is a JSON dictionary of the `ModelRecord`.
- `log.txt` is a log from the `asset_bundle_creator` Unity Editor project.

Note: This method does *not* call `self.write_physics_quality()` or `self.validate()`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| metadata_path |  Union[str, Path] |  | The path to the metadata file as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). |
| output_directory |  Union[str, Path] |  | The root directory of the output files as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). |
| library_description |  str  | None | An optional description of the `ModelLibrarian` that will be included in the `library.json` file. |
| vhacd_resolution |  int  | 800000 | The default resolution of VHACD. A lower value will make VHACD run faster but will create simpler collider mesh shapes. |
| internal_materials |  bool  | False | If True, the visual materials of the models are located within the source file. If False, the materials are located in `Materials/` directory next to each source file. |
| overwrite |  bool  | False | If True, overwrite existing asset bundles. If this is set to False (the default value), you can stop/resume the processing of a directory's contents. |
| continue_on_error |  bool  | True | If True, continue generating asset bundles even if there is a problem with one model. If False, stop the process if there's an error. |
| cleanup |  bool  | True | If True, delete intermediary files such as the prefabs in the `asset_bundle_creator` Unity Editor project. |

#### source_file_to_prefab

**`self.source_file_to_prefab(name, source_file, output_directory)`**

**`self.source_file_to_prefab(name, source_file, output_directory, vhacd_resolution=None, internal_materials=False)`**

Convert a source .obj or .fbx file into a .prefab file. Call this method when you intend to modify the .prefab file by hand before building asset bundles, e.g.:

1. `self.source_file_to_prefab()`
2. Edit .prefab file
3. `self.prefab_to_asset_bundles()`

Example source directory:

```
source_file.obj
source_file.mtl
Textures/
```

Example output:

```
~/asset_bundle_creator/
....Assets/
........prefabs/
............name.prefab
........source_files/
............name/
................name.obj
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| name |  str |  | The name of the model. This can be the same as the source file name minus the extension. This will be the name of the .prefab file. |
| source_file |  Union[str, Path] |  | The path to the source .fbx or .obj file as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). |
| output_directory |  Union[str, Path] |  | The root output directory as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If this directory doesn't exist, it will be created. |
| vhacd_resolution |  int  | None | The default resolution of VHACD. A lower value will make VHACD run faster but will create simpler collider mesh shapes. |
| internal_materials |  bool  | False | If True, the visual materials of the model are located within the source file. If False, the materials are located in `Materials/` directory next to the source file. |

#### create_record

**`self.create_record(name, output_directory)`**

**`self.create_record(name, output_directory, wnid=None, wcategory=None, scale_factor=1, library_path=None, library_description=None)`**

Create a model record and save it to disk. This requires asset bundles of the model to already exist:

```
output_directory/
....Darwin/
........model
....Linux/
........model
....Windows/
........model
....log.txt
```

Result:

```
output_directory/
....Darwin/
........model
....Linux/
........model
....Windows/
........model
....record.json
....log.txt
library.json
```

- `record.json` is a serialized `ModelRecord`.
- `library.json` is a serialized `ModelLibrarian`. It will only be added/set if the optional `library_path` is set.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| name |  str |  | The name of the model (matches the asset bundle file names). |
| output_directory |  Union[str, Path] |  | The root output directory as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If this directory doesn't exist, it will be created. |
| wnid |  str  | None | The WordNet ID of the model. Can be None. |
| wcategory |  str  | None | The WordNet category of the model. Can be None. |
| scale_factor |  float  | 1 | The model will be scaled by this factor. |
| library_path |  Union[str, Path] | None | If not None, this is a path as a string or [`Path`](https://docs.python.org/3/library/pathlib.html) to a new or existing `ModelLibrarian` .json file. The record will be added to this file in addition to being saved to `record.json`. |
| library_description |  str  | None | A description of the library. Ignored if `library_path` is None. |

#### write_physics_quality

**`self.write_physics_quality(name)`**

**`self.write_physics_quality(name, record_path=None, library_path=None)`**

Append the physics quality data to the temporary record file.
This is an optional record field that records the percentage of the model encapsulated by colliders.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| name |  str |  | The model name. |
| record_path |  Union[str, Path] | None | If not None, this is the path to the `ModelRecord` .json file, which will be updated. |
| library_path |  Union[str, Path] | None | If not None, this is the path to an existing `ModelLibrarian` .json file, which will be updated. |

#### validate

**`self.validate(name)`**

**`self.validate(name, record_path=None, library_path=None)`**

Validate the asset bundle.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| name |  str |  | The model name. |
| record_path |  Path  | None | If not None, this is the path to the `ModelRecord` .json file, which will be updated. |
| library_path |  Path  | None | If not None, this is the path to an existing `ModelLibrarian` .json file, which will be updated. |