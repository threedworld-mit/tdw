# Core concepts: Output Data

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

In this example, the controller creates a simple scene, requests [`Environments` output data](../../api/output_data.md#Environments) via the [`send_environments` command](../../api/command_api.md#send_environments), and prints the bounds of each environment in the scene. *Note: "environment" is an old idiom in TDW that gets rarely used now. In this case, each "room" in an interior scene is considered to be a rectangular "environment".*

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Environments
from tdw.add_ons.third_person_camera import ThirdPersonCamera

c = Controller()
c.start()

resp = c.communicate([TDWUtils.create_empty_room(12, 12),
                      {"$type": "send_environments"}])
for i in range(len(resp) - 1):
    # Get the output data ID.
    r_id = OutputData.get_data_type_id(resp[i])
    # This is environment output data.
    if r_id == "envi":
        environments = Environments(resp[i])
        # Print the bounds.
        for j in range(environments.get_num()):
            print(j, environments.get_bounds(j))
c.communicate({"$type": "terminate"})
```

Note that each "environment" isn't a separate object or stored in a convenient dictionary. Flatbuffer doesn't support nested serialization.

Also, note that we don't actually need an avatar in the scene to get `Environments` output data. The only data that requires an avatar in the scene is data actually captured by the avatar (such as `Images`).

## Per-frame output data

Suppose we want to drop an object, record its position as it falls, and end the simulation when it stops moving.

We already know how to set up the scene. Note that the object's `y` value is high above the floor level:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller()
c.start()
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
c.start()
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
c.start()
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

Now we will run the simulation in a loop. `c.communicate([])` means that the controller don't send any commands on this frame. Per frame, the controller will receive [`Transforms`](../../api/output_data.md#Transforms), which it will used to log the position of the object, and  [`Rigidbodies`](../../api/output_data.md#Rigidbodies), which it will use to determine if the object has stopped moving:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Transforms, Rigidbodies

c = Controller()
c.start()
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

***

**Next: [Images](images.md)**

Example controllers:

- [object_output_data.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/core_concepts/object_output_data.py) Receive object output data.

Command API:

- [`send_environments`](../../api/command_api.md#send_environments)
- [`send_transforms`](../../api/command_api.md#send_transforms)
- [`send_rigidbodies`](../../api/command_api.md#send_rigidbodies)

Output Data API:

- [`Environments`](../../api/output_data.md#Environments) 
- [`Transforms`](../../api/output_data.md#Transforms) 
- [`Rigidbodies`](../../api/output_data.md#Rigidbodies) 

[Return to the README](../../README.md)
