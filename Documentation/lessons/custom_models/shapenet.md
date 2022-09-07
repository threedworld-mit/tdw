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

## Setup

### ShapeNetCore

1. Clone the `tdw` repo in order to use `shapenet.py`.
2. See [the requirements for using the `AssetBundleCreator`](custom_models.md).
3. Download and extract `ShapeNetCore.v2.zip`.

### ShapeNet SEM

1. Clone the `tdw` repo in order to use `shapenet.py`.
2. See [the requirements for using the `AssetBundleCreator`](custom_models.md).
3. Create a root directory, for example `D:/shapenet_sem/`
4. Download and extract `models-OBJ.zip` into the root directory.
5. Download and extract `models-textures.zip` into the root directory.
6. Move every file in `textures/` into `models/`.
7. Download `metadata.csv` to the root directory.

Result:

```
D:/shapenet_sem/
....models/
....metadata.csv
```

## Usge

1. `cd tdw/Python/shapenet`
2. `python3 shapenet.py [ARGUMENTS]`

| Argument             | Type | Description                                                  | Default                  |
| -------------------- | ---- | ------------------------------------------------------------ | ------------------------ |
| `--src`              | str  | The absolute path to the root source directory.              | `"D:/ShapeNetCore.v2"`   |
| `--dest`             | str  | The absolute path to the root destination directory.         | `"D:/tdw_shapenet_core"` |
| `--set`              | str  | Which ShapeNet set this is.<br>_Choices:_ `"core"` or `"sem"` | `"core"`                 |
| `--vhacd_resolution` | int  | Higher value=better-fitting colliders and slower build process. | 8000000                  |

## What the script will do

1. Convert ShapeNet metadata into a new metadata.csv file: `output_directory/metadata.csv`.
2. Run `AssetBundleCreator.metadata_file_to_asset_bundles()`. This will generate asset bundles and metadata records.

## Time required

**This is a very slow process. It can take multiple weeks to process all of the models.**

To speed up the process, set `--vhacd_resolution` to a low value (e.g. 1000). This will make the physics colliders fit the model poorly, but will vastly speed up the overall asset bundle creation process. _Even then, expect the whole process to require several days._

**The process can be paused, restarted, etc.** Once you've generated the initial library file, the script will scan for existing asset bundles and won't try to re-create them

## How to use the models in TDW

Once you've created the asset bundles, you can add them to TDW like any other asset bundles:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

shapenet_library_path = "path/to/shapenet/records.json"

c = Controller()
model_librarian = ModelLibrarian(library=shapenet_library_path)
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_object(model_name=model_librarian.records[0].name,
                                object_id=c.get_unique_id(),
                                library=shapenet_library_path)])
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
