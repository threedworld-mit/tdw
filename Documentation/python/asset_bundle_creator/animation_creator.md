# AnimationCreator

`from tdw.asset_bundle_creator.animation_creator import AnimationCreator`

Create animation asset bundles from .anim or .fbx files.

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

**`AnimationCreator()`**

**`AnimationCreator(quiet=False, display="0", unity_editor_path=None, check_version=True)`**

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

#### get_creator_class_name

**`self.get_creator_class_name()`**

_Returns:_  The name of the Unity C# class, e.g. `ModelCreator`.

#### source_file_to_asset_bundles

**`self.source_file_to_asset_bundles(name, source_file, output_directory)`**

Convert a source .anim or .fbx file into 3 asset bundle files (Windows, OS X, and Linux).

Example source directory:

```
animation.anim
```

Example `output_directory`:

```
output_directory/
....Darwin/
........animation
....Linux/
........animation
....Windows/
........animation
....log.txt
....record.json
```

- `Darwin/animation`, `Linux/animation` and `Windows/animation` are the platform-specific asset bundles.
- `log.txt` is a log from the `asset_bundle_creator` Unity Editor project.
- `record.json` is a serialized record.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| name |  str |  | The name of the animation. |
| source_file |  Union[str, Path] |  | The path to the source file as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). |
| output_directory |  Union[str, Path] |  | The root output directory as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). If this directory doesn't exist, it will be created. |

#### source_directory_to_asset_bundles

**`self.source_directory_to_asset_bundles(source_directory, output_directory)`**

**`self.source_directory_to_asset_bundles(source_directory, output_directory, overwrite=False, continue_on_error=True, search_pattern=None)`**

Convert a directory of source .fbx and/or .obj models to asset bundles.

Calling this is *significantly* faster than calling `self.source_file_to_asset_bundles()` multiple times.

Example `source_directory`:

```
source_directory/
....animation_0.anim
....animation_1.anim
```

Example `output_directory`:

```
output_directory/
....animation_0/
........Darwin/
............animation_0
........Linux/
............animation_0
........Windows/
............animation_0
........record.json
........log.txt
....animation_1/
........Darwin/
............animation_1
........Linux/
............animation_1
........Windows/
............animation_1
........record.json
........log.txt
```

- `Darwin/animation_0`, `Linux/animation_0`, etc. are the platform-specific asset bundles.
- `record.json` is a JSON dictionary of the  record
- `log.txt` is a log from the `asset_bundle_creator` Unity Editor project.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| source_directory |  Union[str, Path] |  | The root directory of the source files as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). |
| output_directory |  Union[str, Path] |  | The root directory of the output files as a string or [`Path`](https://docs.python.org/3/library/pathlib.html). |
| overwrite |  bool  | False | If True, overwrite existing asset bundles. If this is set to False (the default value), you can stop/resume the processing of a directory's contents. |
| continue_on_error |  bool  | True | If True, continue generating asset bundles even if there is a problem with one model. If False, stop the process if there's an error. |
| search_pattern |  str  | None | A search pattern for files, for example `"*.obj"`. All subdirectories will be recursively searched. |