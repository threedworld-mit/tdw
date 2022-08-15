# AssetBundleCreatorBase

`from tdw.asset_bundle_creator_base import AssetBundleCreatorBase`

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

**`AssetBundleCreatorBase()`**

**`AssetBundleCreatorBase(quiet=False, display="0", unity_editor_path=None)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| quiet |  bool  | False | If True, don't print any messages to console. |
| display |  str  | "0" | The display to launch Unity Editor on. Ignored if this isn't Linux. |
| unity_editor_path |  Union[Path, str] | None | The path to the Unity Editor executable, for example `C:/Program Files/Unity/Hub/Editor/2020.3.24f1/Editor/Unity.exe`. If None, this script will try to find Unity Editor automatically. |

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

#### get_creator_class_name

**`self.get_creator_class_name()`**

_Returns:_  The name of the Unity C# class, e.g. `ModelCreatorLauncher`.

#### asset_bundles_exist

**`AssetBundleCreatorBase.asset_bundles_exist(name, output_directory)`**

_(Static)_


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| name |  str |  | The name of the asset bundle (the filename). |
| output_directory |  Union[str, Path] |  | The *root* output directory of *all* of the platform-specific asset bundles as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If an asset bundle is located in `/home/user/output_directory/Windows/asset_bundle`, set this to `"/home/user/output_directory"`. |

_Returns:_  True if asset bundles for all three platforms exist in `output_directory`.

#### run_process_and_print_log

**`AssetBundleCreatorBase.run_process_and_print_log(process, log_path)`**

**`AssetBundleCreatorBase.run_process_and_print_log(process, log_path, sleep_time=1)`**

_(Static)_

Poll a process to check if it is completed. If not, try to read a log file. Print the new text of the log file.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| process |  Popen |  | The process. |
| log_path |  Union[str, Path] |  | The path to the log file as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). |
| sleep_time |  float  | 1 | The time in seconds to wait between process polling. |