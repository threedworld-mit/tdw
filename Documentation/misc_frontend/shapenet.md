# ShapeNet and TDW

You can add [ShapeNet](https://www.shapenet.org/) models to TDW by [converting them to asset bundles](add_local_object.md).

TDW includes a script to convert both ShapeNet sets "out of the box": `Python/shapenet/shapenet.py`

## Requirements

You must download and extract the relevant ShapeNet zip files into the following directory structure:

- ShapeNet Core v2: Just unzip and you're all set.
- ShapeNet SEM: Download models, textures, and metadata.csv. They must all be in the same directory:

```
<root>
....models/
....textures/
....metadata.csv
```

**Additional requirements:**

- The latest version of Unity 2019.2
- Python 3.6+
- The [`tdw` Python module](../python/tdw.md)
- Windows 10

## Usage

```bash
py -3 shapenet.py [OPTIONS]
```

#### Arguments

| Argument             | Type | Description                                                  | Default                  |
| -------------------- | ---- | ------------------------------------------------------------ | ------------------------ |
| `--src`              | str  | The absolute path to the root source directory.              | `"D:/ShapeNetCore.v2"`   |
| `--dest`             | str  | The absolute path to the root destination directory.         | `"D:/tdw_shapenet_core"` |
| `--set`              | str  | Which ShapeNet set this is.<br>_Choices:_ `"core"` or `"sem"` | `"core"`                 |
| `--batch_size`       | int  | The number of models per batch.                              | 1000                     |
| `--vhacd_resolution` | int  | Higher value=better-fitting colliders and slower build process. | 8000000                  |
| --first_batch_only   | N/A  | Output only the first batch. Useful for testing purposes.    | N/A                      |

## What the script will do

1. Create a [records database file](../python/librarian/model_librarian.md) of all of the models. (Some of the metadata fields such as `bounds` will require Unity further down the creation pipeline.)
2. (ShapeNet SEM only): Move all images in the `textures/` folder to `models/`
3. Move _batches_ of .obj models, .mtl files, etc. to the asset_bundle_creator project. Default batch size is 1000.
4. Create collider .objs for each model .obj (unless one already exists).
5. Create prefabs.
6. Create asset bundles from the prefabs.
7. Update the database file with accurate metadata.
8. Move the asset bundles to a destination directory.
9. Remove all asset files (models, images, etc.) used to create the asset bundles.

For ShapeNet Core v2, every time a model is added to the _batch_, the Python script will make a few changes to the files. These changes are harmless, unless you're using these models for unrelated research.

## Time required

**This is a very slow process.** It can take multiple weeks to process all of the models.

To speed up the process, set `--vhacd_resolution` to a low value (e.g. 1000). This will make the physics colliders fit the model poorly, but will vastly speed up the overall asset bundle creation process. _Even then, expect the whole process to require several days._

**The process can be paused, restarted, etc.** Once you've generated the initial library file, the script will scan for existing asset bundles and won't try to re-create them.

## How to use the models in TDW

Once you've created the asset bundles, you can add them to TDW like any other asset bundles:

```python
from tdw.librarian import ModelLibrarian
from tdw.controller import Controller

shapenet_library_path = "path/to/shapenet/records.json"

c = Controller()
c.model_librarian = ModelLibrarian(library=shapenet_library_path)
c.start()
c.communicate({"$type": "create_empty_environment"})

c.add_object(c.model_librarian.records[0].name)
```

