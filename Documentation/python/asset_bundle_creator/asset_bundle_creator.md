# AssetBundleCreator

`from tdw.asset_bundle_creator.asset_bundle_creator import AssetBundleCreator`

Base class for creating asset bundles.

***

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

**`AssetBundleCreator()`**

**`AssetBundleCreator(quiet=False, display="0", unity_editor_path=None, check_version=True)`**

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