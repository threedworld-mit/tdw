##### Embodied Avatars

# Overview

*Embodied avatars in TDW is handled via the PhysX physics engine. If you haven't done so already, we strongly recommend you read the [physics tutorial](../physx/overview.md).*

**Embodied avatars** are [avatars](../core_concepts/avatars.md) with bodies that can physically interact with the scene.

Most of the time, when you create an avatar or [`ThirdPersonCamera`](../core_concepts/add_ons.md), you create an avatar of type `"A_Caps_Kinematic"`.

This:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera

c = Controller()
camera = ThirdPersonCamera(avatar_id="a")
c.add_ons.append(camera)
c.communicate(TDWUtils.create_empty_room(12, 12))
```

...does the exact same thing as this:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller()
c.communicate([TDWUtils.create_empty_room(12, 12),
               {"$type": "create_avatar",
                "type": "A_Img_Caps_Kinematic",
                "id": "a"}])
```

All other types of avatars are embodied avatars. 

**In general, we don't recommend you use embodied avatars.** Embodied avatars can be useful for prototyping but in general they're either obsolete or less sophisticated than other agents or both. Avatars are one of the oldest components of TDW and they've been gradually superseded.

The following avatar types *won't* be covered in this tutorial because they are obsolete. They exist in TDW only for the sake of maintaining support for old projects:

- `"A_Img_Caps"`
- `"A_Nav_Mesh"`
- `"A_StickyMitten_Adult"`
- `"A_StickyMitten_Baby"`



***

**Next: [The `EmbodiedAvatar`](embodied_avatar.md)**

[Return to the README](../../../README.md)

***

Python API:

- [`ThirdPersonCamera`](../../python/add_ons/third_person_camera.md)

Command API:

- [`create_avatar`](../../api/command_api.md#create_avatar)



