# ObjectManager

`from tdw.add_ons.object_manager import ObjectManager`

A simple manager class for objects in the scene. This add-on can cache static object data (name, ID, etc.) and record dynamic data (position, velocity, etc.) per frame.

## Usages constraints:

- This add-on assumes that this is a PhysX simulation, as opposed to a simulation with physics disabled or a Flex simulation.
- This add-on will record data for *all* objects in the scene. If you only need data for specific objects, you should use low-level TDW commands.
- By default, this add-on will record [transform data](../object_data/transform.md) but not [rigidbody data](../object_data/rigidbody.md) or [bounds data](../object_data/bound.md). You can set which data the add-on will record in the constructor, but be aware that this can slow down the simulation.

## Example usage

```python
import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.librarian import ModelLibrarian
from tdw.add_ons.object_manager import ObjectManager


c = Controller()
c.model_librarian = ModelLibrarian("models_special.json")
# Create the object manager.
om = ObjectManager()
c.add_ons.append(om)
commands = [TDWUtils.create_empty_room(100, 100)]
# The starting height of the objects.
y = 10
# The radius of the circle of objects.
r = 7.0
# Get all points within the circle defined by the radius.
p0 = np.array((0, 0))
o_id = 0
for x in np.arange(-r, r, 1):
    for z in np.arange(-r, r, 1):
        p1 = np.array((x, z))
        dist = np.linalg.norm(p0 - p1)
        if dist < r:
            commands.extend([c.get_add_object("prim_cone",
                                              object_id=o_id,
                                              position={"x": x, "y": y, "z": z},
                                              rotation={"x": 0, "y": 0, "z": 180})])
            o_id += 1
pass
c.communicate(commands)
for i in range(1000):
    for object_id in om.transforms:
        print(object_id, om.transforms[object_id].position)
    c.communicate([])
c.communicate({"$type": "terminate"})
```

***

## Fields

- `objects_static` [The static object data.](../object_data/object_static.md) Key = The ID of the object.

- `categories` The segmentation color per category as use in the _category image pass. Key = The category. Value = The color as an `[r, g, b]` numpy array.

- `transforms` The [transform data](../object_data/transform.md) for each object on the scene on this frame. Key = The object ID. If `transforms=False` in the constructor, this dictionary will be empty.

- `rigidbodies` The [rigidbody data](../object_data/rigidbody.md) for each rigidbody object on the scene on this frame. Key = The object ID. If `rigidbodies=False` in the constructor, this dictionary will be empty.

- `bounds` The [bounds data](../object_data/bound.md) for each object on the scene on this frame. Key = The object ID. If `bounds=False` in the constructor, this dictionary will be empty.

- `commands` These commands will be appended to the commands of the next `communicate()` call.

- `initialized` If True, this module has been initialized.

***

## Functions

#### \_\_init\_\_

**`ObjectManager()`**

**`ObjectManager(transforms=True, rigidbodies=False, bounds=False)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| transforms |  bool  | True | If True, record the [transform data](../object_data/transform.md) of each object in the scene. |
| rigidbodies |  bool  | False | If True, record the [rigidbody data](../object_data/rigidbody.md) of each rigidbody object in the scene. |
| bounds |  bool  | False | If True, record the [bounds data](../object_data/bound.md) of each object in the scene. |

#### get_initialization_commands

**`self.get_initialization_commands()`**

This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

_Returns:_  A list of commands that will initialize this add-on.

#### on_send

**`self.on_send(resp)`**

This is called after commands are sent to the build and a response is received.

Use this function to send commands to the build on the next frame, given the `resp` response.
Any commands in the `self.commands` list will be sent on the next frame.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| resp |  List[bytes] |  | The response from the build. |

#### before_send

**`self.before_send(commands)`**

This is called before sending commands to the build. By default, this function doesn't do anything.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| commands |  List[dict] |  | The commands that are about to be sent to the build. |

#### reset

**`self.reset()`**

Reset the cached static data. Call this when resetting the scene.