##### Core Concepts

# Output data

So far we've covered how to send **commands** to the build. This document covers how to receive **output data** from the build.

`Controller.communicate()` always returns a list of byte arrays sent by the build at the end of the frame. By default, this list has only one element: the frame number.

```python
from tdw.controller import Controller

c = Controller()
resp = c.communicate({"$type": "do_nothing"})

print(resp)  # [b'\x00\x00\x00\x02']
print(c.get_frame(resp[0]))  # 2

c.communicate({"$type": "terminate"})
```

The controller must explicitly request each type of output data from the build. This way, the controller can run efficiently because it isn't forced to receive data it doesn't need.

Unlike commands, which are serialized JSON dictionaries that get converted to C# classes in the build, output data is always serialized Flatbuffer byte arrays. The main difference is that output isn't a dictionary and can't be read as such. The output data byte arrays are deserialized into Python classes.

Each output data byte array has a four-byte string identifier. Use this identifier to determine how to deserialize the output data.

In this example, the controller creates a simple scene, requests [`SceneRegions` output data](../../api/output_data.md#SceneRegions) via the [`send_scene_regions` command](../../api/command_api.md#send_scene_regions), and prints the bounds of each region in the scene (a region is a rectangular space in a scene; in interior scenes, they usually correspond to rooms).

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, SceneRegions
from tdw.add_ons.third_person_camera import ThirdPersonCamera

c = Controller()

resp = c.communicate([TDWUtils.create_empty_room(12, 12),
                      {"$type": "send_scene_regions"}])
for i in range(len(resp) - 1):
    # Get the output data ID.
    r_id = OutputData.get_data_type_id(resp[i])
    # This is scene regions output data.
    if r_id == "sreg":
        scene_regions = SceneRegions(resp[i])
        # Print the bounds.
        for j in range(scene_regions.get_num()):
            print(j, scene_regions.get_bounds(j))
c.communicate({"$type": "terminate"})
```

Note that each "region" isn't a separate object or stored in a convenient dictionary. Flatbuffer doesn't support nested serialization.

Also, note that we don't actually need an avatar in the scene to get `SceneRegions` output data. The only data that requires an avatar in the scene is data actually captured by the avatar (such as `Images`).

## Per-frame output data

Suppose we want to drop an object, record its position as it falls, and end the simulation when it stops moving.

We already know how to set up the scene. Note that the object's `y` value is high above the floor level:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller()
object_id = c.get_unique_id()
commands = [TDWUtils.create_empty_room(12, 12),
            c.get_add_object(model_name="iron_box",
                             position={"x": 0, "y": 6, "z": 0},
                             rotation={"x": 25, "y": 38, "z": -10},
                             object_id=object_id)]
```

To record the position of the object per-frame, send the [`send_transforms` command](../../api/command_api.md#send_transforms). The `"frequency"` parameter can be set to `"once"` (receive data only on this frame), `"always"` (receive data per frame), and `"never"` (stop receiving data). The `"ids"` parameter is optional. If you don't include it, you'll receive data for *all* objects in the scene.

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller()
object_id = c.get_unique_id()
commands = [TDWUtils.create_empty_room(12, 12),
            c.get_add_object(model_name="iron_box",
                             position={"x": 0, "y": 6, "z": 0},
                             rotation={"x": 25, "y": 38, "z": -10},
                             object_id=object_id),
            {"$type": "send_transforms",
             "frequency": "always",
             "ids": [object_id]}]
```

To determine if the object has stopped moving, we'll also need to send  [`send_rigidbodies`](../../api/command_api.md#send_rigidbodies):

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller()
object_id = c.get_unique_id()
commands = [TDWUtils.create_empty_room(12, 12),
            c.get_add_object(model_name="iron_box",
                             position={"x": 0, "y": 6, "z": 0},
                             rotation={"x": 25, "y": 38, "z": -10},
                             object_id=object_id),
            {"$type": "send_transforms",
             "frequency": "always",
             "ids": [object_id]},
            {"$type": "send_rigidbodies",
             "frequency": "always",
             "ids": [object_id]}]
```

Now we will run the simulation in a loop. Per frame, the controller will receive [`Transforms`](../../api/output_data.md#Transforms), which it will used to log the position of the object, and  [`Rigidbodies`](../../api/output_data.md#Rigidbodies), which it will use to determine if the object has stopped moving:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Transforms, Rigidbodies

c = Controller()
object_id = c.get_unique_id()
commands = [TDWUtils.create_empty_room(12, 12),
            c.get_add_object(model_name="iron_box",
                             position={"x": 0, "y": 6, "z": 0},
                             rotation={"x": 25, "y": 38, "z": -10},
                             object_id=object_id),
            {"$type": "send_transforms",
             "frequency": "always",
             "ids": [object_id]},
            {"$type": "send_rigidbodies",
             "frequency": "always",
             "ids": [object_id]}]

# Send the commands.
resp = c.communicate(commands)

# The position of the object per frame.
positions = []
# If True, the object has stopped moving.
sleeping = False

# Wait for the object to stop moving.
while not sleeping:
    for i in range(len(resp) - 1):
        # Get the output data ID.
        r_id = OutputData.get_data_type_id(resp[i])
        # This is transforms output data.
        if r_id == "tran":
            transforms = Transforms(resp[i])
            for j in range(transforms.get_num()):
                if transforms.get_id(j) == object_id:
                    # Log the position.
                    positions.append(transforms.get_position(j))
        elif r_id == "rigi":
            rigidbodies = Rigidbodies(resp[i])
            for j in range(rigidbodies.get_num()):
                if rigidbodies.get_id(j) == object_id:
                    # Check if the object is sleeping.
                    sleeping = rigidbodies.get_sleeping(j)
    # Advance another frame and continue the loop.
    if not sleeping:
        resp = c.communicate([])
print(positions)
c.communicate({"$type": "terminate"})
```

## The `ObjectManager` add-on

TDW includes an [`ObjectManager` add-on](../../python/add_ons/object_manager.md) that reorganizes static and per-frame object output data. The trade-off is that `ObjectManager` is less flexible than managing this data yourself; it can only return object data for *every* object in the scene and can only do so *always* or *never*. Note that it can optionally include [`Bounds`](../../api/output_data.md#Bounds) output data.

This example does nearly the same thing as the previous example:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.object_manager import ObjectManager

c = Controller()
om = ObjectManager(transforms=True, rigidbodies=True, bounds=False)
c.add_ons.append(om)

# Send the commands.
resp = c.communicate([TDWUtils.create_empty_room(12, 12),
                      c.get_add_object(model_name="iron_box",
                                       position={"x": 0, "y": 6, "z": 0},
                                       rotation={"x": 25, "y": 38, "z": -10},
                                       object_id=c.get_unique_id())])

# Print the name and category of each object.
for object_id in om.objects_static:
    print(object_id, om.objects_static[object_id].name, om.objects_static[object_id].category)

# Run the simulation until all objects stop moving.
positions = dict()
sleeping = False
while not sleeping:
    sleeping = True
    for object_id in om.rigidbodies:
        if not om.rigidbodies[object_id].sleeping:
            sleeping = False
    # Remember the position
    for object_id in om.transforms:
        if object_id not in positions:
            positions[object_id] = list()
        positions[object_id].append(om.transforms[object_id].position)
    # Advance once frame.
    c.communicate([])
print(positions)
c.communicate({"$type": "terminate"})
```

## Other output data

This document covers only a fraction of the possible output data available in TDW. The next document will explain image output data.

**[Read the Output Data API documentation here.](../../api/output_data.md)**

***

**Next: [Images](images.md)**

[Return to the README](../../../README.md)

***

Example controllers:

- [object_output_data.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/core_concepts/object_output_data.py) Receive object output data.
- [object_manager.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/core_concepts/object_manager.py) Example implementation of an `ObjectManager`.

Python API:

- [`ObjectManager`](../../python/add_ons/object_manager.md)

Command API:

- [`send_scene_regions`](../../api/command_api.md#send_scene_regions)
- [`send_transforms`](../../api/command_api.md#send_transforms)
- [`send_rigidbodies`](../../api/command_api.md#send_rigidbodies)
- [`send_bounds`](../../api/command_api.md#send_bounds)

Output Data API:

- [`SceneRegions`](../../api/output_data.md#SceneRegions) 
- [`Transforms`](../../api/output_data.md#Transforms) 
- [`Rigidbodies`](../../api/output_data.md#Rigidbodies) 
- [`Bounds`](../../api/output_data.md#Bounds) 
