

##### Scene Setup (High-Level APIs)

# Procedural object arrangements

In [`ProcGenKitchen`](proc_gen_kitchen.md), objects are grouped into pseudo-atomic "arrangements". Each arrangement is procedurally generated. For example, a single kitchen counter with objects on top of the counter and inside the cabinet is generated via a [`KitchenCounter`](../../python/proc_gen/arrangements/kitchen_counter.md) arrangement.

Arrangement data classes are similar to add-ons in that they accept parameters and generate commands, but they are meant to be used *within* an add-on in groups. In `ProcGenKitchen`, multiple kitchen counters, wall cabinets, etc. are placed alongside each other in the room.

This example adds a kitchen counter to the scene. Note that it relies on [room data](rooms.md) and other data classes. The position of the kitchen counter isn't explicitly set; it is set by setting a `distance` from `corner` along a `wall`.

```python
import numpy as np
from tdw.controller import Controller
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.proc_gen.arrangements.kitchen_counter import KitchenCounter
from tdw.proc_gen.arrangements.cabinetry.cabinetry import CABINETRY
from tdw.proc_gen.arrangements.cabinetry.cabinetry_type import CabinetryType
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from tdw.ordinal_direction import OrdinalDirection
from tdw.cardinal_direction import CardinalDirection
from tdw.librarian import SceneLibrarian

"""
Add a kitchen counter to the scene.
"""

# Get the scene name, record, and the region where the kitchen counter will be added.
scene_name = "mm_craftroom_2a"
scene_record = SceneLibrarian().get_record("mm_craftroom_2a")
region = scene_record.rooms[0].main_region
# Generate a kitchen counter.
kitchen_counter = KitchenCounter(cabinetry=CABINETRY[CabinetryType.beech_honey],
                                 corner=OrdinalDirection.northeast,
                                 wall=CardinalDirection.north,
                                 distance=0,
                                 region=region,
                                 rng=np.random.RandomState(3))
# Add a camera and enable image capture.
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("kitchen_counter")
print(f"Images will be saved to: {path}")
# Look at the root object (the kitchen counter).
camera = ThirdPersonCamera(position={"x": 0, "y": 1.8, "z": 0},
                           look_at=kitchen_counter.root_object_id,
                           avatar_id="a")
capture = ImageCapture(avatar_ids=["a"], path=path, pass_masks=["_img"])
# Start the controller.
c = Controller()
# Append the add-ons.
c.add_ons = [camera, capture]
# Add the scene.
commands = [Controller.get_add_scene(scene_name=scene_name)]
# Add the kitchen counter's commands.
commands.extend(kitchen_counter.get_commands())
c.communicate(commands)
c.communicate({"$type": "terminate"})
```

Result:

![](images/arrangements/kitchen_counter.jpg)

## Adjusting arrangement parameters

Each arrangement is a subclass of [`Arrangement`](../../python/proc_gen/arrangements/arrangement.md). Many arrangements are sub-classes of mid-level abstract classes. Arrangements therefore often share the same parameters.

Arrangement parameters can be adjusted in the constructor. In higher-level APIs such as `ProcGenKitchen`, the arrangement constructors are automatically called, meaning that you can't (and shouldn't) adjust constructor parameters.

In all cases, including `ProcGenKitchen`, you can adjust class variables. A good example of this is `Arrangement.MODEL_CATEGORIES`.

`Arrangement.MODEL_CATEGORIES` is a dictionary that has been curated from the overall list of models. The key of `Arrangement.MODEL_CATEGORIES` is a "proc-gen category", which overlaps with [`model_record.wcategory`](../../python/librarian/model_librarian.md) but is often not the same. For example, in TDW kitchen counters and wall cabinets have the same `wcategory` but not the same proc-gen category:

```python
from tdw.proc_gen.arrangements.arrangement import Arrangement
from tdw.librarian import ModelLibrarian

lib = ModelLibrarian()
model_names = ["cabinet_24_wall_wood_beech_honey_composite",
               "cabinet_24_single_door_wood_beech_honey_composite"]
for model_name in model_names:
    # Get the proc-gen category.
    for category in Arrangement.MODEL_CATEGORIES:
        if model_name in Arrangement.MODEL_CATEGORIES[category]:
            # Get the record.
            record = lib.get_record(model_name)
            print(category, record.wcategory)
```

Output:

```
wall_cabinet cabinet
kitchen_counter cabinet
```

To add a model from models_core.json, simply add it to the dictionary:

```python
from tdw.proc_gen.arrangements.arrangement import Arrangement

Arrangement.MODEL_CATEGORIES["knife"].append("knife1")
```

To force arrangements to only use one model in a given category, set the list accordingly:

```python
from tdw.proc_gen.arrangements.arrangement import Arrangement

Arrangement.MODEL_CATEGORIES["wall_cabinet"] = ["cabinet_24_wall_wood_beech_honey_composite"]
```



