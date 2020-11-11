# `asset_bundle_creator.py`

## `AssetBundleCreator`

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

***

#### `__init__(self, quiet: bool = False, display: str = ":0")`


| Parameter | Description |
| --- | --- |
| quiet | If true, don't print any messages to console. |
| display | The display to launch Unity Editor on. Ignored if this isn't Linux. |

***

#### `create_asset_bundle(self, model_path: Union[Path, str], cleanup: bool, wnid: int = -1, wcategory: str = "", scale: float = 1) -> (List[Path], Path)`

Create an asset bundle for each operating system. Typically, this is the only function you'll want to use.
This function calls in sequence: `fbx_to_obj()`, `obj_to_wrl()`, `wrl_to_obj()`, `move_files_to_unity_project()`, `create_prefab()`, `prefab_to_asset_bundle()`, and `create_record()`.

| Parameter | Description |
| --- | --- |
| model_path | The path to the model. |
| cleanup | If true, remove temporary files after usage. |
| wnid | The WordNet ID. |
| wcategory | The WordNet category. |
| scale | The scale of the object. |

_Returns:_ The paths to each asset bundle as Path objects (from pathlib) and the path to the metadata record file as a Path object (from pathlib).

***

#### `get_model_path(model_path: Union[Path, str]) -> Path`

_This is a static function._

Check if the model path is valid.

| Parameter | Description |
| --- | --- |
| model_path | The path to the model. Can be a Path object, or a string representing the absolute file path. |

_Returns:_ The path as a Path object if there are no problems.

***

#### `get_assets_directory(self) -> Path`

_Returns:_ The path to `<home>/asset_bundle_creator/Assets/`

***

#### `get_resources_directory(self) -> Path`

_Returns:_ The path to `<home>/asset_bundle_creator/Assets/Resources`

***

#### `get_editor_path() -> Path`

_This is a static function._

_Returns:_ The path to the Unity Editor executable.

***

#### `get_base_unity_call(self) -> List[str]`

_Returns:_ The call to launch Unity Editor silently in batchmode, execute something, and then quit.

***

#### `get_unity_project(self) -> Path`

Build the asset_bundle_creator Unity project.

_Returns:_ The path to the asset_bundle_creator Unity project.

***

#### `fbx_to_obj(self, model_path: Path) -> Tuple[Path, bool]`

Convert a .fbx file to a .obj file with assimp

| Parameter | Description |
| --- | --- |
| model_path | The path to the model. |

_Returns:_ The path to the new object, and True if it's a new file (False if it's the existing base file).

***

#### `obj_to_wrl(self, model_path: Path, vhacd_resolution: int = 8000000) -> Path`

Convert a .obj file to a .wrl file with testVHACD

| Parameter | Description |
| --- | --- |
| model_path | The path to the model. |
| vhacd_resolution | The V-HACD voxel resolution. A higher number will create more accurate physics colliders, but it will take more time to initially create the asset bundle. |

_Returns:_ The path to the .wrl file.

***

#### `wrl_to_obj(self, wrl_filename: Path, model_name: str) -> Path`

Convert a .wrl file back into a .obj file with meshconv

| Parameter | Description |
| --- | --- |
| wrl_filename | The to the .wrl file. |
| model_name | The name of the model (minus its file extension). |

_Returns:_ The path to the .obj file.

***

#### `move_files_to_unity_project(self, obj_colliders: Optional[Path], model_path: Path, sub_directory: str = "") -> List[Path]`

Moves all required files to the Unity project.

| Parameter | Description |
| --- | --- |
| obj_colliders | The path to the colliders .obj file. May be None. |
| sub_directory | Optional subdirectory to move the files to. |
| model_path | The path to the model. Can be a Path object, or a string representing the absolute file path. |

_Returns:_ A list of paths of files in the Unity project.

***

#### `create_prefab(self, colliders: str, model_name: str, model_extension: str) -> Tuple[Path, Path]`

Create a prefab from the files existing in the Unity project folder.

| Parameter | Description |
| --- | --- |
| colliders | The colliders filename. |
| model_name | The name of the model, minus its file extension. |
| model_extension | The file extension of the model (e.g. ".obj"). |

_Returns:_ The path to the prefab and the path to the report (if any).

***

#### `prefab_to_asset_bundle(self, prefab_path: Path, model_name: str, platforms: List[str] = None) -> List[Path]`

Given a .prefab, create asset bundles and write them to disk.

| Parameter | Description |
| --- | --- |
| prefab_path | The path to the .prefab file. |
| model_name | The name of the model, minus its file extension. |
| platforms | Platforms to build asset bundles for. Options: "windows", "osx", "linux". If None, build all. |

_Returns:_ The paths to the asset bundles.

***

#### `get_local_asset_bundle_path(model_name: str) -> Path`

_This is a static function._


| Parameter | Description |
| --- | --- |
| model_name | The name of the model, minus its file extension. |

_Returns:_ The expected path of the local asset bundle for this platform.

***

#### `create_record(self, model_name: str, wnid: int, wcategory: str, scale: float, urls: Dict[str, str], record: Optional[ModelRecord] = None, write_physics: bool = False) -> Path`

Create a local .json metadata record of the model.

| Parameter | Description |
| --- | --- |
| model_name | The name of the model. |
| wnid | The WordNet ID. |
| wcategory | The WordNet category. |
| scale | The default scale of the object. |
| urls | The finalized URLs (or local filepaths) of the assset bundles. |
| record | A pre-written metadata record. If not None, it will override the other parameters. |
| write_physics | If true, launch the build to write the physics quality. (This is optional). |

_Returns:_ The path to the file with the metadata record.

***

#### `get_local_urls(asset_bundle_paths: List[Path]) -> Dict[str, str]`

_This is a static function._

Generate a dictionary of local URLs from the asset bundle paths.

| Parameter | Description |
| --- | --- |
| asset_bundle_paths | The asset bundle paths. |

_Returns:_ A dictionary. Key = OS, Value = Path to the local file.

***

#### `write_physics_quality(record_path: Path, asset_bundle_path: Path) -> None`

_This is a static function._

Append the physics quality data to the temporary record file.
This is an optional record field that records the percentage of the model encapsualted by colliders.

| Parameter | Description |
| --- | --- |
| record_path | The path to the temporary record file. |
| asset_bundle_path | The URL to the local asset bundle. |

***

#### `validate(self, record_path: Path, asset_bundle_path: Path) -> Tuple[bool, str]`

Validate the asset bundle.

| Parameter | Description |
| --- | --- |
| record_path | The path to the temporary record file. |
| asset_bundle_path | The URL to the local asset bundle. |

_Returns:_ True if there aren't problems, and a string output report.

***

#### `create_many_asset_bundles(self, library_path: str, cleanup: bool = True, vhacd_resolution: int = 8000000) -> None`

Create asset bundles in batch from .obj or .fbx files already in: asset_bundle_creator/Assets/Resources/models
This function will create collider .obj files if there aren't any already
(it will look for a file named <model>_colliders.obj).

| Parameter | Description |
| --- | --- |
| library_path | The path to the library file. |
| cleanup | If true, remove all temp files when done. |
| vhacd_resolution | The V-HACD voxel resolution. A higher number will create more accurate physics colliders, but it will take more time to initially create the asset bundle. |

***

