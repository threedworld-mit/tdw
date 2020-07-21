# Humanoids

Humanoids are photorealistic 3D character models (male and female) in both business and casual attire. They are fully "rigged", i.e. they have skeletons and can be driven by motion-capture animations.

For a list of humanoids, see the records in the [Humanoid Librarian](../python/librarian/humanoid_librarian.md).

For a list of animations, see the records in the [Humanoid Animation Librarian](../python/librarian/humanoid_animation_librarian.md).

For an example controller, see `animate_humanoid.py`.

## How to add animations and humanoids

- Add a humanoid with [`add_humanoid`](../api/command_api.md#add_humanoid).
- Add an animation with [`add_humanoid_animation`]((../api/command_api.md#add_humanoid_animation)). This will add and cache the animation into memory, but not play it.
- To play an animation, first send [`play_humanoid_animation`](../api/command_api.md#play_humanoid_animation). It will advance the animation 1 frame per TDW step:

```python
from tdw.librarian import HumanoidAnimationLibrarian
from tdw.controller import Controller

c = Controller()
lib = HumanoidAnimationLibrarian()

# Your code here.

animation = lib.get_record("wading_through_water")
c.communicate({"$type": "play_humanoid_animation",
                "name": animation.name,
                "id": 0})
# Iterate through the whole animation.
frame = 0
num_frames = animation.get_num_frames()
while frame < num_frames:
    resp = c.communicate([]) # You can add commands here as needed.
    frame += 1
```

## Current limitations

The initial implementation of Humanoid represents the first phase of development of realistic humanoid avatars that can move around within a scene, perform various actions and interact with objects in the scene (e.g. open doors, pick up objects etc.). 

Many of the animations ideally require "prop" objects (e.g. a "mopping the floor" motion would typically require a mop object that the character is holding). At the present time there is no support for integrating props with the motion library animations, but this is on our TODO List.

Additionally, Humanoid character models do not respond to physics and cannot physically interact with other objects in the scene due to their lack of colliders etc. Should a scene object be in the path of a Humanoid motion, the Humanoid will simply pass through the object. 



