# Humanoids

Humanoids are photorealistic 3D character models (male and female) in both business and casual attire. They are fully "rigged", i.e. they have skeletons and can be driven by motion-capture animations.

For a list of humanoids, see the records in the [Humanoid Librarian](../python/librarian/humanoid_librarian.md):

```python
from tdw.librarian import HumanoidLibrarian

lib = HumanoidLibrarian()
for record in lib.records:
    print(record.name)
```

Output:

```
man_casual_1
man_suit
woman_business_1
woman_business_2
woman_casual_1
```

To fetch a specific record:

```python
from tdw.librarian import HumanoidLibrarian

lib = HumanoidLibrarian()
record = lib.get_record("man_casual_1")
```

For a list of animations, see the records in the [Humanoid Animation Librarian](../python/librarian/humanoid_animation_librarian.md):

```python
from tdw.librarian import HumanoidAnimationLibrarian

lib = HumanoidAnimationLibrarian()
for record in lib.records:
    print(record.name)
```

To fetch a specific record:

```python
from tdw.librarian import HumanoidLibrarian

lib = HumanoidLibrarian()
record = lib.get_record("man_casual_1")
```

There are additional animations extracted from [SMPL](https://smpl.is.tue.mpg.de/downloads) in a separate librarian that can be used by any humanoid:

```python
from tdw.librarian import HumanoidAnimationLibrarian

lib = HumanoidAnimationLibrarian("smpl_animations.json")
for record in lib.records:
    print(record.name)
```

For an example controller, see `animate_humanoid.py`.

## How to add animations and humanoids

- Add a humanoid with [`add_humanoid`](../api/command_api.md#add_humanoid) or `Controller.get_add_humanoid()`
- Add an animation with [`add_humanoid_animation`]((../api/command_api.md#add_humanoid_animation)). This will add and cache the animation into memory, but not play it. Alternatively, you can call `Controller.get_add_humanoid_animation()`. Unlike most `get_add` wrapper functions, this one returns a command *and* a record; you can use the record to get the total number of frames of the animation.
- To play an animation, first send [`play_humanoid_animation`](../api/command_api.md#play_humanoid_animation). Then call `communicate()` for the number of frames in the animation:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller()
c.start()
humanoid_id = 0
animation_command, animation_record = c.get_add_humanoid_animation(humanoid_animation_name="walking_1")
commands = [TDWUtils.create_empty_room(12, 12),
            c.get_add_humanoid(humanoid_name="man_casual_1", object_id=humanoid_id),
            animation_command,
            {"$type": "play_humanoid_animation",
             "name": animation_record.name,
             "id": humanoid_id}]
commands.extend(TDWUtils.create_avatar(position={"x": -3, "y": 1.7, "z": 0.5}))
look_at = {"$type": "look_at",
           "object_id": humanoid_id}
commands.append(look_at)
c.communicate(commands)

frames = animation_record.get_num_frames()
for i in range(frames):
    c.communicate(look_at)
c.communicate({"$type": "terminate"})
```

## SMPL humanoids

 [SMPL humanoids](https://smpl.is.tue.mpg.de/downloads) have parameterized body shapes.

For an example controller, see `smpl_humanoid.py`.

To review the SMPL models available, load the SMPL humanoid librarian and iterate through the records:

```python
from tdw.librarian import HumanoidLibrarian

lib = HumanoidLibrarian("smpl_humanoids.json")
for record in lib.records:
    print(record.name)
```

Output:

```
humanoid_smpl_f
humanoid_smpl_m
```

To add a SMPL humanoid, send `add_smpl_humanoid`:

```python
import random
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.librarian import HumanoidLibrarian

c = Controller()
c.start()
c.humanoid_librarian = HumanoidLibrarian("smpl_humanoids.json")
humanoid_record = c.humanoid_librarian.get_record("humanoid_smpl_f")
animation_command, animation_record = c.get_add_humanoid_animation("walking_1")
humanoid_id = 0
commands = [TDWUtils.create_empty_room(12, 12),
            {"$type": "add_smpl_humanoid",
             "id": humanoid_id,
             "name": humanoid_record.name,
             "url": humanoid_record.get_url(),
             "position": {"x": 0, "y": 0, "z": 0},
             "rotation": {"x": 0, "y": 0, "z": 0},
             "height": random.uniform(-1, 1),
             "weight": random.uniform(-1, 1),
             "torso_height_and_shoulder_width": random.uniform(-1, 1),
             "chest_breadth_and_neck_height": random.uniform(-1, 1),
             "upper_lower_back_ratio": random.uniform(-1, 1),
             "pelvis_width": random.uniform(-1, 1),
             "hips_curve": random.uniform(-1, 1),
             "torso_height": random.uniform(-1, 1),
             "left_right_symmetry": random.uniform(-1, 1),
             "shoulder_and_torso_width": random.uniform(-1, 1)},
            animation_command,
            {"$type": "play_humanoid_animation",
             "name": animation_record.name,
             "id": humanoid_id}]
commands.extend(TDWUtils.create_avatar(position={"x": -3, "y": 1.7, "z": 0.5}))
look_at = {"$type": "look_at",
           "object_id": humanoid_id}
commands.append(look_at)
c.communicate(commands)
frames = animation_record.get_num_frames()
for i in range(frames):
    c.communicate(look_at)
c.communicate({"$type": "terminate"})
```

## Current limitations

The initial implementation of Humanoid represents the first phase of development of realistic humanoid avatars that can move around within a scene, perform various actions and interact with objects in the scene (e.g. open doors, pick up objects etc.). 

Many of the animations ideally require "prop" objects (e.g. a "mopping the floor" motion would typically require a mop object that the character is holding). At the present time there is no support for integrating props with the motion library animations, but this is on our TODO List.

Additionally, Humanoid character models do not respond to physics and cannot physically interact with other objects in the scene due to their lack of colliders etc. Should a scene object be in the path of a Humanoid motion, the Humanoid will simply pass through the object. 



