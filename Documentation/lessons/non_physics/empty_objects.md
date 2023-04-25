##### Non-physics objects

# Empty objects

An empty object is a transform point attached to a [TDW object](../core_concepts/objects.md).  An empty object has a position and rotation. When the parent object moves or rotates, the empty object moves or rotates relative to the parent object. An empty object doesn't have a visual mesh, colliders, mass, etc. It won't respond to any physics events independent of its parent object's physics events. TDW objects may have any number of child empty objects.

In most cases, empty objects are meant to be handled in add-on internal code. For example [Replicants try to reach for objects at affordance points](../replicants/arm_articulation.md); these affordance points are actually empty objects that have been automatically added to the TDW objects using model record metadata.

## The `EmptyObjectManager` add-on

You can also add your own empty objects. Any time you need a point in space to continuously move and rotate relative to an object, you should use empty objects.

The best way to add empty objects and get their positions is by using an [`EmptyObjectManager`](../../python/add_ons/empty_object_manager.md). This add-on has an `empty_object_positions` parameter in the constructor in which you can set your empty object positions per object (in addition to the empty objects that TDW will automatically set from model record metadata). 

The positions of each empty object are stored in `empty_object_manager.empty_objects`, a dictionary. Key = Object ID. Value = A list of positions as numpy arrays. The `empty_objects` dictionary includes the empty objects you added via the `empty_object_positions` parameter plus any empty objects added automatically by TDW.

To reset `EmptyObjectManager` for a new scene, call: `empty_object_manager.reset(empty_object_positions)`.

This is a minimal example:

```python
from tdw.add_ons.empty_object_manager import EmptyObjectManager
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller()
object_id = 0
empty_object_manager = EmptyObjectManager(empty_object_positions={object_id: [{"x": 0, "y": 5, "z": 0}]})
c.add_ons.append(empty_object_manager)
c.communicate([TDWUtils.create_empty_room(12, 12),
               Controller.get_add_object(model_name="cube",
                                         object_id=object_id,
                                         library="models_flex.json",
                                         position={"x": 0, "y": 0.5, "z": 0},
                                         rotation={"x": 70, "y": 0, "z": 0})])
for i in range(10):
    c.communicate([])
    print(empty_object_manager.empty_objects[object_id][0])
c.communicate({"$type": "terminate"})
```

Output:

```
[0.        2.2071574 4.6984634]
[0.        2.2042146 4.6984634]
[0.        2.2002904 4.6984634]
[0.        2.1953855 4.6984634]
[0.        2.1894994 4.6984634]
[0.        2.1826324 4.6984634]
[1.2850297e-03 2.1690733e+00 4.7039351e+00]
[1.2141104e-03 2.1516466e+00 4.7120643e+00]
[7.0444454e-04 2.1317329e+00 4.7214184e+00]
[3.3666918e-04 2.1096809e+00 4.7316799e+00]
```

## Low-level description

`EmptyObjectManager` initializes by sending [`send_dynamic_static_objects`](../../api/command_api.md#send_static_objects) and [`send_dynamic_empty_objects`](../../api/command_api.md#send_dynamic_empty_objects). On the first `communicate()` call, the add-on receives [`StaticEmptyObjects`](../../api/output_data.md#StaticEmptyObjects). On every `communicate()` call, the add-on receives [`DynamicEmptyObjects`](../../api/output_data.md#DynamicEmptyObjects).

***

**This is the last document in the "Non-physics objects" tutorial.**

[Return to the README](../../../README.md)

***

Example controllers:

- [empty_objects.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/non_physics/empty_objects.py)  Add an empty object to a cube and print its position per communicate() call.

Python API:

- [`EmptyObjectManager`](../../python/add_ons/empty_object_manager.md)

Command API:

- [`send_dynamic_empty_objects`](../../api/command_api.md#send_dynamic_empty_objects)
- [`send_dynamic_static_objects`](../../api/command_api.md#send_static_objects)

Output Data:

- [`DynamicEmptyObjects`](../../api/output_data.md#DynamicEmptyObjects)
- [`StaticEmptyObjects`](../../api/output_data.md#StaticEmptyObjects)