# AssetBundleCreator

`from tdw.asset_bundle_creator import AssetBundleCreator`

Given a .fbx file or a .obj file, and (optionally) Materials and/or Textures folder adjacent to that file,
create asset bundles for Windows, OS X, and Linux.

Usage:

```python
from tdw.asset_bundle_creator import AssetBundleCreator

a = AssetBundleCreator()

# Typically this is the only function you'll want to call.
asset_bundle_paths, record_path = a.create_asset_bundle("cube.fbx", cleanup=True)
```

For more information, see: `Documentation/misc_frontend/add_local_object.md`.

## Class Variables

| Variable | Type | Description | Value |
| --- | --- | --- | --- |
| `UNITY_VERSION` | str | Use this version of Unity Editor to launch the asset bundle creator. | `"2020.3"` |

***

## Functions

#### \_\_init\_\_

**`AssetBundleCreator()`**

**`AssetBundleCreator(quiet=False, display="0", unity_editor_path=None)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| quiet |  bool  | False | If true, don't print any messages to console. |
| display |  str  | "0" | The display to launch Unity Editor on. Ignored if this isn't Linux. |
| unity_editor_path |  Union[Path, str] | None | The path to the Unity Editor executable, for example `C:/Program Files/Unity/Hub/Editor/2020.3.24f1/Editor/Unity.exe`. If None, this script will try to find Unity Editor automatically. |

#### get_base_unity_call

**`self.get_base_unity_call()`**

_Returns:_  The call to launch Unity Editor silently in batchmode, execute something, and then quit.

#### get_unity_project

**`self.get_unity_project()`**

Build the asset_bundle_creator Unity project.

_Returns:_  The path to the asset_bundle_creator Unity project.

#### get_project_path

**`AssetBundleCreator.get_project_path()`**

_(Static)_

_Returns:_  The expected path of the Unity project.

#### create_asset_bundle

**`self.create_asset_bundle(model_path, cleanup)`**

**`self.create_asset_bundle(model_path, cleanup, wnid=-1, wcategory="", scale=1)`**

Create an asset bundle for each operating system. Typically, this is the only function you'll want to use.
This function calls in sequence: `fbx_to_obj()`, `obj_to_wrl()`, `wrl_to_obj()`, `move_files_to_unity_project()`, `create_prefab()`, `prefab_to_asset_bundle()`, and `create_record()`.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| model_path |  Union[Path, str] |  | The path to the model. |
| cleanup |  bool |  | If true, remove temporary files after usage. |
| wnid |  int  | -1 | The WordNet ID. |
| wcategory |  str  | "" | The WordNet category. |
| scale |  float  | 1 | The scale of the object. |

_Returns:_  The paths to each asset bundle as Path objects (from pathlib) and the path to the metadata record file as a Path object (from pathlib).

#### get_model_path

**`AssetBundleCreator.get_model_path(model_path)`**

_(Static)_

Check if the model path is valid.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| model_path |  Union[Path, str] |  | The path to the model. Can be a Path object, or a string representing the absolute file path. |

_Returns:_  The path as a Path object if there are no problems.

#### get_assets_directory

**`self.get_assets_directory()`**

_Returns:_  The path to `<home>/asset_bundle_creator/Assets/`

#### get_resources_directory

**`self.get_resources_directory()`**

_Returns:_  The path to `<home>/asset_bundle_creator/Assets/Resources`

#### fbx_to_obj

**`self.fbx_to_obj(model_path)`**

Convert a .fbx file to a .obj file with assimp


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| model_path |  Path |  | The path to the model. |

_Returns:_  The path to the new object, and True if it's a new file (False if it's the existing base file).

#### obj_to_wrl

**`self.obj_to_wrl(model_path)`**

**`self.obj_to_wrl(model_path, vhacd_resolution=8000000)`**

Convert a .obj file to a .wrl file with testVHACD


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| model_path |  Path |  | The path to the model. |
| vhacd_resolution |  int  | 8000000 | The V-HACD voxel resolution. A higher number will create more accurate physics colliders, but it will take more time to initially create the asset bundle. |

_Returns:_  The path to the .wrl file.

#### wrl_to_obj

**`self.wrl_to_obj(wrl_filename, model_name)`**

Convert a .wrl file back into a .obj file with meshconv


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| wrl_filename |  Path |  | The to the .wrl file. |
| model_name |  str |  | The name of the model (minus its file extension). |

_Returns:_  The path to the .obj file.

#### move_files_to_unity_project

**`self.move_files_to_unity_project(obj_colliders, model_path)`**

**`self.move_files_to_unity_project(obj_colliders, sub_directory="", model_path)`**

Moves all required files to the Unity project.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| obj_colliders |  Optional[Path] |  | The path to the colliders .obj file. May be None. |
| sub_directory |  str  | "" | Optional subdirectory to move the files to. |
| model_path |  Path |  | The path to the model. Can be a Path object, or a string representing the absolute file path. |

_Returns:_  A list of paths of files in the Unity project.

#### create_prefab

**`self.create_prefab(colliders, model_name, model_extension)`**

Create a prefab from the files existing in the Unity project folder.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| colliders |  str |  | The colliders filename. |
| model_name |  str |  | The name of the model, minus its file extension. |
| model_extension |  str |  | The file extension of the model (e.g. ".obj"). |

_Returns:_  The path to the prefab and the path to the report (if any).

#### prefab_to_asset_bundle

**`self.prefab_to_asset_bundle(prefab_path, model_name)`**

**`self.prefab_to_asset_bundle(prefab_path, model_name, platforms=None)`**

Given a .prefab, create asset bundles and write them to disk.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| prefab_path |  Path |  | The path to the .prefab file. |
| model_name |  str |  | The name of the model, minus its file extension. |
| platforms |  List[str] | None | Platforms to build asset bundles for. Options: "windows", "osx", "linux". If None, build all. |

_Returns:_  The paths to the asset bundles.

#### get_local_asset_bundle_path

**`AssetBundleCreator.get_local_asset_bundle_path(model_name)`**

_(Static)_


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| model_name |  str |  | The name of the model, minus its file extension. |

_Returns:_  The expected path of the local asset bundle for this platform.

#### create_record

**`self.create_record(model_name, wnid, wcategory, scale, urls)`**

**`self.create_record(model_name, wnid, wcategory, scale, urls, record=None, write_physics=False)`**

Create a local .json metadata record of the model.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| model_name |  str |  | The name of the model. |
| wnid |  int |  | The WordNet ID. |
| wcategory |  str |  | The WordNet category. |
| scale |  float |  | The default scale of the object. |
| urls |  Dict[str, str] |  | The finalized URLs (or local filepaths) of the assset bundles. |
| record |  Optional[ModelRecord] | None | A pre-written metadata record. If not None, it will override the other parameters. |
| write_physics |  bool  | False | If true, launch the build to write the physics quality. (This is optional). |

_Returns:_  The path to the file with the metadata record.

#### get_local_urls

**`AssetBundleCreator.get_local_urls(asset_bundle_paths)`**

_(Static)_

Generate a dictionary of local URLs from the asset bundle paths.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| asset_bundle_paths |  List[Path] |  | The asset bundle paths. |

_Returns:_  A dictionary. Key = OS, Value = Path to the local file.

#### write_physics_quality

**`AssetBundleCreator.write_physics_quality(record_path, asset_bundle_path)`**

_(Static)_

Append the physics quality data to the temporary record file.
This is an optional record field that records the percentage of the model encapsualted by colliders.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| record_path |  Path |  | The path to the temporary record file. |
| asset_bundle_path |  Path |  | The URL to the local asset bundle. |

#### validate

**`self.validate(record_path, asset_bundle_path)`**

Validate the asset bundle.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| record_path |  Path |  | The path to the temporary record file. |
| asset_bundle_path |  Path |  | The URL to the local asset bundle. |

_Returns:_  True if there aren't problems, and a string output report.

#### create_many_asset_bundles

**`self.create_many_asset_bundles(library_path)`**

**`self.create_many_asset_bundles(library_path, cleanup=True, vhacd_resolution=8000000)`**

Create asset bundles in batch from .obj or .fbx files already in: asset_bundle_creator/Assets/Resources/models
This function will create collider .obj files if there aren't any already
(it will look for a file named <model>_colliders.obj).

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| library_path |  str |  | The path to the library file. |
| cleanup |  bool  | True | If true, remove all temp files when done. |
| vhacd_resolution |  int  | 8000000 | The V-HACD voxel resolution. A higher number will create more accurate physics colliders, but it will take more time to initially create the asset bundle. |

#### cleanup

**`self.cleanup()`**

Delete all files from `~/asset_bundle_creator` with these extensions: .obj, .fbx, .mtl, .mat, .jpg, .prefab