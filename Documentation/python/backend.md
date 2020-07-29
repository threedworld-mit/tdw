# `tdw` Module (Backend)

This document is an index of the backend scripts and files in the [`tdw` module](tdw.md). Most users won't need to ever use these scripts.

## Python Scripts

### `version.py`

The version of TDW. This is used when checking for updates.

### `tdw.backend.paths`

Contains filepaths used in various backend scripts.

 `ASSET_BUNDLE_VERIFIER_OUTPUT_DIR` and `VALIDATOR_REPORT_PATH` are used when creating model asset bundles. 

`PLAYER_LOG_PATH` and `EDITOR_LOG_PATH` are the paths to the build log files.

### `tdw.backend.platforms`

Various dictionaries to convert between platform names:

| Name       | Description                                                  | Example         |
| ---------- | ------------------------------------------------------------ | --------------- |
| SYSTEM     | The output of `platform.system()`                            | `Darwin`        |
| S3         | The platform name in TDW's [Amazon S3 asset bundle library](librarian/librarian.md). | `osx`           |
| UNITY      | The Unity Engine name for the platform                       | `StandaloneOSX` |
| EXECUTABLE | The file extension of an executable on the platform          | `.app`          |
| RELEASE    | The name of a [TDW release zip file](https://github.com/threedworld-mit/tdw/releases/latest) | `TDW_OSX`       |

Currently, the mapping of the strings is incomplete (we add to it as-needed).

The following dictionaries are available:

- `SYSTEM_TO_S3`
- `S3_TO_UNITY`
- `SYSTEM_TO_UNITY`
- `UNITY_TO_SYSTEM`
- `SYSTEM_TO_EXECUTABLE`
- `SYSTEM_TO_RELEASE`

Example:

```python
from platform import system
from tdw.backend.paths import SYSTEM_TO_S3

print(SYSTEM_TO_S3[system()]) # osx
```

### `tdw.FBOutput`

These scripts are the auto-generated Flatbuffer [output data](../api/output_data.md). They are difficult to use. You should always use the user-friendly wrapper classes in `tdw.output_data` instead.

### `tdw.flatbuffers`

Python [Flatbuffers](https://google.github.io/flatbuffers/flatbuffers_guide_use_python.html) library.

### `tdw.model_pipeline.missing_materials`

```python
from tdw.model_pipeline.missing_materials import MissingMaterials
from tdw.controller import Controller

MissingMaterials.run(Controller())
```

Check models for missing materials. Used by [AssetBundleCreator](asset_bundle_creator).

| Function                                                     | Description                              |
| ------------------------------------------------------------ | ---------------------------------------- |
| `start(c: Controller)`                                       | Start the controller.                    |
| `materials_are_missing(c: Controller, record: ModelRecord, url: str) -> bool` | Check a model for missing materials.     |
| `run(c: Controller)`                                         | Check every model for missing materials. |

### `tdw.model_pipeline.validator.py`

Usage: `py -3 validator.py [ARGUMENTS]`

Check a model asset bundle for problems. First, load the model into the build and report back any errors. Then, scan the model for missing materials. Used by [AssetBundleCreator](asset_bundle_creator).

| Argument              | Type | Description                            |
| --------------------- | ---- | -------------------------------------- |
| `--record_path`       | str  | The path to the temporary record file. |
| `--asset_bundle_path` | str  | The path to the local asset bundle.    |

### `tdw.model_pipeline.write_physics_quality.py`

Usage: `py -3 write_physics_quality.py [ARGUMENTS]`

Check a model asset bundle for problems (see `validator.py`; this is a sub-class of `Validator`) and write the `physics_quality` value of the [record](librarian/model_librarian.md). Used by [AssetBundleCreator](asset_bundle_creator).

| Argument              | Type | Description                            |
| --------------------- | ---- | -------------------------------------- |
| `--record_path`       | str  | The path to the temporary record file. |
| `--asset_bundle_path` | str  | The path to the local asset bundle.    |

### `tdw.release.build`

[Read this.](build.md)

### `tdw.release.pypi`

[Read this.](pypi.md)

## Other Files

### `asset_bundle_creator.unitypackage`

The compressed Unity package used to create a local copy of the [asset_bundle_creator Unity project](../misc_frontend/add_local_object)..

### `exe/`

Windows executables used by [AssetBundleCreator](asset_bundle_creator). None of these were made by the TDW team.

| .exe            | Description                      |
| --------------- | -------------------------------- |
| `assimp.exe`    | Used to convert a .fbx to a .obj |
| `meshconv.exe`  | Used to convert a .wrl to a .obj |
| `testVHACD.exe` | Used to create a .obj to a .wrl  |

### `flex/fluid_types.json`

Parameter values for each [type of fluid](fluid_types.json).

### `metadata_libraries/`

This folder contains each [library .json file](librarian/librarian.md). You should always use a Librarian object to read these files.

### `py_impact/material_data/`

This folder contains the raw audio material data used by [PyImpact](py_impact.md).

### `py_impact/objects.csv`

This spreadsheet contains per-object audio data for [PyImpact](py_impact.md). You should always use the wrapper function `PyImpact.get_objects()` instead of reading this file directly.