# Record Libraries and Librarians

## Asset Bundles

Most objects in TDW are stored as [asset bundles](https://docs.unity3d.com/Manual/AssetBundlesIntro.html). These external binary files can be loaded into the build at runtime. TDW has [four types of asset bundles](../../getting_started.md#Terminology):

1. Models
2. Materials
3. Scenes
4. HDRI Skyboxes
5. Humanoid Animations
6. Humanoids

TDW has large **libraries** of each of these categories stored on a remote server.

## Librarians and Records

The `tdw` Python module includes various .json **records database** files. These files are organized by the type of asset bundle (models, materials, etc.) and contain lists of **records**. Each record corresponds to an asset bundle.

```python
from tdw.librarian import ModelLibrarian

lib = ModelLibrarian()
record = lib.records[0]
print(record.name + ", " + record.wcategory) # afl_lamp, table lamp
```

Technically, all that the Unity Engines requires in order to load an asset bundle is its URL (or local filepath), but TDW also requires additional metadata (such as the name of the asset bundle); each record has this required information, plus additional metadata that you might find useful.

The `tdw` module includes Python class wrappers for the different types of libraries and records:

| Asset Bundle Type | Librarian        | Record        | Command |
| ----------------- | ---------------- | ------------- | ------------- |
| Model             | `ModelLibrarian` | `ModelRecord` | `add_object` |
| Material | `MaterialLibrarian` | `MaterialRecord` | `add_material` |
| Scene | `SceneLibrarian` | `SceneRecord` | `add_scene` |
| HDRI Skybox | `HDRISkyboxLibrarian` | `HDRISkyboxRecord` | `add_hdri_skybox` |
| Humanoid Animation | `HumanoidAnimationLibrarian` | `HumanoidAnimationRecord` | `add_humanoid_animation` |
| Humanoid | `HumanoidLibrarian` | `HumanoidRecord` | `add_humanoid` |

The `tdw` module includes one or more .json records files for each type of asset bundle for each TDW asset bundle stored on a remote server.

## What libraries are available?

Each type of library has a `get_library_filenames()` static function that will list all of the records library filenames bundled with TDW.

```python
from tdw.librarian import ModelLibrarian

filenames = ModelLibrarian.get_library_filenames()
print(filenames) # ['models_core.json', 'models_full.json', 'models_special.json']
```

If you set the `library` parameter in the constructor to one of those filenames, the librarian object will unpack the data from that file:

```python
from tdw.librarian import ModelLibrarian

lib = ModelLibrarian(library='models_full.json')
```

If you don't supply the `library` parameter, the librarian will use the first filename in the list returned by `get_librarian_filenames()`:

```python
from tdw.librarian import ModelLibrarian

lib = ModelLibrarian() # Will use 'models_core.json'
```

## Creating your own asset bundles

TDW includes [automated tools for converting a .obj or .fbx file into an asset bundle](../../misc_frontend/add_local_object.md). It is _technically_ possible to create the other types of asset bundles, but this functionality isn't supported yet.

When you create an asset bundle, it won't be uploaded to TDW's remote server; it will stay on your machine. You might therefore find it useful to create your own records database file for your asset bundles (see API documentation).

#### Creating your own records library

You may find it useful to organize your asset bundle metadata in a records library. To create your own:

You can create your own library .json file and access it by setting `library` to the absolute path of that file:

```python
path = "/home/username/tdw_custom_library.json"
ModelLibrarian.create_library(description="My custom library", path=path)
lib = ModelLibrarian(library=path)
```

## APIs

- [Model Librarian](model_librarian.md)
- [Material Librarian](material_librarian.md)
- [Scene Librarian](scene_librarian.md)
- [HDRI Skybox Librarian](hdri_skybox_librarian.md)
- [Humanoid Animation Librarian](humanoid_animation_librarian.md)
- [Humanoid Librarian](humanoid_librarian.md)