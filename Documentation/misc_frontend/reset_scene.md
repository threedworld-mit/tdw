# Reset a Scene

## Reset a Scene to Original State

There are many ways to reset a scene in TDW to its original state. Below are the most common strategies:

### 1. Destroy the scene and rebuild it

Reloading a scene always destroys all objects and avatars within it. If you have your initialization code in a single function or set of functions, you can do this:

```python
def reset():
    c.start()
    c.communicate(TDWUtils.create_empty_room(20, 20))
    c.communicate(TDWUtils.create_avatar())
    c.add_object("iron_box", position={"x": 0, "y": y, "z": 0})
    

reset()
```

### 2. Selectively destroy parts of the scene and rebuild 

If you only need to destroy some parts of the scene, destroy those.

In this example, the objects and avatars are destroyed, but not the room:

```python
def create():
    c.start()
    c.communicate(TDWUtils.create_empty_room(20, 20))

def reset():
    c.communicate({"$type": "destroy_all_objects"})
    c.communicate(TDWUtils.create_avatar())
    c.add_object("iron_box", position={"x": 0, "y": y, "z": 0})
    

create()
reset()
```

## Reset a Scene to an Arbitrary State

Unfortunately, this is not supported in TDW. It isn't possible to take a "snapshot" of the Unity physics engine, or of TDW's "global state", and reload that snapshot later. You _can_ create your own snapshots to some extent; for example, if all you need is positional and visual material data, you can cache that in your controller.