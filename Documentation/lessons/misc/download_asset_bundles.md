# Download asset bundles

*If you haven't done so already, please read the documentation for the types asset bundles used in your project:*
- *[Models](../core_concepts/objects.md)* 
- *[Scenes](../core_concepts/scenes.md)*
- *[Materials](../scene_setup_low_level/materials_textures_colors.md)*
- *[HDRI skyboxes](../photorealism/lighting.md)*
- *[Robots](../robots/overview.md)*
- *[Non-physics humanoids](../non_physics/humanoids.md)*
- *[Humanoid animations](../non_physics/humanoids.md)*

As described in [this document](../3d_models/custom_models.md), it is possible to create custom 3D models and load them at runtime by providing a filepath instead of a URL. It is likewise possible to download any* of TDW's asset bundles (models, scenes, etc.) and load them at runtime.

The main reason to use local asset bundles is that is *always* faster to load local asset bundles than remote asset bundles because local files don't need to be downloaded. That said, it can still take a while to load the asset bundles into memory at runtime.

The main reason to *not* use local asset bundles is that it will be relatively difficult to code your project. You will need to develop a system that points to the correct download folder regardless of the user or operating system. Also, if you update the list of local asset bundles (for example, if you decide to add or remove models from your project), those changes won't automatically propagate to the local asset bundles.

\* *If you want to download from models_full.json, [you will need access credentials](../3d_models/non_free_models.md).*

## Download lists of asset bundles and create local librarians

The simplest way to download lists of asset bundles is with `TDWUtils.download_asset_bundles()`. This function will:

- Download asset bundles for your OS (for example, if you are using Windows, it will download Windows asset bundles)
- Create local librarian .json files

### Example 1: Download model asset bundles

This example will download two models from `models_core.json` and create a local librarian at `D:/local_asset_bundles/models.json`:

```python
from tdw.tdw_utils import TDWUtils

TDWUtils.download_asset_bundles(path="D:/local_asset_bundles",
                                models={"models_core.json": ["iron_box", "rh10"]})
```

To use the newly-downloaded models:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

model_librarian_path = "D:/local_asset_bundles/models.json"
c = Controller()
c.communicate([TDWUtils.create_empty_room(12, 12),
               Controller.get_add_object(model_name="rh_10",
                                         object_id=0,
                                         library=model_librarian_path),
               Controller.get_add_object(model_name="iron_box",
                                         object_id=1,
                                         library=model_librarian_path)])
```

You can download from multiple librarian files at once; the local asset bundles will be combined into a single librarian:

```python
from tdw.tdw_utils import TDWUtils
from tdw.librarian import ModelLibrarian

TDWUtils.download_asset_bundles(path="D:/local_asset_bundles",
                                models={"models_core.json": ["iron_box", "rh10"],
                                        "models_flex.json": ["cube"]})
librarian = ModelLibrarian("D:/local_asset_bundles/models.json")
for record in librarian.records:
    print(record.name)
```

Output:

```
cube
iron_box
rh10
```

### Example 2: Download model and scene asset bundles

This example downloads a model and a scene:

```python
from tdw.tdw_utils import TDWUtils

TDWUtils.download_asset_bundles(path="D:/local_asset_bundles",
                                models={"models_core.json": ["iron_box"]},
                                scenes={"scenes.json": ["tdw_room"]})
```

To use the newly-downloaded model and scene:

```python
from tdw.controller import Controller

model_librarian_path = "D:/local_asset_bundles/models.json"
scene_librarian_path = "D:/local_asset_bundles/scenes.json"
c = Controller()
c.communicate([Controller.get_add_scene(scene_name="tdw_room",
                                        library=scene_librarian_path),
               Controller.get_add_object(model_name="iron_box",
                                         object_id=0,
                                         library=model_librarian_path)])
```

### Example 3: Download many types of asset bundles

You can download asset bundles for scenes, materials, HDRI skyboxes, robots, non-physics humanoids, and humanoid animations:

```python
from tdw.tdw_utils import TDWUtils

TDWUtils.download_asset_bundles(path="D:/local_asset_bundles",
                                models={"models_core.json": ["iron_box", "rh10"],
                                        "models_flex.json": ["cube"]},
                                scenes={"scenes.json": ["tdw_room"]},
                                materials={"materials_high.json": ["ceramic_raw_striped"],
                                           "materials_med.json": ["glass_clear"]},
                                hdri_skyboxes={"hdri_skyboxes.json": ["bergen_4k"]},
                                robots={"robots.json": ["ur5"]},
                                humanoids={"humanoids.json": ["woman_business_2", "woman_casual_1"]},
                                humanoid_animations={"humanoid_animations.json": ["walking_1", "walking_2"]})
```

If `path` is `"D:/local_asset_bundles"`, these are the filepaths of the librarian files:

| Asset bundle type   | Path                                                |
| ------------------- | --------------------------------------------------- |
| Models              | `"D:/local_asset_bundles/models.json"`              |
| Scenes              | `"D:/local_asset_bundles/scenes.json"`              |
| Materials           | `"D:/local_asset_bundles/materials.json"`           |
| HDRI Skyboxes       | `"D:/local_asset_bundles/hdri_skyboxes.json"`       |
| Robots              | `"D:/local_asset_bundles/robots.json"`              |
| Humanoids           | `"D:/local_asset_bundles/humanoids.json"`           |
| Humanoid animations | `"D:/local_asset_bundles/humanoid_animations.json"` |

## Set the default librarians

You might want to have the option to set TDW's default librarians if you expect users to sometimes use remote asset bundles and sometimes use local asset bundles.

When you call `Controller.get_add_object()`,`Controller.get_add_physics_object()`, `Controller.get_add_material()`, `Controller.get_add_scene()`, etc. the controller does the following:

1. If the `library` parameter is *not* explicitly set, the controller sets it to either the most recently-used value or a default value (such as `models_core.json`).
2. The controller looks for a librarian in the corresponding dictionary. For models, this is `Controller.MODEL_LIBRARIANS`. If the librarian object doesn't exist, the controller creates it.
3. The controller gets the record from the librarian, and gets the URL from the record.

You could feasibly toggle between remote and local librarians like this:

```python
from argparse import ArgumentParser
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

parser = ArgumentParser()
parser.add_argument("--local", action="store_true")
args = parser.parse_args()
if args.local:
    model_librarian_path = "D:/local_asset_bundles/models.json"
else:
    model_librarian_path = "models_core.json"
c = Controller()
c.communicate([TDWUtils.create_empty_room(12, 12),
               Controller.get_add_object(model_name="iron_box",
                                         object_id=0,
                                         library=model_librarian_path)])
```

However, in practice this kind of coding can quickly become flimsy, because you'll need to remember to set `library` *every* time you add an asset bundle.

A workaround to this is to set the librarian itself:

```python
from argparse import ArgumentParser
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.librarian import ModelLibrarian

parser = ArgumentParser()
parser.add_argument("--local", action="store_true")
args = parser.parse_args()
if args.local:
    Controller.MODEL_LIBRARIANS["models_core.json"] = ModelLibrarian("D:/local_asset_bundles/models.json")
else:
    Controller.MODEL_LIBRARIANS["models_core.json"] = ModelLibrarian("models_core.json")
c = Controller()
c.communicate([TDWUtils.create_empty_room(12, 12),
               Controller.get_add_object(model_name="iron_box",
                                         object_id=0)])
```

Now, the default library ("models_core.json") can actually point to your local librarian.

`TDWUtils.set_default_librarians()` is a wrapper of the above example:

```python
from argparse import ArgumentParser
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

parser = ArgumentParser()
parser.add_argument("--local", action="store_true")
args = parser.parse_args()
if args.local:
    TDWUtils.set_default_libraries(model_library="D:/local_asset_bundles/models.json")
c = Controller()
c.communicate([TDWUtils.create_empty_room(12, 12),
               Controller.get_add_object(model_name="iron_box",
                                         object_id=0)])
```

You can use `TDWUtils.set_defalt_libaries()` to set multiple library asset bundles types at the same time:

```python
from argparse import ArgumentParser
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

parser = ArgumentParser()
parser.add_argument("--local", action="store_true")
args = parser.parse_args()
if args.local:
    TDWUtils.set_default_libraries(model_library="D:/local_asset_bundles/models.json",
                                   scene_library="D:/local_asset_bundles/scenes.json")
c = Controller()
c.communicate([Controller.get_add_scene(scene_name="tdw_room"),
               Controller.get_add_object(model_name="iron_box",
                                         object_id=0)])
```

Full list of parameters: `model_library`, `scene_library`, `material_library`, `hdri_skybox_library`, `robot_library`, `humanoid_library`, `humanoid_animation_library`.

## Download individual asset bundles

You an also download individual asset bundles as needed. This can be useful if you only need a few asset bundles and the code described above is more complicated than it needs to be.

To get the URL of an asset bundle, see `record.urls`:

```python
from tdw.librarian import ModelLibrarian

librarian = ModelLibrarian("models_core.json")
record = librarian.get_record("iron_box")
print(record.urls)
```

Output:

```
{'Darwin': 'https://tdw-public.s3.amazonaws.com/models/osx/2018-2019.1/iron_box', 'Linux': 'https://tdw-public.s3.amazonaws.com/models/linux/2018-2019.1/iron_box', 'Windows': 'https://tdw-public.s3.amazonaws.com/models/windows/2018-2019.1/iron_box'}
```

Downloading an asset bundle is as simple as copy+pasting the URL into your browser. You can also download an asset bundle programmatically using `requests`:

```python
from tdw.librarian import ModelLibrarian
from requests import get

librarian = ModelLibrarian("models_core.json")
record = librarian.get_record("iron_box")
resp = get(record.urls["Linux"]).content
with open("iron_box", "wb") as f:
    f.write(resp)
```

To load the asset bundle:

```python
from pathlib import Path
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

model_path = "file:///" + str(Path("iron_box").resolve())
c = Controller()
c.communicate([TDWUtils.create_empty_room(12, 12),
               {"$type": "add_object",
                "name": "iron_box",
                "url": model_path,
                "scale_factor": {"x": 1, "y": 1, "z": 1},
                "position": {"x": 0, "y": 0, "z": 0},
                "rotation": {"x": 0, "y": 0, "z": 0},
                "category": "box",
                "id": 0}])
```

***

[Return to the README](../../../README.md)