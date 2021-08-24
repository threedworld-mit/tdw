##### Objects and Scenes

# Reset a scene

In general, the goal of resetting a scene is to revert the scene and its objects to an initial state. 

## Option 1: Destroy all objects in the scene and recreate them from cached positions



Except in very certain circumstances via the Command API, scenes are static and there is no need to revert 

There is a subtle but important difference in how TDW manages memory for scenes and objects. Both are [asset bundles](https://docs.unity3d.com/Manual/AssetBundlesIntro.html) that loaded into memory (usually from TDW's remote Amazon S3 server) at runtime. The difference is:

Object asset bundles stay in memory unless otherwise requested. This means that while the *first* time you add an object, it can take a long time to load, but adding subsequent copies of the object will be extremely fast. Even if an object is destroyed, its asset bundle will stay in memory.

To demonstrate this, this controller repeatedly creates and destroys a fairly large (in terms of memory usage) asset bundle and clocks the time elapsed each time:

```python
from time import time
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils

c = Controller()
c.start()
# Create the scene.
c.communicate(TDWUtils.create_empty_room(12, 12))
object_id = c.get_unique_id()
for i in range(10):
    t0 = time()
    c.communicate([c.get_add_object(model_name="arflex_hollywood_sofa",
                     position={"x": 0, "y": 0, "z": 0},
                     object_id=object_id),
                   {"$type": "destroy_object",
                    "id": object_id}])
    print(time() - t0)
c.communicate({"$type": "terminate"})
```

If you're using `create_exterior_walls` or the wrapper function `TDWUtils.create_empty_room(12, 12)`, creating and destroying the scene is extremely fast. However, unless you're actually changing the walls of the scene per reset, you don't need to do this. Scenes are always static objects and can't change except in very specific circumstances via the Command API.

Additionally, scene asset bundles (via `add_scene` commands) are always unloaded from memory when a new scene is loaded in. This means that repeatedly calling `add_scene` is *very* slow and almost not worth it:

```python
from time import time
from tdw.controller import Controller

c = Controller()
for i in range(10):
    t0 = time()
    c.communicate(c.get_add_scene(scene_name="tdw_room"))
    print(time() - t0)
c.communicate({"$type": "terminate"})
```

 