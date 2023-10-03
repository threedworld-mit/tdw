# CompositeObjectCreator

`from tdw.asset_bundle_creator.composite_object_creator import CompositeObjectCreator`

Create asset bundles of objects from a .urdf file.

This class should very rarely be used! In most cases, you should use [`RobotCreator`](robot_creator.md) instead.

This class should only be used for *non*-robot .urdf files such as PartNet Mobility files.

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

**`CompositeObjectCreator()`**

**`CompositeObjectCreator(quiet=False, display="0", unity_editor_path=None, check_version=True)`**

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

**`self.prefab_to_asset_bundles(name, output_directory, targets=None)`**

Build asset bundles from a .prefab file. This is useful when you want to edit the .prefab file by hand, e.g.:

1. `self.source_file_to_prefab()`
2. Edit .prefab file
3. `self.prefab_to_asset_bundles()`

Example source:

```
~/asset_bundle_creator/
....Assets/
........prefabs/
............name/
................name.prefab
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
| targets |  List[str] | None | A list of build targets. Options: "linux", "osx", "windows", "webgl". If None, defaults to `["linux", "osx", "windows"]`. |

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

**`self.source_file_to_asset_bundles(name, source_file, output_directory, vhacd_resolution=800000, wnid=None, wcategory=None, cleanup=True, targets=None)`**

Convert a source .urdf file into 3 asset bundle files (Windows, OS X, and Linux).

This is equivalent to, *but significantly faster than*, a combination of:

- `self.source_file_to_prefab()`
- `self.prefab_to_asset_bundles()`
- `self.cleanup()`

Example source directory:

```
mobility.urdf
textured_objs/
....original-1.obj
....original-1.mtl
.... (etc.)
```

Example `output_directory`:

```
output_directory/
....Darwin/
........mobility
....Linux/
........mobility
....Windows/
........mobility
....log.txt
....model.json
```

- `Darwin/mobility`, `Linux/mobility` and `Windows/mobility` are the platform-specific asset bundles.
- `log.txt` is a log from the `asset_bundle_creator` Unity Editor project.
- `model.json` is a JSON dump of the converted URDF data and mesh paths.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| name |  str |  | The name of the model. This can be the same as the source file name minus the extension. |
| source_file |  Union[str, Path] |  | The path to the source .urdf file as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). |
| output_directory |  Union[str, Path] |  | The root output directory as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If this directory doesn't exist, it will be created. |
| vhacd_resolution |  int  | 800000 | The default resolution of VHACD. A lower value will make VHACD run faster but will create simpler collider mesh shapes. |
| wnid |  str  | None | The WordNet ID of the model. Can be None. |
| wcategory |  str  | None | The WordNet category of the model. Can be None. |
| cleanup |  bool  | True | If True, delete intermediary files such as the prefab in the `asset_bundle_creator` Unity Editor project. |
| targets |  List[str] | None | A list of build targets. Options: "linux", "osx", "windows", "webgl". If None, defaults to `["linux", "osx", "windows"]`. |

#### source_file_to_prefab

**`self.source_file_to_prefab(name, source_file, output_directory)`**

**`self.source_file_to_prefab(name, source_file, output_directory, vhacd_resolution=None)`**

Convert a source .urdf file into a .prefab file. Call this method when you intend to modify the .prefab file by hand before building asset bundles, e.g.:

1. `self.source_file_to_prefab()`
2. Edit .prefab file
3. `self.prefab_to_asset_bundles()`

Example source directory:

```
mobility.urdf
textured_objs/
....original-1.obj
....original-1.mtl
.... (etc.)
```

Example output:

```
~/asset_bundle_creator/
....Assets/
........prefabs/
............mobility.prefab
........source_files/
............mobility/
................mobility.obj
```

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| name |  str |  | The name of the model. This can be the same as the source file name minus the extension. This will be the name of the .prefab file. |
| source_file |  Union[str, Path] |  | The path to the source .urdf file as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). |
| output_directory |  Union[str, Path] |  | The root output directory as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If this directory doesn't exist, it will be created. |
| vhacd_resolution |  int  | None | The default resolution of VHACD. A lower value will make VHACD run faster but will create simpler collider mesh shapes. |