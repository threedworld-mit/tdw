# Units and data types in TDW

## Units

- Distance is always in meters
- Rotations, angular velocities, etc. are always in degrees
- Velocity is always in meters per second
- Force is always in Newtons

## Positions

Positions are always in (x, y, z) coordinates. 

#### Input (Commands)

In the Command API, positions are always dictionaries:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller(launch_build=False)
c.start()
object_id = 0
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_object(model_name="iron_box",
                                object_id=object_id)])
c.communicate({"$type": "teleport_object",
               "id": object_id,
               "position": {"x": 0, "y": 0, "z": 2.5}})
```

#### Output (Output Data)

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Transforms

c = Controller(launch_build=False)
c.start()
object_id = 0
resp = c.communicate([TDWUtils.create_empty_room(12, 12),
                      c.get_add_object(model_name="iron_box",
                                       object_id=object_id),
                      {"$type": "send_transforms"}])
for i in range(len(resp) - 1):
    r_id = OutputData.get_data_type_id(resp[i])
    if r_id == "tran":
        tr = Transforms(resp[i])
        for j in range(tr.get_num()):
            x, y, z = tr.get_position(j)
```

#### Position vs. bounds

**The position of an object its bottom-center point, *not* its center.** This is because it's almost always more convenient to place objects in the scene if its pivot is at the bottom-center.

To get the center of the object, use `Bounds` data instead of `Transforms` data:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Transforms, Bounds

c = Controller(launch_build=False)
c.start()
object_id = 0
resp = c.communicate([TDWUtils.create_empty_room(12, 12),
                      c.get_add_object(model_name="iron_box",
                                       object_id=object_id),
                      {"$type": "send_transforms"},
                      {"$type": "send_bounds"}])
for i in range(len(resp) - 1):
    r_id = OutputData.get_data_type_id(resp[i])
    if r_id == "tran":
        tr = Transforms(resp[i])
        for j in range(tr.get_num()):
            print("Position at bottom-center: ", tr.get_position(j))
    elif r_id == "boun":
        bo = Bounds(resp[i])
        for j in range(bo.get_num()):
            print("Position at center: ", bo.get_center(j))
c.communicate({"$type": "terminate"})
```

## Rotations

Rotations are either in (x, y, z) Euler angles, (x, y, z) directional vectors, (x, y, z, w) quaternions, or an angle and an axis or rotation.

#### Input (Commands)

In the Command API, Euler angles, directional vectors, and quaternions are always dictionaries. Angle+axis rotations are always a float and a string (`"pitch"`, `"yaw"`, or `"roll"`).

Some rotation commands have a `use_centroid` parameter. By default, objects will rotate around their bottom-center pivot. If `use_centroid == True` objects will rotate around their true center.

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller(launch_build=False)
c.start()
object_id = 0

# Different ways to rotate an object:
# 1. Euler angles (the get_add_object() wrapper function)
# 2. A quaternion (rotate_object_to)
# 3. An angle + an axis (rotate_object_by)
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_object(model_name="iron_box",
                                object_id=object_id,
                                rotation={"x": 0, "y": 0, "z": 0}),
               {"$type": "rotate_object_to",
                "rotation": {"x": 3.5, "y": -5, "z": 0, "w": 0.1},
                "id": object_id,
                "use_centroid": True},
               {"$type": "rotate_object_by",
                "angle": 45,
                "id": object_id,
                "axis": "pitch",
                "use_centroid": True}])
```

#### Output (Output Data API)

In the Output Data API, directional vectors are return as (x, y, z) tuples. Rotations are always returned as (x, y, z, w) tuples, representing a quaternion:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Transforms

c = Controller(launch_build=False)
c.start()
object_id = 0
resp = c.communicate([TDWUtils.create_empty_room(12, 12),
                      c.get_add_object(model_name="iron_box",
                                       object_id=object_id,
                                       rotation={"x": 0, "y": 35, "z": 0}),
                      {"$type": "send_transforms"}])
for i in range(len(resp) - 1):
    r_id = OutputData.get_data_type_id(resp[i])
    if r_id == "tran":
        tr = Transforms(resp[i])
        for j in range(tr.get_num()):
            # The forward directional vector of the object.
            xf, yf, zf = tr.get_forward(j)
            # The rotation quaternion of the object.
            xr, yr, zr, wr = tr.get_rotation(j)
```

#### Euler angles

Euler angles are a useful and intuitive way to *initially* place objects. **Euler angles are *not* useful for subsequent rotations.** As soon as you rotate around any axis more than 180 degrees, it is possible to achieve [gimbal lock](https://www.youtube.com/watch?v=zc8b2Jo7mno). **Gimbal lock is unavoidable, and the resulting Euler angles won't be useful data.** TDW _never_ sends Euler angles as part of output data because it's impossible to guarantee that they'll be accurate or meaningful.

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller(launch_build=False)
c.start()
object_id = 0
# Set initial Euler angles for the object.
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_object(model_name="iron_box",
                                object_id=object_id,
                                rotation={"x": 0, "y": 35, "z": 0})])
```

#### Directional vectors

Directional vectors are useful for getting spatial positions but aren't useful for rotational math. This example sets a position 5 meters in front of the object along its forward directional vector:

```python
import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Transforms

c = Controller(launch_build=False)
c.start()
object_id = 0
resp = c.communicate([TDWUtils.create_empty_room(12, 12),
                      c.get_add_object(model_name="iron_box",
                                       object_id=object_id,
                                       rotation={"x": 0, "y": 35, "z": 0}),
                      {"$type": "send_transforms"}])
for i in range(len(resp) - 1):
    r_id = OutputData.get_data_type_id(resp[i])
    if r_id == "tran":
        tr = Transforms(resp[i])
        for j in range(tr.get_num()):
            # The forward directional vector of the object.
            forward = np.array(tr.get_forward(j))
            # The position of the object.
            position = np.array(tr.get_position(j))
            # A position 5 meters in front of the object.
            position_1 = position + (forward * 5)
```

### Quaternions

Quaternions are four-dimensional number systems with three real numbers and one imaginary number: https://www.youtube.com/watch?v=zjMuIxRvygQ

Quaternions are the only way to correctly express rotations. They are also very unintuitive! TDW includes [`QuaternionUtils`, a utility class for basic quaternion operations.](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/tdw_utils.md#quaternionutils)

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller(launch_build=False)
c.start()
object_id = 0
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_object(model_name="iron_box",
                                object_id=object_id),
               {"$type": "rotate_object_to",
                "rotation": {"x": 3.5, "y": -5, "z": 0, "w": 0.1},
                "id": object_id,
                "use_centroid": True}])
```

#### Angle + Axis

Some commands in TDW have angle and axis parameters. On the backend, these are converted into quaternions, but they can be a much more user-friendly means of rotating objects than inputting quaternions:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller(launch_build=False)
c.start()
object_id = 0
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_object(model_name="iron_box",
                                object_id=object_id),
               {"$type": "rotate_object_by",
                "angle": 45,
                "id": object_id,
                "axis": "pitch",
                "use_centroid": True}])
```

