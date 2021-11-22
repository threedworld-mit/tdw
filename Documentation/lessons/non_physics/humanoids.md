##### Non-physics objects

# Non-physics humanoids

Non-physics humanoids are photorealistic 3D character models (male and female) in both business and casual attire. They are fully "rigged", i.e. they have skeletons and can be driven by motion-capture animations. They are non-physics in that they don't have mass or colliders; if allowed, they will walk through other objects without interacting with them.

## Add a non-physics humanoid to the scene

Like [objects](../core_concepts/objects.md) and [scenes](../core_concepts/scenes.md), non-physics humanoids are **asset bundles** stored on a remote S3 server that must be downloaded before they can be added to the scene. Add a non-physics humanoid the scene with the [`add_humanoid`](../../api/command_api.md#add_humanoid) command or the wrapper function [`Controller.get_add_humanoid()`](../../Python/controller.md):

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

# Add a camera and enable image capture.
camera = ThirdPersonCamera(avatar_id="a",
                           position={"x": 0, "y": 1.5, "z": 1.6},
                           look_at={"x": 0, "y": 1.0, "z": -1})
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("humanoid_minimal")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=["a"], path=path)
# Start the controller.
c = Controller()
c.add_ons.extend([camera, capture])
# Create a scene and add a humanoid.
humanoid_id = c.get_unique_id()
c.communicate([TDWUtils.create_empty_room(8, 8),
               c.get_add_humanoid(humanoid_name="man_suit",
                                  object_id=humanoid_id,
                                  position={"x": 0, "y": 0, "z": -1})])
c.communicate({"$type": "terminate"})
```

Result:

![](images/humanoids/man_suit.jpg)

This controller does the exact same thing of the previous controller but uses the `add_humanoid` command without the wrapper function:

```python
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

# Add a camera and enable image capture.
camera = ThirdPersonCamera(avatar_id="a",
                           position={"x": 0, "y": 1.5, "z": 1.6},
                           look_at={"x": 0, "y": 1.0, "z": -1})
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("humanoid_minimal")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=["a"], path=path)
# Start the controller.
c = Controller()
c.add_ons.extend([camera, capture])
# Create a scene and add a humanoid.
humanoid_id = c.get_unique_id()
c.communicate([TDWUtils.create_empty_room(8, 8),
               {'$type': 'add_humanoid',
                'name': 'man_suit', 
                'url': 'https://tdw-public.s3.amazonaws.com/humanoids/linux/2019.2/man_suit',
                'position': {'x': 0, 'y': 0, 'z': -1},
                'rotation': {'x': 0, 'y': 0, 'z': 0},
                'id': 4337102}])
c.communicate({"$type": "terminate"})
```

## Select a non-physics humanoid

Non-physics humanoid metadata records are stored in a [`HumanoidLibrarian`](../../python/librarian/humanoid_librarian.md):

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

## Animate a non-physics humanoid

Non-physics humanoid animations are *also* asset bundles. Humanoid animations were recorded at varying framerates, have varying play lengths. Additionally, some animations are designed to loop and some are not.

All of this means that prior to adding an animation to the scene, you need to have its metadata. Humanoid animation metadata is stored in the [Humanoid Animation Librarian](../python/librarian/humanoid_animation_librarian.md):

```python
from tdw.librarian import HumanoidAnimationLibrarian

lib = HumanoidAnimationLibrarian()
for record in lib.records:
    print(record.name)
```

To fetch a specific record:

```python
from tdw.librarian import HumanoidAnimationLibrarian

lib = HumanoidAnimationLibrarian()
record = lib.get_record("walking_1")
print(record.name, record.framerate, record.get_num_frames(), record.loop)
```

Output:

```
walking_1 30 69 True
```

There are additional animations extracted from [SMPL](https://smpl.is.tue.mpg.de/downloads) in a separate librarian that can be used by any humanoid:

```python
from tdw.librarian import HumanoidAnimationLibrarian

lib = HumanoidAnimationLibrarian("smpl_animations.json")
for record in lib.records:
    print(record.name)
```

To start an animation, you must first send [`add_humanoid_animation`](../../api/command_api.md#add_humanoid_animation). This will download the animation asset bundle and load it into memory. After doing this, you don't need to send `add_humanoid_animation` for that animation again. For example, if you want to play a walk animation *n* times in a row, you only need to send `add_humanoid_animation` once.

You can also call [`Controller.get_add_humanoid_animation()`](../../Python/controller.md). This returns a *tuple*: an `add_humanoid_animation` command and a metadata record.

This will add the `walking_1` animation to this scene:

```python
from tdw.controller import Controller

c = Controller()
animation_command, animation_record = c.get_add_humanoid_animation("walking_1")
c.communicate(animation_command)
```

This example does the same thing, but without the wrapper function:

```python
from tdw.controller import Controller

c = Controller()
c.communicate({'$type': 'add_humanoid_animation', 
               'name': 'walking_1',
               'url': 'https://tdw-public.s3.amazonaws.com/humanoid_animations/linux/2019.2/walking_1'})
```

To play the animation, send  [`play_humanoid_animation`](../api/command_api.md#play_humanoid_animation). Then call `communicate()` for the number of frames in the animation.

This example adds a non-physics humanoid, adds an animation, and then plays the animation for 2 loops:

```python
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Minimal example of an animated non-physics humanoid.
"""

# Add a camera and enable image capture.
camera = ThirdPersonCamera(avatar_id="a",
                           position={"x": -5.5, "y": 5, "z": -2},
                           look_at={"x": 0, "y": 1.0, "z": -1})
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("humanoid_minimal")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=["a"], path=path)
# Start the controller.
c = Controller()
c.add_ons.extend([camera, capture])
# Create a scene and add a humanoid.
humanoid_id = c.get_unique_id()
commands = [TDWUtils.create_empty_room(36, 36),
            c.get_add_humanoid(humanoid_name="man_suit",
                               object_id=humanoid_id,
                               position={'x': 0, 'y': 0, 'z': -1})]
# Add an animation.
animation_name = "walking_1"
animation_command, animation_record = c.get_add_humanoid_animation(humanoid_animation_name=animation_name)
num_frames = animation_record.get_num_frames()
commands.extend([animation_command,
                 {"$type": "play_humanoid_animation",
                  "name": animation_name,
                  "id": humanoid_id}])
# Set the framerate.
commands.append({"$type": "set_target_framerate",
                 "framerate": animation_record.framerate})
# Send the commands.
c.communicate(commands)
# Play some loops.
for i in range(2):
    # Play the animation.
    for j in range(num_frames):
        c.communicate([])
    # Start the next loop.
    c.communicate({"$type": "play_humanoid_animation",
                   "name": animation_name,
                   "id": humanoid_id})
c.communicate({"$type": "terminate"})
```

Result:

![](images/humanoids/walk.gif)

## SMPL humanoids

 [SMPL humanoids](https://smpl.is.tue.mpg.de/downloads) have parameterized body shapes.

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

To fetch a specific record:

```python
from tdw.librarian import HumanoidLibrarian

lib = HumanoidLibrarian("smpl_humanoids.json")
record = lib.get_record("humanoid_smpl_f")
```

To add a SMPL humanoid, send [`add_smpl_humanoid`](../api/command_api.md#add_smpl_humanoid):

