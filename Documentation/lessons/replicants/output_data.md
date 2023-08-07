##### Replicants

# Output Data

*For more information regarding TDW output data, [read this](../core_concepts/output_data.md).*

*For more information regarding TDW image output data, [read this](../core_concepts/images.md).*

The Replicant includes static data about the agent (such as body part IDs) and dynamic data (such as body part positions). 

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

- `dynamic.got_images` is a boolean that indicates whether there is image data.
- `dynamic.images` is a dictionary of image data. The key is the [pass mask as a string](../core_concepts/images.md). See below for more information:

## Images

Images, as noted above, are stored in `dynamic.images`. 

### Image frequency

**By default, images are captured at the end of every [action](actions.md).** If there is no image data, `dynamic.images` is an empty dictionary:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.replicant import Replicant
from tdw.replicant.action_status import ActionStatus

c = Controller()
replicant = Replicant()
c.add_ons.append(replicant)
c.communicate(TDWUtils.create_empty_room(12, 12))
# Walk forward 0.5 meters.
replicant.move_by(0.5)
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])
    # This will be an empty dictionary.
    print(replicant.dynamic.images.keys())
c.communicate([])
# This will print the image pass mask labels.
print(replicant.dynamic.images.keys())
c.communicate({"$type": "terminate"})
```

Output:

```
dict_keys([])
dict_keys([])
dict_keys([])
dict_keys([])
dict_keys([])
dict_keys([])
dict_keys([])
dict_keys([])
dict_keys([])
dict_keys([])
dict_keys([])
dict_keys(['img', 'id', 'depth'])
```

If you want to capture images on every `communicate()` call, or never capture images, set the `image_frequency` parameter in the Replicant constructor, which accepts an [`ImageFrequency`](../../python/replicant/image_frequency.md) value:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.replicant import Replicant
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.image_frequency import ImageFrequency

c = Controller()
# Request image data on every `communicate()` call.
replicant = Replicant(image_frequency=ImageFrequency.always)
c.add_ons.append(replicant)
c.communicate(TDWUtils.create_empty_room(12, 12))
replicant.move_by(0.5)
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])
    print(replicant.dynamic.images.keys())
c.communicate([])
print(replicant.dynamic.images.keys())
c.communicate({"$type": "terminate"})
```

Output:

```
dict_keys([])
dict_keys(['img', 'id', 'depth'])
dict_keys(['img', 'id', 'depth'])
dict_keys(['img', 'id', 'depth'])
dict_keys(['img', 'id', 'depth'])
dict_keys(['img', 'id', 'depth'])
dict_keys(['img', 'id', 'depth'])
dict_keys(['img', 'id', 'depth'])
dict_keys(['img', 'id', 'depth'])
dict_keys(['img', 'id', 'depth'])
dict_keys(['img', 'id', 'depth'])
dict_keys(['img', 'id', 'depth'])
```

### Save images

To save images, call `replicant.dynamic.save_images` after a `communicate()` call:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.replicant import Replicant
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.image_frequency import ImageFrequency
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("replicant_egocentric")
print(f"Images will be saved to: {path}")
c = Controller()
# Request image data on every `communicate()` call.
replicant = Replicant(image_frequency=ImageFrequency.always)
c.add_ons.append(replicant)
c.communicate(TDWUtils.create_empty_room(12, 12))
replicant.move_by(2)
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])
    # Save the images.
    replicant.dynamic.save_images(output_directory=path)
c.communicate([])
# Save the images.
replicant.dynamic.save_images(output_directory=path)
c.communicate({"$type": "terminate"})
```

Result:

![](images/output_data/move_by_egocentric.gif)

### Convert image to PIL images

To convert raw image data to PIL Image objects, call `replicant.get_pil_image(pass_mask)` where `pass_mask` is a string: `"img"`, `"id"`, or `"depth"`:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.replicant import Replicant
from tdw.replicant.action_status import ActionStatus


c = Controller()
r = Replicant()
c.add_ons.append(r)
c.communicate(TDWUtils.create_empty_room(12, 12))
while r.action.status == ActionStatus.ongoing:
    c.communicate([])
c.communicate({"$type": "terminate"})
r.dynamic.get_pil_image("img").show()
```

### `_depth` and `_id` passes

In addition to the the `_img` pass, the Replicant will capture `_id` and `_depth` passes. The `_id` pass is `dynamic.images["id"]` and the `_depth` pass is `dynamic.images["depth"]` (assuming that `dynamic.images` isn't empty). 

- [To learn more about the `_id` pass, read  this.](../visual_perception/id.md)
- [To learn more about the `_depth` pass, including how to interpret it as a point cloud, read this.](../visual_perception/depth.md)

## Low-level description

When the `Replicant` add-on initializes, it sends [`send_replicants`](../../api/command_api.md#send_replicants) in order to receive [`Replicants`](../../api/output_data.md#Replicants) output data per `communicate()` call. This data has been optimized for speed, not human usage; this one of many reasons that we recommend using the `Replicant` add-on instead of low-level TDW commands and output data. Both `ReplicantStatic` and `ReplicantDynamic` parse`Replicants` output data. 

Some [actions](actions.md) require additional output data. When the `Replicant` add-on initializes, it also sends [`send_transforms`](../../api/command_api.md#send_transforms), [`send_bounds`](../../api/command_api.md#send_bounds), and [`send_containment`](../../api/command_api.md#send_containment) to receive  [`Transforms`](../../api/output_data.md#Transforms),  [`Bounds`](../../api/output_data.md#Bounds), and  [`Containment`](../../api/output_data.md#Containment) respectively per `communicate()` call.

The `Replicant`'s `static` and `dynamic` data are initially `None`. Both are set *after* the first `communicate()` call (because the Replicant needs one `communicate()` call to start requesting output data).

On the *second* `communicate()` call (i.e. one call after initialization), the `Replicant` add-on sends [`create_avatar`](../../api/command_api.md#create_avatar) and [`parent_avatar_to_replicant`](../../api/command_api.md#parent_avatar_to_replicant) to attach an [avatar (camera)](../core_concepts/avatars.md) to its head. This is how it receives image data.

The `Replicant` sends [`send_images`](../../api/command_api.md#send_images) and [`send_camera_matrices`](../../api/command_api.md#send_camera_matrices) to receive [`Images`](../../api/output_data.md#Images) and [`CameraMatrices`](../../api/output_data.md#CameraMatrices) output data, respectively. The frequency at which this data is sent depends on the value of the `image_frequency` value in the constructor. By default, these commands are only sent when an action ends; accordingly, they are actually passed from the `action`, to the `Replicant`, to the controller.

***

**Next: [Collision detection](collision_detection.md)**

[Return to the README](../../../README.md)

***

Example controllers:

- [egocentric_images.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/replicant/egocentric_images.py) Capture image data from the Replicant per `communicate()` call and save it to disk.

Command API:

- [`send_replicants`](../../api/command_api.md#send_replicants)
- [`send_transforms`](../../api/command_api.md#send_transforms)
- [`send_bounds`](../../api/command_api.md#send_bounds)
- [`send_containment`](../../api/command_api.md#send_containment)
- [`create_avatar`](../../api/command_api.md#create_avatar)
- [`parent_avatar_to_replicant`](../../api/command_api.md#parent_avatar_to_replicant)
- [`send_images`](../../api/command_api.md#send_images)
- [`send_camera_matrices`](../../api/command_api.md#send_camera_matrices)

Output Data API:

- [`Replicants`](../../api/output_data.md#Replicants)
- [`Transforms`](../../api/output_data.md#Transforms)
- [`Bounds`](../../api/output_data.md#Bounds)
- [`Containment`](../../api/output_data.md#Containment)
- [`Images`](../../api/output_data.md#Images)
- [`CameraMatrices`](../../api/output_data.md#CameraMatrices)

Python API:

- [`Replicant`](../../python/add_ons/replicant.md)
- [`ReplicantStatic`](../../python/replicant/replicant_static.md)
- [`ReplicantDynamic`](../../python/replicant/replicant_dynamic.md)
- [`Arm`](../../python/replicant/arm.md)
- [`ReplicantBodyPart`](../../python/replicant/replicant_body_part.md)
- [`ImageFrequency`](../../python/replicant/image_frequency.md)
- [`Transform`](../../python/object_data/transform.md)
