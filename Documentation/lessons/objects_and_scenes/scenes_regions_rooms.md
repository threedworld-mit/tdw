##### Objects and Scenes

# Scenes, regions, and rooms

Procedural generation in TDW often utilizes spatial scene data, i.e. the size of the scene, where its rooms are, the size of its rooms, etc. Some of this data can be calculated at runtime while some of it has to be cached beforehand.

TDW's proc-gen system, in particular the [ProcGenKitchen](proc_gen_kitchen.md), uses this scene data to populate a scene with objects. This document explains what each relevant data class contains and how it is used.

## 1. `SceneRegions`

[`SceneRegions`](../../api/output_data.md) is the raw scene region output data of a scene. If you've read the "Core Concepts" lesson you've already seen this data in the [Output Data document](../core_concepts/output_data.md). 

Scenes have 1-*n* **regions**, which are rectangular spaces within a scene. Scenes may have multiple regions. In [streamed scenes](../core_concepts/scenes.md), regions are pre-defined by the TDW development team. In [proc-gen scenes](proc_gen_room.md), there is always one region and it spans the entire scene.

This example loads a scene and prints data for each **region**:

```python
from tdw.controller import Controller
from tdw.output_data import OutputData, SceneRegions

c = Controller()
resp = c.communicate([Controller.get_add_scene(scene_name="mm_craftroom_4a"),
                      {"$type": "send_scene_regions"}])
for i in range(len(resp) - 1):
    # Get the output data ID.
    r_id = OutputData.get_data_type_id(resp[i])
    # This is scene regions output data.
    if r_id == "sreg":
        scene_regions = SceneRegions(resp[i])
        # Print the bounds.
        for j in range(scene_regions.get_num()):
            print(j, scene_regions.get_bounds(j))
c.communicate({"$type": "terminate"})
```

Output:

```
0 (6.704792499542236, 2.892470359802246, 2.153679847717285)
1 (3.7115163803100586, 2.892470359802246, 4.577892303466797)
```

## 2. `SceneBounds`

[`SceneBounds`](../../python/scene_data/scene_bounds.md) is a helpful wrapper class for `SceneRegions` output data. This example prints the extents of the scene:

```python
from tdw.controller import Controller
from tdw.scene_data.scene_bounds import SceneBounds

c = Controller()
resp = c.communicate([Controller.get_add_scene(scene_name="mm_craftroom_4a"),
                      {"$type": "send_scene_regions"}])
scene_bounds = SceneBounds(resp=resp)
print("x_min", scene_bounds.x_min)
print("x_max", scene_bounds.x_max)
print("z_min", scene_bounds.z_min)
print("z_max", scene_bounds.z_max)
c.communicate({"$type": "terminate"})
```

Output:

```
x_min -3.361567974090576
x_max 3.34322452545166
z_min -3.3512234687805176
z_max 3.377729892730713
```

## 3. `RegionBounds`

[`RegionBounds`](../../python/scene_data/region_bounds.md) is data per region within `SceneBounds`:

```python
from tdw.controller import Controller
from tdw.scene_data.scene_bounds import SceneBounds

c = Controller()
resp = c.communicate([Controller.get_add_scene(scene_name="mm_craftroom_4a"),
                      {"$type": "send_scene_regions"}])
scene_bounds = SceneBounds(resp=resp)
for region in scene_bounds.regions:
    print("id", region.region_id)
    print("x_min", region.x_min)
    print("x_max", region.x_max)
    print("z_min", region.z_min)
    print("z_max", region.z_max)
c.communicate({"$type": "terminate"})
```

Output:

```
id 1
x_min -3.361567974090576
x_max 3.34322452545166
z_min 1.2240500450134277
z_max 3.377729892730713
id 0
x_min -1.8706207275390625
x_max 1.840895652770996
z_min -3.3512234687805176
z_max 1.2266688346862793
```

## 4. `InteriorRegion`

[`InteriorRegion`](../../python/scene_data/interior_region.md) is a subclass of `RegionBounds` with additional data. **Unlike `SceneRegions`, `SceneBounds`, and `RegionBounds`, `InteriorRegion` cannot be calculated via TDW output data.** This is because that data it contains is too difficult to detect programmatically. As a consequence, TDW includes cached `InteriorRegion` data that has been partially defined by the development team.

## 5. `Room`

A [`Room`](../../scene_data/room.md) is a collection of `InteriorRegions`. A room has a `main_region` and 0-*n* "alcoves". For example, an `L`-shaped room has 2 regions: `|` (the main region) and `_` (an alcove).

In TDW, room data is cached per-scene in [`SceneRecord.rooms`](../../python/librarian/scene_librarian.md). Right now, only a subset of scenes that could have room data actually have room data:

```python
from tdw.librarian import SceneLibrarian

librarian = SceneLibrarian()
for record in librarian.records:
    if len(record.rooms) > 0:
        print(record.name)
```

