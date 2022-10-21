##### Replicants

# Output Data

*For more information regarding TDW output data, [read this](../core_concepts/output_data.md).*

*For more information regarding TDW image output data, [read this](../core_concepts/images.md).*

The Replicant  includes static data about the agent (such as body part IDs) and dynamic data (such as body part positions). 

## Static Replicant Data

Static Replicant data is stored in `replicant.static`. This is a [`ReplicantStatic` object](../../python/replicant/replicant_static.md).

In addition to the replicant's ID (`static.replicant_id`), each body part has a separate ID.

- `static.body_parts` is a dictionary. The key is a [`ReplicantBodyPart`](../../python/replicant/replicant_body_part.md) enum value. The value is the body part ID:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.replicant import Replicant
from tdw.replicant.replicant_body_part import ReplicantBodyPart

c = Controller()
replicant = Replicant()
c.add_ons.append(replicant)
c.communicate(TDWUtils.create_empty_room(12, 12))
# Print the ID of the Replicant's left hand.
print(replicant.static.body_parts[ReplicantBodyPart.hand_l])
c.communicate({"$type": "terminate"})
```

- `static.body_parts_by_id` is the reciprocal dictionary: the key is the body part ID and the value is a [`ReplicantBodyPart`](../../python/replicant/replicant_body_part.md) enum value.

- Internally, the Replicant often needs to refer to each hand quickly. For ease of use, the static data includes `static.hands`, a dictionary with the key is an [`Arm`](../../python/replicant/arm.md) enum value and the value is an ID of a hand:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.replicant import Replicant
from tdw.replicant.arm import Arm

c = Controller()
replicant = Replicant()
c.add_ons.append(replicant)
c.communicate(TDWUtils.create_empty_room(12, 12))
# Print the ID of the Replicant's left hand.
print(replicant.static.hands[Arm.left])
c.communicate({"$type": "terminate"})
```

-  `static.avatar_id` is the ID of the Replicant's avatar (camera). This is always the string-ified version of `replicant_id`. If `replicant_id` is `0` then `avatar_id` is `"0"`.

## Dynamic Replicant Data

Dynamic Replicant data is stored in `self.replicant.dynamic`. This is a [`ReplicantDynamic` object](../../python/replicant/replicant_dynamic.md). It is updated every `communicate()` call.

- `dynamic.transform` is the [`Transform`](../../python/object_data/transform.md) (position, rotation, and forward) of the Replicant. This prints the position of the Replicant:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.replicant import Replicant

c = Controller()
replicant = Replicant()
c.add_ons.append(replicant)
c.communicate(TDWUtils.create_empty_room(12, 12))
print(replicant.dynamic.transform.position)
c.communicate({"$type": "terminate"})
```

Output:

```
[0. 0. 0.]
```

- `dynamic.body_parts` is a dictionary. The key is a body part ID. The value is a [`Transform`](../../python/object_data/transform.md). This example prints the position of the Replicant's left hand. Note that we use the `static` data to get the hand's ID.

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.replicant import Replicant
from tdw.replicant.arm import Arm

c = Controller()
replicant = Replicant()
c.add_ons.append(replicant)
c.communicate(TDWUtils.create_empty_room(12, 12))
hand_id = replicant.static.hands[Arm.left]
print(replicant.dynamic.body_parts[hand_id].position)
c.communicate({"$type": "terminate"})
```

- `dynamic.held_objects` records whether an object is held in each hand and if so what the object's ID is. The key is an [`Arm`](../../python/replicant/arm.md) enum value and the value is an ID of an object. If the hand isn't holding an object, the key won't be in the dictionary:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.replicant import Replicant
from tdw.replicant.arm import Arm

c = Controller()
replicant = Replicant()
c.add_ons.append(replicant)
c.communicate(TDWUtils.create_empty_room(12, 12))
hand = Arm.left
# Is the left hand holding an object?
if hand in replicant.dynamic.held_objects:
    # This is the object being held.
    object_id = replicant.dynamic.held_objects[hand]
    print(object_id)
```

- `dynamic.projection_matrix` and `dynamic.camera_matrix` are numpy arrays of the camera matrices.
- `dynamic.collisions` is a dictionary. The key is a body part ID. The value is a list of object IDs that the body part collided with. This example checks whether the lower left arm is colliding with any objects:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.replicant import Replicant
from tdw.replicant.replicant_body_part import ReplicantBodyPart

c = Controller()
replicant = Replicant()
c.add_ons.append(replicant)
c.communicate(TDWUtils.create_empty_room(12, 12))
body_part_id = replicant.static.body_parts[ReplicantBodyPart.lowerarm_l]
# Is the lower left arm colliding with any objects?
object_ids = replicant.dynamic.collisions[body_part_id]
print(len(object_ids) > 0)
c.communicate({"$type": "terminate"})
```

Output:

```
False
```

### Images

By default, a Replicant captures images at the end of every [action](actions.md).

- `dynamic.got_images` is a boolean that indicates whether there is image data.
- `dynamic.images` is a dictionary of image data. The key is the [pass mask as a string](../core_concepts/images.md). The Replicant always captures `_img`, [`_id`](../visual_perception/id.md), and [`_depth`](../visual_perception/depth.md) images.

