##### Navigation

# NavMesh pathfinding

A [NavMesh](https://docs.unity3d.com/Manual/nav-BuildingNavMesh.html) is a feature of the underlying Unity Engine that can generate basic pathfinding data for agents. In TDW, if a scene has a NavMesh you can receive path data, where a path is a list of (x, y, z) positions.

## Baking a NavMesh

A NavMesh is a static data object in a Unity scene. It must be *baked* in order to be used for navigation. It isn't possible to view the NavMesh in TDW; however, this is what it looks like in the Unity Editor (the software used to develop Unity projects):

![](images/nav_mesh_floorplan.jpg)

If you are using a [streamed scene](../core_concepts/scenes.md), there is already a baked NavMesh. 

If you are using a [proc-gen room](../objects_and_scenes/proc_gen_room.md), you must bake the NavMesh by sending [`bake_nav_mesh`](../../api/command_api.md#bake_nav_mesh):

```python
from tdw.tdw_utils import TDWUtils
from tdw.controller import Controller

c = Controller(launch_build=False)
c.communicate([TDWUtils.create_empty_room(12, 12),
               {"$type": "bake_nav_mesh"}])
```

Result:

 ![](images/nav_mesh_proc_gen_room.jpg)

## NavMesh obstacles

If there are objects in the scene, `bake_nav_mesh` will make them NavMesh obstacles:

```python
from tdw.tdw_utils import TDWUtils
from tdw.controller import Controller

c = Controller(launch_build=False)
c.communicate([TDWUtils.create_empty_room(12, 12),
               c.get_add_object(model_name="trunck",
                                object_id=0,
                                position={"x": 0, "y": 0, "z": 0}),
               {"$type": "bake_nav_mesh"}])
```

Result:

![](images/nav_mesh_trunck.jpg)

If you add objects *after* baking the NavMesh, they will be ignored. This can allow you to manually set NavMesh obstacles by sending [`make_nav_mesh_obstacle`](../../api/command_api.md#make_nav_mesh_obstacle). For example, you might want some objects to carve wider areas than others.

```python
from tdw.tdw_utils import TDWUtils
from tdw.controller import Controller

c = Controller(launch_build=False)
c.communicate([TDWUtils.create_empty_room(12, 12),
               {"$type": "bake_nav_mesh"},
               c.get_add_object(model_name="trunck",
                                object_id=0,
                                position={"x": 0, "y": 0, "z": 0}),
               {"$type": "make_nav_mesh_obstacle",
                "id": 0,
                "carve_type": "stationary",
                "scale": 1,
                "shape": "box"},
               c.get_add_object(model_name="rh10",
                                object_id=1,
                                position={"x": -1, "y": 0, "z": 1.5}),
               {"$type": "make_nav_mesh_obstacle",
                "id": 1,
                "carve_type": "all",
                "scale": 1,
                "shape": "box"}])
```

Result:

![](images/nav_mesh_obstacles.jpg)

## `NavMeshPath` output data

