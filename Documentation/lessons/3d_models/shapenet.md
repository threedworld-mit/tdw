##### 3D Model Libraries

# Add ShapeNet models to TDW

You can add [ShapeNet](https://shapenet.org/) models to TDW by converting them to asset bundles.

ShapeNet is a huge repository of semantically tagged obj files available to users that has several advantages and disadvantages compared to TDW's models.

**Advantages:**

- There are *far* more ShapeNet models and semantic categories than TDW's model libraries.
- ShapeNet is free (as opposed to [TDW's largest model library](non_free_models.md), which is non-free).

**Disadvantages:**

- ShapeNet models are inferior to TDW's models.
  - Most of them are not photorealistic.
  - Some of them are corrupted or have features that make them unsuitable for TDW such as being a 2D quad. 
  - Many of them have different "up" directions.
  - ShapeNet models were often created at different canonical scales; for example, two ShapeNet that are ostensibly 1 cubic meter may be totally different sizes when added  to TDW.
- ShapeNet models are not hosted by default as TDW asset bundles. This is because of the reasons listed above (it would be extremely time-consuming for us to vet all of ShapeNet) and for potential licensing reasons.

That said, you can generate your own ShapeNet asset bundles and host them locally.

## Requirements

1. You must download and extract the relevant ShapeNet zip files into the following directory structure:

  - ShapeNet Core v2: Just unzip and you're all set.
  - ShapeNet SEM: Download models, textures, and metadata.csv. They must all be in the same directory:

```
<root>
....models/
....textures/
....metadata.csv
```

2. Clone the `tdw` repo.
3. See [the requirements for using the `AssetBundleCreator`](custom_models.md).

## Usage

1. `cd tdw/Python/shapenet`
2. `python3 shapenet.py [ARGUMENTS]`

| Argument             | Type | Description                                                  | Default                  |
| -------------------- | ---- | ------------------------------------------------------------ | ------------------------ |
| `--src`              | str  | The absolute path to the root source directory.              | `"D:/ShapeNetCore.v2"`   |
| `--dest`             | str  | The absolute path to the root destination directory.         | `"D:/tdw_shapenet_core"` |
| `--set`              | str  | Which ShapeNet set this is.<br>_Choices:_ `"core"` or `"sem"` | `"core"`                 |
| `--batch_size`       | int  | The number of models per batch.                              | 1000                     |
| `--vhacd_resolution` | int  | Higher value=better-fitting colliders and slower build process. | 8000000                  |
| `--first_batch_only` | N/A  | Output only the first batch. Useful for testing purposes.    | N/A                      |

## What the script will do

1. Create a [model librarian file](../../python/librarian/model_librarian.md) of all of the models. (Some of the metadata fields such as `bounds` will require Unity further down the creation pipeline.)
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

**This is a very slow process. It can take multiple weeks to process all of the models.**

To speed up the process, set `--vhacd_resolution` to a low value (e.g. 1000). This will make the physics colliders fit the model poorly, but will vastly speed up the overall asset bundle creation process. _Even then, expect the whole process to require several days._

**The process can be paused, restarted, etc.** Once you've generated the initial library file, the script will scan for existing asset bundles and won't try to re-create them

## How to use the models in TDW

Once you've created the asset bundles, you can add them to TDW like any other asset bundles:

```python
from tdw.librarian import ModelLibrarian
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

shapenet_library_path = "path/to/shapenet/records.json"

c = Controller()
c.model_librarian = ModelLibrarian(library=shapenet_library_path)
c.communicate([TDWUtils.create_empty_room(12, 12,),
               c.get_add_object(model_name=c.model_librarian.records[0].name,
                                object_id=c.get_unique_id())])
```

***

**This is the last document in the "Non-Default 3D models" tutorial.**

[Return to the README](../../../README.md)

***

ShapeNet convertor script:

- [`shapenet.py`](https://github.com/threedworld-mit/tdw/blob/master/Python/shapenet/shapenet.py)

Python API:

- [`ModelLibrarian`](../../python/librarian/model_librarian.md)
- [`AssetBundleCreator`](../../python/asset_bundle_creator.md)
