

##### Scene Setup (High-Level APIs)

# Procedural object arrangements

In [`ProcGenKitchen`](proc_gen_kitchen.md), objects are grouped into pseudo-atomic "arrangements". Each arrangement is procedurally generated. For example, a single kitchen counter with objects on top of the counter and inside the cabinet is generated via a [`KitchenCounter`](../../python/proc_gen/arrangements/kitchen_counter.md) arrangement.

Arrangement data classes are similar to add-ons in that they accept parameters and generate commands, but they are meant to be used *within* an add-on in groups. In `ProcGenKitchen`, multiple kitchen counters, wall cabinets, etc. are placed alongside each other in the room.

Arrangements are procedurally generated. The models used are randomly selected from pre-categorized lists. Object positions, rotations, etc. are also randomized within various constraints.

## `Arrangement` class hierarchy

Arrangements are all data objects. Every type of arrangement is a subclass of [`Arrangement`](../../python/proc_gen/arrangements/arrangement.md). Some arrangement types may have intermediary abstract subclasses such as [`ArrangementWithRootObject`](../../python/proc_gen/arrangements/arrangement_with_root_object.md).

There are many `Arrangement` sub-classes; see the bottom of this document for a list. As adding example controller code to this document for every `Arrangement` would be so verbose as to make this document unreadable, only a few notable examples would be shown. For others, you should read the API documentation.

### Example A: `CupAndCoaster`

A [`CupAndCoaster`](../../python/proc_gen/arrangements/cup_and_coaster.md) is a relatively simple arrangement. It creates either a cup or a wine glass. 50% of the time, there is a coaster under the cup or glass.

`CupAndCoaster` has the following constructor parameters:

- `position` sets the position of the arrangement (either the coaster or, if there is no coaster, the cup or wineglass).
- `rng` is optional and defaults to None. It is either a random seed (and integer) or a `numpy.random.RandomState` object. If None, a new `numpy.random.RandomState` object is created.

To add a `CupAndCoaster` to the scene:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.image_capture import ImageCapture
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.proc_gen.arrangements.cup_and_coaster import CupAndCoaster
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Create a cup and coaster.
"""

# Add a camera and enable image capture.
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("cup_and_coaster")
print(f"Images will be saved to: {path}")
camera = ThirdPersonCamera(position={"x": -1.5, "y": 0.8, "z": 0},
                           look_at={"x": 0, "y": 0, "z": 0},
                           avatar_id="a")
capture = ImageCapture(avatar_ids=["a"], path=path, pass_masks=["_img"])
# Start the controller.
c = Controller()
c.add_ons.extend([camera, capture])
# Add a `CupAndCoaster` arrangement.
cup_and_coaster = CupAndCoaster(position={"x": 0, "y": 0, "z": 0},
                                rng=0)
# Create the scene.
commands = [TDWUtils.create_empty_room(12, 12)]
# Add commands to create the cup and coaster.
commands.extend(cup_and_coaster.get_commands())
# Send the commands.
c.communicate(commands)
c.communicate({"$type": "terminate"})
```

Result:

![](images/arrangements/cup_and_coaster.jpg)

### Example B: `KitchenCounter`

[`KitchenCounter`](../../python/proc_gen/arrangements/kitchen_counter.md) is in some key ways structured very differently than `CupAndCoaster`. The constructor doesn't accept an explicit position. Instead, a `KitchenCounter` is positioned in relationship to the room: a `distance` from a `corner` along a `wall`. It is a subclass of [`ArrangementAlongWall`](../../python/proc_gen/arrangements/arrangement_along_wall.md) and relies on [room data](rooms.md) and other data classes.

`KitchenCounter` has the following constructor parameters (note that `position` is *not* a parameter):

- `cabinetry` defines the cabinetry set; this is used to make all kitchen cabinets, sinks, etc. in the scene look like they're part of the same set. `cabinetry` is of type [`Cabinetry`](../../python/proc_gen/arrangements/cabinetry/cabinetry.md). There are two pre-defined `Cabinetry` sets; see `tdw.proc_gen.arrangements.cabinetry.cabinetry.CABINETRY`, a dictionary where the key is a  [`CabinetryType`](../../python/proc_gen/arrangements/cabinetry/cabinetry_type.md) and the value is a pre-set [`Cabinetry`](../../python/proc_gen/arrangements/cabinetry/cabinetry.md).
- `wall` is a [`CardinalDirection`](../../python/cardinal_direction.md) value describing the location of the wall that the `KitchenCounter` abuts.
- `corner` is an [`OrdinalDirection`](../../python/ordinal_direction.md) value describing the "starting corner" (this conceptually assumes that there are multiple kitchen counters, sinks, etc. along the wall, starting from `corner`). The value of `corner` must correspond to the value of `wall`;  for example, if `wall == CardinalDirection.north`, then the two valid values for `corner` are `OrdinalDirection.northwest` and `OrdinalDirection.northeast`.
- `distance` is a float describing the kitchen counter's distance from the `corner` along the `wall`.
- `region` is the [`InteriorRegion`](../../python/scene_data/interior_region.md) that the wall, corner, and kitchen counter are located in. [Read this for more information.](rooms.md) In most cases, you can set this to `scene_record.rooms[0].main_region` (assuming that you've already defined `scene_record`).
- `allow_microwave` is a boolean. If True, the kitchen counter may have a microwave. This can be useful for controlling the total number of microwaves in a scene. It is optional and defaults to True.
- `microwave_plate` is a float defining the probability of there being a [`Plate`](../../python/proc_gen/arrangements/plate.md) inside the microwave (if there is a microwave). It is optional and defaults to 0.7.
- `empty` is a float defining the probability of the kitchen cabinet being empty. It is optional and defaults to 0.1
- `model` is either a string (the name of a model) or a `ModelRecord`. This is the root kitchen counter model.
- `wall_length` is the length of the wall. If None, it defaults to the actual length of the wall. This can be useful if you want to start calculating the `distance` at an offset.
- `rng` is optional and defaults to None. It is either a random seed (and integer) or a `numpy.random.RandomState` object. If None, a new `numpy.random.RandomState` object is created.

This example adds a kitchen counter to the scene:

```python
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
                                 rng=3)
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

## `Arrangement` parameters and `ProcGenKitchen`

By design, `ProcGenKitchen` hides and automates most of the parameters of its constituent `Arrangements`. `ProcGenKitchen` positions arrangements such that they appear kitchen-like; as such, only a fairly narrow range of preset parameter values will be valid.

## Class variables and `MODEL_CATEGORIES`

It is possible to adjust the class variables of any of the `Arrangement` classes; refer to the API documentation for a list.

One class variable that is likely to be adjusted more than most is `Arrangement.MODEL_CATEGORIES`, a dictionary that has been curated from the overall list of models. The key of `Arrangement.MODEL_CATEGORIES` is a "proc-gen category", which overlaps with [`model_record.wcategory`](../../python/librarian/model_librarian.md) but is often not the same. For example, in TDW kitchen counters and wall cabinets have the same `wcategory` but not the same proc-gen category:

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

***

**Next: [Scripted object placement (floorplan layouts)](floorplans.md)**

[Return to the README](../../../README.md)

***

Example Controllers:

- [cup_and_coaster.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/scene_setup_high_level/cup_and_coaster.py) Create a cup and coaster.
- [kitchen_counter.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/scene_setup_high_level/kitchen_counter.py) Create a kitchen counter arrangement.

Python API:

- Add-ons:
  - [`ProcGenKitchen`](../../python/add_ons/proc_gen_kitchen.md)
- Arrangements:
  - [`Arrangement`](../../python/proc_gen/arrangements/arrangement.md)
  - [`ArrangementAlongWall`](../../python/proc_gen/arrangements/arrangement_along_wall.md)
  - [`ArrangementWithRootObject`](../../python/proc_gen/arrangements/arrangement_with_root_object.md)
  - [`Basket`](../../python/proc_gen/arrangements/basket.md)
  - [`CupAndCoaster`](../../python/proc_gen/arrangements/cup_and_coaster.md)
  - [`Dishwasher`](../../python/proc_gen/arrangements/dishwasher.md)
  - [`KitchenCabinet`](../../python/proc_gen/arrangements/kitchen_cabinet.md)
  - [`KitchenCounter`](../../python/proc_gen/arrangements/kitchen_counter.md)
  - [`KitchenCounterTop`](../../python/proc_gen/arrangements/kitchen_counter_top.md)
  - [`KitchenTable`](../../python/proc_gen/arrangements/kitchen_table.md)
  - [`Microwave`](../../python/proc_gen/arrangements/microwave.md)
  - [`Painting`](../../python/proc_gen/arrangements/painting.md)
  - [`Plate`](../../python/proc_gen/arrangements/plate.md)
  - [`Radiator`](../../python/proc_gen/arrangements/radiator.md)
  - [`Refrigerator`](../../python/proc_gen/arrangements/refrigerator.md)
  - [`Shelf`](../../python/proc_gen/arrangements/shelf.md)
  - [`SideTable`](../../python/proc_gen/arrangements/side_table.md)
  - [`Sink`](../../python/proc_gen/arrangements/sink.md)
  - [`StackOfPlates`](../../python/proc_gen/arrangements/stack_of_plates.md)
  - [`Stool`](../../python/proc_gen/arrangements/stool.md)
  - [`Stove`](../../python/proc_gen/arrangements/stove.md)
  - [`Suitcase`](../../python/proc_gen/arrangements/suitcase.md)
  - [`TableAndChairs`](../../python/proc_gen/arrangements/table_and_chairs.md)
  - [`TableSetting`](../../python/proc_gen/arrangements/table_setting.md)
  - [`Void`](../../python/proc_gen/arrangements/void.md)
  - [`WallCabinet`](../../python/proc_gen/arrangements/wall_cabinet.md)
- Cabinetry:
  - [`Cabinetry`](../../python/proc_gen/arrangements/cabinetrycabinetry.md)
  - [`CabinetryType`](../../python/proc_gen/arrangements/cabinetrycabinetry_type.md)
- Directions:
  - [`CardinalDirection`](../../python/cardinal_direction.md)
  - [`OrdinalDirection`](../../python/ordinal_direction.md)
- Scene Data:
  - [`InteriorRegion`](../../python/scene_data/interior_region.md)