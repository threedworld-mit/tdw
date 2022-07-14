# CHANGELOG

# v1.10.x

To upgrade from TDW v1.9 to v1.10, read [this guide](upgrade_guides/v1.9_to_v1.10.md).

## v1.10.1

### Command API

#### New Commands

| Command              | Description                                     |
| -------------------- | ----------------------------------------------- |
| `send_field_of_view` | Send the camera field of view and focal length. |

### Output Data

#### New Output Data

| Output Data   | Description                                |
| ------------- | ------------------------------------------ |
| `FieldOfView` | The camera field of view and focal length. |

### Model Library

- Flagged b04_wallmounted_soap_dispenser_composite as do_not_use (missing asset bundles)

## v1.10.0

### New Features

- **Added `ProcGenKitchen`.** This add-on procedurally generates kitchen environments.

### Command API

#### New Commands

| Command                          | Description                                                  |
| -------------------------------- | ------------------------------------------------------------ |
| `add_box_container`              | Add a box container shape to an object.                      |
| `add_cylinder_container`         | Add a cylindrical container shape to an object.              |
| `add_sphere_container`           | Add a spherical container shape to an object.                |
| `send_containment`               | Send `Overlap` output data from every container shape.       |
| `set_sub_object_id`              | Set the ID of a composite sub-object.                        |
| `set_first_person_avatar`        | Set the parameters of an A_First_Person avatar.              |
| `send_mouse_raycast`             | Raycast from a camera through the mouse screen position.     |
| `send_mouse`                     | Send mouse output data.                                      |
| `set_cursor`                     | Set cursor parameters                                        |
| `set_visual_material_smoothness` | Set the smoothness (glossiness) of an object's visual material. |

### Modified Commands

| Command                                               | Modification                                                 |
| ----------------------------------------------------- | ------------------------------------------------------------ |
| `create_avatar`                                       | Removed: `A_Img_Caps`, `A_StickyMitten_Baby`, `A_StickyMitten_Adult`, `A_Nav_Mesh`<br>Added: `A_First_Person` |
| `send_boxcast`<br>`send_raycast`<br>`send_spherecast` | `origin` and `destination` parameters now default to `{"x": 0, "y": 0, "z": 0}`. |
| `add_ui_image`<br>`add_ui_text`                       | Added optional parameter `raycast_target`.                   |

#### Removed Commands

| Command                                                      | Reason                                                       |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| `set_proc_gen_floor_color`                                   | Deprecated in v1.9; use `set_floor_color` instead.           |
| `set_proc_gen_floor_texture_scale`                           | Deprecated in v1.9; use `set_floor_texture_scale` instead.   |
| `set_proc_gen_floor_material`                                | Deprecated in v1.9; use `set_floor_material` instead.        |
| `send_composite_objects`                                     | Deprecated in v1.9; use `send_static_composite_objects` and `send_dynamic_composite_objects` instead. |
| `set_nav_mesh_avatar`<br>`set_nav_mesh_avatar_destination`   | Removed `A_Nav_Mesh`                                         |
| `set_avatar_rigidbody_constraints`<br>`rotate_head_by`<br>`rotate_waist`<br>`set_sticky_mitten_profile`<br>`stop_arm_joint`<br>`bend_arm_joint_by`<br>`bend_arm_joint_to`<br>`adjust_joint_angular_drag_by`<br>`set_joint_angular_drag`<br>`adjust_joint_damper_by`<br>`adjust_joint_force_by`<br>`set_joint_damper`<br>`set_joint_force`<br>`put_down`<br>`set_stickiness`<br>`pick_up`<br>`pick_up_proximity` | Removed `A_StickyMitten_Baby` and `A_StickyMitten_Adult`     |

### Output Data

#### New Output Data

| Output Data | Description                        |
| ----------- | ---------------------------------- |
| `Mouse`     | Data for mouse input and movement. |

#### Modified Output Data

| Output Data                | Modification                                                 |
| -------------------------- | ------------------------------------------------------------ |
| `Transforms`               | Significant speed improvement.<br>`get_position(index)`,  `get_rotation(index)`, and `get_forward(index)` return numpy arrays instead of tuples. |
| `Rigidbodies`              | Significant speed improvement.<br/>`get_velocity(index)` and `get_angular_velocity(index)` return a numpy arrays instead of tuples. |
| `StaticRigidbodies`        | Significant speed improvement.                               |
| `Bounds`                   | Significant speed improvement.<br>`get_front(index)`, `get_back(index)`, etc. return numpy arrays instead of tuples. |
| `SegmentationColors`       | `get_object_color(index)` returns a numpy array instead of a tuple. |
| `Volumes`                  | Significant speed improvement.                               |
| `LocalTransforms`          | Significant speed improvement.<br/>`get_position(index)`,  `get_rotation(index)`, and `get_forward(index)` return numpy arrays instead of tuples. |
| `DynamicCompositeObjects`  | Significant speed improvement.<br>Restructured how hinge and light data is stored and returned. |
| `IdPassSegmentationColors` | Moderate (approximately 25%) speed improvement.<br>Removed `get_sensor_name()`. |

#### Removed Output Data

| Output Data                                                  | Reason                                                       |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| `CompositeObjects`                                           | Deprecated in v1.9; use `StaticCompositeObjects` and `DynamicCompositeObjects` instead. |
| `ArrivedAtNavMeshDestination`                                | Removed `A_Nav_Mesh`                                         |
| `AvatarStickyMitten`<br>`AvatarStickyMittenSegmentationColors` | Removed `A_StickyMitten_Baby` and `A_StickyMitten_Adult`     |

### `tdw` module

- **Added `ProcGenKitchen`.** Procedurally generate a kitchen in a new scene or an existing scene.
- Added procedural generation "arrangement" data classes:
  - `Arrangement` Abstract base class for procedurally-generated spatial arrangements of objects.
  - `ArrangementAlongWall` Abstract class procedurally-generated spatial arrangements of objects that are positioned alongside a wall as part of a lateral arrangement.
  - `ArrangementWithRootObject` Abstract class for procedurally-generated spatial arrangements of objects with a single root object.
  - `Basket` A basket with random objects.
  - `CupAndCoaster` A cup, which sometimes has a coaster underneath it.
  - `Dishwasher` A dishwasher with a kitchen counter top with objects on it.
  - `KitchenCabinet` Abstract class for kitchen counters, wall cabinets, and sinks. These all shared the same canonical rotation and height.
  - `KitchenCounter` A kitchen counter can have objects on it and inside it.
  - `KitchenCounterTop` A floating kitchen counter top along a wall.
  - `KitchenTable` A kitchen table has chairs and table settings.
  - `Microwave` A microwave can have objects on top of it and inside of it.
  - `Painting` A painting hanging on the wall.
  - `Plate` A kitchen plate that may have food on it.
  - `Radiator` A radiator.
  - `Refrigerator` A refrigerator.
  - `Shelf` Shelving with objects on the shelves.
  - `SideTable` A small side table with objects on it.
  - `Sink` A sink can have objects on it and inside it.
  - `StackOfPlates` A stack of plates.
  - `Stool` A stool placed along a wall.
  - `Stove` A stove with oven doors.
  - `Suitcase` A suitcase placed along a wall.
  - `TableAndChairs` Abstract base class for a table with chairs around it.
  - `TableSetting` A table setting includes a plate, fork, knife, spoon, and sometimes a cup.
  - `Void` An empty space along a wall.
  - `WallCabinet` A wall cabinet hangs on the wall above a kitchen counter. It can have objects inside it.
- Added procedural generation cabinetry data classes:
  - `Cabinetry` A set of cabinetry models.
  - `CabinetryType` Enum values describing a set of cabinetry.
- Added scene data classes:
  - `InteriorRegion` An interior region has bounds data and cached data regarding continuous walls and walls with windows.
  - `Room` A room in an interior environment.
- Adjusted existing scene data classes:
  - New constructor parameters for `RegionBounds`
  - Renamed `scene_bounds.rooms` to `scene_bounds.regions`
- Added: `CardinalDirection` Enum for cardinal directions.
- Added: `OrdinalDirection` Enum for ordinal directions.
- Added: `TDWUtils.get_corners_from_wall(wall)` Returns the corners of the wall as a 2-element list of `OrdinalDirection`.
- Added: `TDWUtils.get_direction_from_corner(corner, wall)` Given an corner an a wall, get the direction that a lateral arrangement will run along. 
- `ContainerManager` now uses "container shapes" instead of trigger colliders. Trigger colliders are a built-in feature of Unity that detect non-physics collisions. They generate lots of event data, causing `ContainerManager` to be very slow in complex scenes. Now, `ContainerManager` sends "container shape" commands such as `add_box_container`, which define a 3D space without a trigger collider. Per-frame, container shapes will send `Overlap` data instead of `TriggerCollision` data. The result is that `ContainerManager` is much faster now.
  - `ContainerManager` sends container shape commands (see above) per object and then sends `send_containment` to request `Overlap` data per frame.
  - `ContainerManager` is no longer a subclass of `TriggerCollisionManager`, meaning that it no longer has the following fields: `trigger_ids` and `collisions`.
  - Added: `ContainerManager.container_shapes` A dictionary of container IDs to parent object IDs.
  - Renamed `ContainerManager._tags` to `ContainerManager.tags`
  - Replaced `ContainerManager.add_box_collider(object_id, position, scale, rotation, trigger_id, tag)` with `ContainerManager.add_box(object_id, position, tag, half_extents, rotation)`
  - Replaced `ContainerManager.add_cylinder_collider(object_id, position, scale, rotation, trigger_id, tag)` with `ContainerManager.add_cylinder(object_id, position, tag, radius, height, rotation)`
  - Replaced `ContainerManager.add_sphere_collider(object_id, position, diameter, trigger_id, tag)` with `ContainerManager.add_sphere(object_id, position, tag, radius)`
- Refactored the following containment data classes:
  - Replaced `ContainerBoxTriggerCollider` with `BoxContainer`
  - Replaced `ContainerCylinderTriggerCollider` with `CylinderContainer`
  - Replaced `ContainerSphereTriggerCollider` with `SphereContainer`
  - Renamed `ContainerColliderTag` to `ContainerTag`
  - Replaced `ModelRecord.container_colliders` with `ModelRecord.container_shapes`
  - Replaced `ContainmentEvent.object_id` (the ID of the contained object) with `ContainmentEvent.object_ids` (a numpy array of all contained objects)
- The data classes used in `DynamicCompositeObjects` (`CompositeObjectDynamic`, `HingeDynamic`, `LightDynamic`, and `SubObjectDynamic`) all take different constructor parameters. They are otherwise unchanged. The API for `CompositeObjectManager` is the same as before.
- **Added: `FirstPersonAvatar` add-on.** This avatar can be controlled using standard video game first-person keyboard and mouse controls.
- Added: `Mouse` add-on. Listen for mouse input and movement.
- Renamed `ThirdPersonCameraBase._RENDER_ORDER` to `ThirdPersonCameraBase.RENDER_ORDER`
- Renamed `PhysicsAudioRecorder.recording` to `PhysicsAudioRecorder.done`
- Added optional parameter `record_audio` to the `PhysicsAudioRecorder` constructor.
- Parameter `path` in `PhysicsAudioRecorder.start(path)` is now optional (defaults to None).

### Build

- Fixed: `add_line_renderer` doesn't correctly add line points.

### Example Controllers

- Split `objects_and_scenes/` controllers into `scene_setup_high_level/` and `scene_setup_low_level/`
- Removed: `objects_and_scenes/proc_gen_objects.py` (obsolete)
- Removed: `keyboard/keyboard_controls.py` (obsolete)
- Added: `scene_setup_high_level/cup_and_coaster.py`
- Added: `scene_setup_high_level/kitchen_counter.py`
- Added: `scene_setup_high_level/microwave.py`
- Added: `scene_setup_high_level/plate.py`
- Added: `scene_setup_high_level/proc_gen_kitchen_lighting.py`
- Added: `scene_setup_high_level/proc_gen_kitchen_minimal.py`
- Added: `scene_setup_high_level/proc_gen_kitchen_rng.py`
- Added: `keyboard_and_mouse/first_person_controls.py`
- Added: `keyboard_and_mouse/mouse_controls.py`

### Model Library

- Added to `models_special.json`: b04_db_apps_tech_08_03_counter_top, b05_db_apps_tech_08_09_counter_top, dishwasher_4_counter_top, floating_counter_top_counter_top

### Scene Library

- Added: `SceneRecord.rooms` Cached `Room` data per scene.

### Benchmark

- Added kitchen benchmark to `PerformanceBenchmarkController` and `main.py`
- Removed agent and flex benchmarks from `PerformanceBenchmarkController` and `main.py` because they are obsolete.
- Updated Object Data benchmarks.

### Documentation

- The "Objects and Scenes" lesson has been split into two sections: "Scene Setup (High-Level APIs)" and "Scene Setup (Low-Level APIs)"
- The "Keyboard" lesson has been renamed to "Keyboard and Mouse"

#### New Documentation

| Document                                                     | Description                                               |
| ------------------------------------------------------------ | --------------------------------------------------------- |
| `upgrade_guides/v1.9_to_v1.10.md`                            | Upgrade guide.                                            |
| `scene_setup/overview.md`                                    | Overview of scene setups.                                 |
| `scene_setup_high_level/overview.md`                         | Overview of TDW's high-level scene setup APIs.            |
| `scene_setup_high_level/arrangements.md`                     | How `Arrangement` and its sub-classes work.               |
| `scene_setup_high_level/proc_gen_kitchen.md`                 | Lesson document for the `ProcGenKitchen` add-on.          |
| `scene_setup_high_level/rooms.md`                            | How room data works.                                      |
| `scene_setup_low_level/overview.md`                          | Overview of TDW's lower-level scene setup APIs.           |
| `keyboard_and_mouse/first_person_avatar.md`                  | Lesson document for the `FirstPersonAvatar` add-on.       |
| `keyboard_and_mouse/mouse.md`                                | Lesson document for the `Mouse` add-on.                   |
| `keyboard_and_mouse/overview.md`                             | Overview of keyboard and mouse input.                     |
| `python/add_ons/proc_gen_kitchen.md`                         | API documentation for `ProcGenKitchen`                    |
| `python/proc_gen/arrangements/cabinetry/cabinetry.md`<br>`python/proc_gen/arrangements/cabinetry/cabinetry_type.md` | API documentation for cabinetry.                          |
| `python/proc_gen/arrangements/arrangement.md`<br/>`python/proc_gen/arrangements/arrangement_along_wall.md`<br/>`python/proc_gen/arrangements/arrangement_with_root_object.md`<br/>`python/proc_gen/arrangements/basket.md`<br/>`python/proc_gen/arrangements/cup_and_coaster.md`<br/>`python/proc_gen/arrangements/dishwasher.md`<br/>`python/proc_gen/arrangements/kitchen_cabinet.md`<br/>`python/proc_gen/arrangements/kitchen_counter.md`<br/>`python/proc_gen/arrangements/kitchen_counter_top.md`<br/>`python/proc_gen/arrangements/kitchen_table.md`<br/>`python/proc_gen/arrangements/microwave.md`<br/>`python/proc_gen/arrangements/painting.md`<br/>`python/proc_gen/arrangements/plate.md`<br/>`python/proc_gen/arrangements/radiator.md`<br/>`python/proc_gen/arrangements/refrigerator.md`<br/>`python/proc_gen/arrangements/shelf.md`<br/>`python/proc_gen/arrangements/side_table.md`<br/>`python/proc_gen/arrangements/sink.md`<br/>`python/proc_gen/arrangements/stack_of_plates.md`<br/>`python/proc_gen/arrangements/stool.md`<br/>`python/proc_gen/arrangements/stove.md`<br/>`python/proc_gen/arrangements/suitcase.md`<br/>`python/proc_gen/arrangements/table_and_chairs.md`<br/>`python/proc_gen/arrangements/table_setting.md`<br/>`python/proc_gen/arrangements/void.md`<br/>`python/proc_gen/arrangements/wall_cabinet.md` | API documentation for `Arrangement` and its data classes. |
| `python/cardinal_direction.md`                               | API documentation for `CardinalDirection`.                |
| `python/ordinal_direction.md`                                | API documentation for `OrdinalDirection`.                 |
| `python/add_ons/mouse.md`                                    | API documentation for `Mouse`.                            |
| `python/add_ons/first_person_avatar.md`                      | API documentation for `FirstPersonAvatar`.                |

#### Modified Documentation

| Document                                                     | Modification                                                 |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| `lessons/semantic_states/containment.md`                     | Rewrote most of the document and replaced some images in order to describe container shapes. |
| `python/container_data/`                                     | Removed old API documents (e.g. `container_collider_tag.md`) and added new API documents (e.g. `container_tag.md`). |
| `benchmark/benchmark.md`                                     | Added explanation and FPS of kitchen benchmark.              |
| `objects_and_scenes/floorplans.md`<br>`objects_and_scenes/reset_scene.md` | Moved to `scene_setup_high_level/`                           |
| `objects_and_scenes/bounds.md`<br>`objects_and_scenes/materials_textures_colors.md`<br>`objects_and_scenes/proc_gen_room.md`<br>`objects_and_scenes/units.md` | Moved to `scene_setup_low_level/`                            |

### Removed Documentation

| Document                                 | Reason    |
| ---------------------------------------- | --------- |
| `objects_and_scenes/proc_gen_objects.md` | Obsolete. |

# v1.9.x

To upgrade from TDW v1.8 to v1.9, read [this guide](upgrade_guides/v1.8_to_v1.9.md).

## v1.9.17

### `tdw` module

- Added: `OculusTouch.vr_node_ids` Objects IDs of the VR nodes (body and hands).

### Build

- Replaced the head following logic of the Oculus Touch rigs. Previously, the head was a Rigidbody object that responded to physics. This could result in crashes to desktop due to invalid velocities, especially if the framerate was slow. Now, the head is a non-physics object.

## v1.9.16

### Output Data

#### Modified Output Data

| Output Data | Modification                                                 |
| ----------- | ------------------------------------------------------------ |
| `Collision` | Added: `get_impulse()` The total impulse applied to the pair of objects to resolve the collision. |

### Build

- Fixed: `teleport_vr_rig` doesn't teleport all sub-objects of the rig correctly.

### `tdw` module

- Added field `impulse` to `CollisionObjObj`
- Added optional field `plane_distance` to `ui.attach_canvas_to_avatar()` and `ui.attach_canvas_to_vr_rig()`. 
- The default `plane_distance` value for `ui.attach_canvas_to_vr_rig(plane_distance)` is 0.25 (was 1)
- Added `ui.add_loading_screen(text, text_size)` A macro function for loading screens.
- Added optional parameters `position` (an x, y, z dictionary) and `rotation` to the constructor of `VRRig`, `vr.reset()`, the constructor of `OculusTouch`, and `oculus_touch.reset()`. This fixes a "bug" in which it wasn't possible to set the position of a VR rig on the same frame as when it is spawned.

### Model Library

- Added to `models_core.json`: b01_trumpet, b03_trumpet_vray, b03_piccolo_trumpet_vray, b04_b200003_01, b04_baterijska_busilica, dewalt_compact_drill_vray, b03_hair_comb_2010, b04_baseball_bat, b05_racket, dumb-bell_2010, 12_06_001, b04_faucet1, b04_p22732_cc_cp_2013, b04_p25050_slc_ad_2013, b05_p24409_00_cp_2013, brizo_solna, kitchen_faucet, pixamoon_free_test_faucet_001_publish
- , Removed from `models_core.json` and `models_full.json`: b03_12_06_027_composite (asset bundle doesn't exist).
- Flagged b03_headphone__max2014 in `models_full.json` as do_not_use (bad mesh geometry causes the model to bounce rapidly).

### Documentation

#### Modified Documentation

| Document                     | Modification                                                 |
| ---------------------------- | ------------------------------------------------------------ |
| `lessons/vr/oculus_touch.md` | Added documentation for `position` and `rotation` parameters. |

## v1.9.15

### New Features

- **Added Obi Cloth.**

### Command API

#### New Commands

| Command                   | Description                                                  |
| ------------------------- | ------------------------------------------------------------ |
| `set_obi_solver_scale`    | Set an Obi solver's scale. This will uniformly scale the physical size of the simulation, without affecting its behavior. |
| `create_obi_cloth_sheet`  | Create an Obi cloth sheet object.                            |
| `create_obi_cloth_volume` | Create an Obi cloth volume object.                           |
| `apply_force_to_obi_cloth` | Apply a uniform force to an Obi cloth actor. |
| `apply_torque_to_obi_cloth` | Apply a uniform torque to an Obi cloth actor. |
| `parent_textured_quad_to_object` | Parent a textured quad to an object in the scene. The textured quad will always be at a fixed local position and rotation relative to the object. |
| `unparent_textured_quad`         | Unparent a textured quad from an object.                     |

#### Deprecated Commands

| Command                | Reason                 |
| ---------------------- | ---------------------- |
| `set_flex_cloth_actor` | Use Obi cloth instead. |

### Output Data

#### Modified Output Data

| Output Data          | Modification                                                 |
| -------------------- | ------------------------------------------------------------ |
| `OculusTouchButtons` | Added: `get_left_axis()` and `get_right_axis()` to listen for control stick input. |

### Build

- Fixed: Freeze when sending `set_vr_obi_collision_material` or `create_vr_obi_colliders`
- Fixed: `add_ui_image` often creates images with badly-stretched borders.

### `tdw` module

- Fixed: Crash in `ObiActor` in certain cases if particle output data is enabled.
- Added functions to `Obi` add-on:
  - `create_cloth_sheet()`  Create a cloth sheet object.
  - `create_cloth_volume()` Create a cloth volume object.
  - `set_solver()` Set solver parameters.
  - `untether_cloth_sheet()` Untether a cloth sheet.
  - `apply_force_to_cloth()` Apply a force and/or torque to a cloth actor.
- Added data classes for Obi cloth in `tdw.obi_data.cloth`:
  - `ClothMaterial` 
  - `SheetType`
  - `TetherParticleGroup`
  - `VolumeType`
  - `TetherType`
  - `ForceMode`
- Added to `OculusTouch` add on: `self.listen_to_axis(is_left, delta)` Listen to control stick movement. 
- Fixed: `OculusTouch` doesn't set non-kinematic non-graspable objects to `discrete` collision detection mode.

### Model Library

- Added models to `models_core.json` and `models_full.json`: b03_12_06_027_composite, b04_wallmounted_soap_dispenser_composite, vray_077_composite, vray_083_composite, vray_084_composite, vray_085_composite
- Added models to `models_special.json`: stairs_one, stairs_two

### Example Controllers

- Added: `vr/oculus_touch_axis_listener.py`
- Added Obi cloth example controllers in `obi/`:
  - `cloth_sheet.py`
  - `cloth_volume.py`
  - `custom_cloth.py`
  - `sheet_types.py`
  - `tether_self.py`
  - `untether.py`
  - `tether_object.py`

### Documentation

#### New Documentation

| Document                                                     | Modification                                  |
| ------------------------------------------------------------ | --------------------------------------------- |
| `lessons/obi/cloth.md`                                       | Documentation for Obi cloth.                  |
| `python/obi_data/cloth/cloth_material.md`<br>`python/obi_data/cloth/sheet_type.md`<br>`python/obi_data/cloth/tether_particle_group.md`<br>`python/obi_data/cloth/volume_type.md` | API documentation for Obi cloth data classes. |

#### Modified Documentation

| Document                      | Modification                                    |
| ----------------------------- | ----------------------------------------------- |
| `lessons/obi/solvers.md`      | Added an example of how to scale a cloth sheet. |
| `lessons/obi/obi_and_flex.md` | Added cloth benchmarks.                         |
| `lessons/vr/oculus_touch.md` | Added a section for control stick input. |
| `lessons/non_physics/textured_quads.md` | Clarified  that only textured quad commands work with textured quads. |

## v1.9.14

### Command API

#### New Commands

| Command                      | Description                                                  |
| ---------------------------- | ------------------------------------------------------------ |
| `add_ui_canvas`              | Add a UI canvas to the scene. By default, the canvas will be an "overlay" and won't appear in image output data. |
| `attach_ui_canvas_to_avatar` | Attach a UI canvas to an avatar. This allows the UI to appear in image output data. |
| `attach_ui_canvas_to_vr_rig` | Attach a UI canvas to the head camera of a VR rig.           |
| `destroy_ui_canvas`          | Destroy a UI canvas and all of its UI elements.              |
| `add_ui_image`               | Add a UI image to the scene. Note that the size parameter must match the actual pixel size of the image. |
| `add_ui_text`                | Add UI text to the scene.                                    |
| `destroy_ui_element`         | Destroy a UI element in the scene.                           |
| `set_ui_element_size`        | Set the size of a UI element.                                |
| `set_ui_text`                | Set the text of a Text object that is already on the screen. |

### `tdw` module

- Added `UI` add-on.

### Documentation

#### New Documentation

| Document                    | Description                            |
| --------------------------- | -------------------------------------- |
| `lessons/non_physics/ui.md` | User documentation to the `UI` add-on. |
| `python/add_ons/ui.md`      | API documentation for the `UI` add-on. |

#### Modified Documentation

| Document                          | Modification                                                 |
| --------------------------------- | ------------------------------------------------------------ |
| `lessons/misc/c_sharp_sources.md` | Replaced the document with a single paragraph explaining the reasons the C# code is closed-source. |

## v1.9.13

### Command API

#### New Commands

| Command                   | Description                          |
| ------------------------- | ------------------------------------ |
| `rotate_textured_quad_to` | Set the rotation of a textured quad. |

## v1.9.12

### New Features

- **Added Obi fluids to TDW.** This is a particle-based fluid simulator that in most respects is superior to the existing Flex fluid simulator.

### Command API

#### New Commands

| Command                            | Description                                             |
| ---------------------------------- | ------------------------------------------------------- |
| `create_floor_obi_colliders`       | Create Obi colliders for the floor if there aren't any. |
| `set_floor_obi_collision_material` | Set the Obi collision material of the floor.            |
| `create_obi_fluid`                 | Create an Obi fluid.                                    |
| `create_obi_solver`                | Create an Obi solver.                                   |
| `destroy_obi_solver`               | Destroy an Obi solver.                                  |
| `set_obi_solver_substeps`          | Set an Obi solver's number of substeps.                 |
| `create_obi_colliders`             | Create Obi colliders for an object if there aren't any. |
| `set_obi_collision_material`       | Set the Obi collision material of an object.            |
| `set_obi_fluid_emission_speed`     | Set the emission speed of a fluid emitter.              |
| `create_robot_obi_colliders`       | Create Obi colliders for a robot if there aren't any.   |
| `set_robot_obi_collision_material` | Set the Obi collision material of a robot.              |
| `send_obi_particles`               | Send particle data for all Obi actors in the scene.     |
| `create_vr_obi_colliders`          | Create Obi colliders for a VR rig if there aren't any.  |
| `set_vr_obi_collision_material`    | Set the Obi collision material of the VR rig.           |

#### Deprecated Commands

| Command                                                      | Reason                                                   |
| ------------------------------------------------------------ | -------------------------------------------------------- |
| `set_flex_fluid_actor`<br>`set_flex_fluid_source_actor`<br>`load_flex_fluid_from_resources`<br>`load_flex_fluid_source_from_resources` | Flex fluids have been deprecated in favor of Obi fluids. |

### Output Data

#### New Output Data

| Output Data    | Description        |
| -------------- | ------------------ |
| `ObiParticles` | Obi particle data. |

### `tdw` module

- Added `Obi` add-on. This add-on handles most aspects of an Obi physics simulation, including initialization, actor creation, and particle output data.
- Added Obi data classes for usage within the `Obi` add-on:
  - `ObiActor` Handles particle data per Obi actor.
  - Fluids:
    - `FluidBase` Abstract base class for fluids.
    - `Fluid` Includes a dictionary of presets: `from tdw.obi_data.fluids.fluid import FLUIDS`
    - `GranularFluid` Includes a dictionary of presets: `from tdw.obi_data.fluids.granular_fluid import GRANULAR_FLUIDS`
  - Emitter shapes:
    - `EmitterShape` Abstract base class for emitter shapes.
    - `CubeEmitter`
    - `DiskEmitter`
    - `EdgeEmitter`
    - `SphereEmitter`
    - `EmitterSamplingMethod` Enum values for the emitter sampling method.
  - Collision materials:
    - `CollisionMaterial`
    - `MaterialCombineMode`
- Fixed: `AssetBundleCreator` fails because the `asset_bundle_creator/` Unity project doesn't include Newtonsoft.JSON
- By default, the `OculusTouch` add-on will set the rig's hands and all graspable objects to the "discrete" collision detection mode.

### Model Library

- Marked models as do_not_use: 03_106, 07_01_001, 11_02_003, 11_02_046, 2012-2, adirondack_chair, animal_dog_rtstand_1281, apple04(8_vray), apple07(8_vray), b03_bosch_cbg675bs1b_2013__vray_composite, b03_calligraphybrush_circle, b03_fire_hydrant_los_angeles(1), b05_025_vray, b05_clochild4, banana, bananas(8_vray), billiardtable, brush_circle, cgaxis_models_88_21_vray, coca-cola_can_001, db_apps_tech_08_10, de_dietrich_dop7350w, elva_camod_5691_141x51xh87, fire_hydrant, giraffe_mesh, golf_cart, hair_comb_2010, holo3d-mesh-snake, honey_jar_max_2011, prim_cone, ramp_with_platform, snek_new, whirlpool_akzm7630ix

### Example Controllers

- Added: `obi/custom_fluid.py`, `obi/milk.py` `obi/obi_minimal.py`, `obi/obi_robot.py`, `obi/strawberry_jam.py`, `obi/water.py`

### Documentation

#### New Documentation

| Document                                                     | Description                                                  |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| `lessons/obi/overview.md`<br>`lessons/obi/fluids.md`<br>`lessons/obi/obi_particles.md`<br>`lessons/obi/colliders_and_collision_materials.md`<br>`lessons/obi/solvers.md`<br>`lessons/obi/robots.md`<br>`lessons/obi/obi_and_flex.md` | Tutorial documentation for Obi in TDW.                       |
| `python/add_ons/obi.md`<br>`python/obi_data/collision_materials/collision_material.md`<br>`python/obi_data/collision_materials/material_combine_mode.md`<br>`python/obi_data/fluids/cube_emitter.md`<br>`python/obi_data/fluids/disk_emitter.md`<br>`python/obi_data/fluids/edge_emitter.md`<br>`python/obi_data/fluids/emitter_sampling_method.md`<br>`python/obi_data/fluids/emitter_shape.md`<br>`python/obi_data/fluids/fluid.md`<br>`python/obi_data/fluids/fluid_base.md`<br>`python/obi_data/fluids/granular_fluid.md`<br>`python/obi_data/fluids/sphere_emitter.md`<br>`python/obi_data/obi_actor.md` | API documentation for the `Obi` add-on and associated data classes. |

#### Modified Documentation

| Document                           | Modification                                   |
| ---------------------------------- | ---------------------------------------------- |
| `lessons/flex/fluid_and_source.md` | Added deprecation notice.                      |
| `lessons/physx/overview.md`        | Updated comparison section to include Obi.     |
| `lessons/vr/oculus_touch.md`       | Added a section regarding physics glitchiness. |

### Benchmarking

- Added: `flex_fluid.py`, `obi.py`, and `obi_fluid.py`
- Added Obi benchmark to `performance_benchmark_controller.py

## v1.9.11

### Command API

#### New Commands

| Command                       | Description                                                  |
| ----------------------------- | ------------------------------------------------------------ |
| `set_floor_color`             | Set the albedo color of the floor.                           |
| `set_floor_material`          | Set the material of the floor.                               |
| `set_floor_texture_scale`     | Set the scale of the tiling of the floor material's main texture. |
| `set_floor_physic_material`   | Set the physic material of the floor.                        |
| `send_collider_intersections` | Send data for collider intersections between pairs of objects and between single objects and the environment (e.g. walls). Note that each intersection is a separate output data object, and that each pair of objects/environment meshes might intersect more than once because they might have more than one collider. |

#### Modified Commands

| Command             | Modification                                                 |
| ------------------- | ------------------------------------------------------------ |
| `send_model_report` | Added a test for whether each MeshCollider has a mesh.<br>Added a test for whether each MeshCollider's mesh is readable. |

#### Deprecated Commands

| Command                            | Reason                                   |
| ---------------------------------- | ---------------------------------------- |
| `set_proc_gen_floor_color`         | Replaced with `set_floor_color`.         |
| `set_proc_gen_floor_material`      | Replaced with `set_floor_material`.      |
| `set_proc_gen_floor_texture_scale` | Replaced with `set_floor_texture_scale`. |

### Output Data

#### New Output Data

| Output Data                       | Description                                                  |
| --------------------------------- | ------------------------------------------------------------ |
| `EnvironmentColliderIntersection` | Data for an whose colliders are intersecting with an environment collider such as a wall. |
| `ObjectColliderIntersection`      | Data for two objects whose colliders are intersecting.       |

### Example Controllers

- Updated `objects_and_scenes/proc_gen_room.py` to use the new floor commands.

### Documentation

#### Modified Documentation

| Document                                      | Modification                                         |
| --------------------------------------------- | ---------------------------------------------------- |
| `lessons/objects_and_scenes/proc_gen_room.md` | Replaced old floor commands with new floor commands. |

## v1.9.10

### Build

- Fixed: The OS X build doesn't use OpenGL rendering, causing _depth and _depth_simple passes to render as _img passes. (There were probably other OpenGL-related issues as well).

### Model Library

- Fixed: Removed cabinet_24_two_drawer_wood_beech_honey_composite record from the model librarian because the asset bundles don't exist.

## v1.9.9

### Command API

#### Modified Commands

| Command                 | Modification                            |
| ----------------------- | --------------------------------------- |
| `create_flex_container` | Added optional parameter `restitution`. |

### `tdw` module

- Added optional parameter `device_name` to `AudioUtils.start()` and `AudioUtils. get_system_audio_device()` to specify the capture device (such as a headset microphone).
- Added: `Logger.reset(path)` Reset the Logger add-on.
- Fixed: `Logger` add-on doesn't create directories for the log if the directories don't exist.
- Added optional parameter `scale_mass` to `Controller.get_add_physics_object()`. If False, scale an object without adjusting its mass.

### Documentation

#### Modified Documentation

| Document                           | Modification                                                 |
| ---------------------------------- | ------------------------------------------------------------ |
| `lessons/audio/record_audio.md`    | Added a section for how to record from a microphone.         |

## v1.9.8

### Command API

#### New Commands

| Command                 | Description                                                  |
| ----------------------- | ------------------------------------------------------------ |
| `scale_object_and_mass` | Scale the object by a factor from its current scale. Scale its mass proportionally. This command assumes that a canonical mass has already been set. |

### Build

- Removed warning in `scale_object` about Flex objects because `set_flex_scale` isn't a command.

### `tdw` module

- `Controller.get_add_physics_object()` will dynamically scale the "canonical" mass of the object if a value for the `scale_factor` parameter is provided.

### Model Library

- Added models `models_core.json` and `models_full.json`:  b03_cooking_pot_01_composite, fridge_large_composite (including container collider data)

### Documentation

#### Modified Documentation

- **Fixed: Missing information in various Python API documents.**

| Document                           | Modification                                                 |
| ---------------------------------- | ------------------------------------------------------------ |
| `lessons/flex/fluid_and_source.md` | Clarified that a receptacle is not needed.                   |
| `python/controller.md`             | Clarified how the wrapper functions that return commands work. |

## v1.9.7

### Command API

#### Modified Commands

| Command                | Modification                              |
| ---------------------- | ----------------------------------------- |
| `add_trigger_collider` | Added trigger collider shape `"cylinder"` |

### Build

- Fixed: DllNotFoundException in TDW.app (OS X) due to missing AudioPluginOculusSpatializer.bundle
- Fixed: Potential memory leak with audio commands

### `tdw` module

- Fixed: `struct.error` in `CompositeObjectManager` when deserializing static spring data.
- Added `TriggerCollisionManager` add-on. Manager per-frame trigger collision data.
- Added the following trigger collider/collision data classes:
  - `TriggerColliderShape` Enum describing the shape of the collider.
  - `TriggerCollisionEvent` Wrapper for trigger collision data.
- Added `ContainerManager` add-on. Manager per-frame containment data. This is a subclass of `TriggerCollisionManager`.
- Added the following container trigger collider/collision data classes:
  - `ContainerBoxTriggerCollider` Data for a box-shaped container trigger collider.
  - `ContainerColliderTag` Enum of semantic tags for container trigger colliders.
  - `ContainerCylinderTriggerCollider` Data for a cylinder-shaped container trigger collider.
  - `ContainerNonUniformScaleTriggerCollider` Abstract class for container trigger colliders with non-uniform scales.
  - `ContainerSphereTriggerCollider` Data for a sphere-shaped container trigger collider.
  - `ContainerTriggerCollider` Abstract base class for container trigger collider data.
  - `ContainmentEvent` Wrapper for containment trigger collision data.
- Fixed: AssertionError `AssetBundleCreator` and `RobotCreator` if `unity_editor_path` is set in the constructor but `asset_bundle_creator/` project path doesn't yet exist.

### Model Library

- Added cached trigger collision data to model records. Not all records have container trigger colliders; see `model_record.trigger_colliders`.
  - (Backend) Added: `tdw.librarian._Encoder` JSONEncoder extension that is used within `_Librarian` classes. For now, this just handles container collider data.
- Added models `models_core.json` and `models_full.json`: cabinet_36_two_door_wood_oak_white_composite, cabinet_36_two_door_wood_beech_honey_composite, cabinet_24_wall_wood_beech_honey_composite, cabinet_24_wall_wood_oak_white_composite, cabinet_36_wall_wood_beech_honey_composite, cabinet_36_wall_wood_oak_white_composite, appliance-ge-profile-microwave3_composite, appliance-ge-profile-microwave_composite, microwave_composite

### Example Controllers

- Moved composite object controllers from `physx/` to `semantic_states/`
- Moved overlap and raycast controllers from `objects_and_scenes/` to `semantic_states/`
- Added: `semantic_states/containment.py`
- Added: `semantic_states/trigger_collisions.py`
- Fixed: `objects_and_scenes/floorplan.py` doesn't hide the roof.

### Documentation

#### New Documentation

| Document                                                     | Description                                                 |
| ------------------------------------------------------------ | ----------------------------------------------------------- |
| `lessons/semantic_states/containment.md`                     | Documentation for how to use the `ContainerManager`.        |
| `lessons/semantic_state/grasped.md`                          | Overview of "grasped" semantic states with various agents.  |
| `lessons/semantic_states/overview.md`                        | Overview of semantic states.                                |
| `lessons/semantic_states/trigger_collisions.md`              | Documentation for how to use the `TriggerCollisionManager`. |
| `python/add_ons/container_manager.md`                        | API documentation for `ContainerManager`.                   |
| `python/add_ons/trigger_collision_manager.md`                | API documentation for `TriggerCollisionManager`.            |
| `python/collision_data/trigger_collider_shape.md`<br>`python/collision_data/trigger_collision_event.md` | API documentation for trigger collision data classes.       |
| `python/container_data/container_box_trigger_collider.md`<br>`python/container_data/container_collider_tag.md`<br>`python/container_data/container_cylinder_trigger_collider.md`<br>`python/container_data/container_non_uniform_scale_trigger_collider.md`<br>`python/container_data/container_sphere_trigger_collider.md`<br>`python/container_data/container_trigger_collider.md`<br>`python/container_data/containment_event.md` | API documentation for containment data classes.             |


#### Modified Documentation

| Document                                | Modification                                             |
| --------------------------------------- | -------------------------------------------------------- |
| `lessons/objects_and_scenes/raycast.md` | Moved to: `lessons/semantic_states/raycast.md`           |
| `lessons/objects_and_scenes/overlap.md` | Moved to: `lessons/semantic_states/overlap.md`           |
| `lessons/physx/composite_objects.md`    | Moved to: `lessons/semantic_states/composite_objects.md` |

## v1.9.6

### Command API

#### Modified Commands

| Command              | Modification                                                 |
| -------------------- | ------------------------------------------------------------ |
| `send_audio_sources` | Removed optional parameter `ids` because it was non-functional. |

### Output Data

#### New Output Data

| Output Data       | Description                                                  |
| ----------------- | ------------------------------------------------------------ |
| `AudioSourceDone` | Output data that announces that an audio source is done playing. |

### `tdw` module

- Fixed: Error when initializing `PyImpact` if there isn't a VR rig in the scene.
- Fixed: `send_audio_sources` checks for object IDs instead of audio source IDs and therefore doesn't work.
- Fixed: `PyImpact` doesn't play valid impact audio events. Now, it uses `AudioSourceDone` output data to check the time between impact events.
  - Added optional parameter `min_time_between_audio_events` to the constructor.
- Fixed: `PyImpact` doesn't calculate `size` values accurately. Added `PyImpact.get_size(model)`.

### Example Controllers

- Fixed: TypeError in `fluid.py`

### Documentation

#### Modified Documentation

| Document                              | Modification                                               |
| ------------------------------------- | ---------------------------------------------------------- |
| `lessons/audio/py_impact.md`          | Added a section regarding `min_time_between_impact_events` |
| `lessons/audio/py_impact_advanced.md` | Added better guidance for how to set `size` values.        |

## v1.9.5

### New Features

- **Added support for the Oculus Quest 2 with Touch controllers.**

### Command API

#### New Commands

| Command                          | Description                                                  |
| -------------------------------- | ------------------------------------------------------------ |
| `send_static_composite_objects`  | Send static data for every composite object in the scene.    |
| `send_dynamic_composite_objects` | Send dynamic data for every composite object in the scene.   |
| `rotate_vr_rig`                  | Rotate the VR rig by an angle.                               |
| `set_vr_resolution_scale`        | Controls the actual size of eye textures as a multiplier of the device's default resolution. |
| `send_oculus_touch_buttons`      | Send data for buttons pressed on Oculus Touch controllers.   |
| `send_static_oculus_touch`       | Send static data for the Oculus Touch rig.                   |

#### Modified Commands

| Command         | Modification                                                 |
| --------------- | ------------------------------------------------------------ |
| `create_vr_rig` | Added parameter `rig_type`: The type of VR rig to instantiate.<br>Added parameter `sync_timestep_with_vr`: Whether to sync Time.fixedDeltaTime with the VR device refresh rate. Doing this improves physics behavior in VR; this parameter should almost always be True. |
| `set_graspable` | Renamed to `set_vr_graspable`<br>Added parameter `joint_break_force`: The joint break force for this graspable object. Lower values mean it's easier to break the joint. |

#### Deprecated Commands 

| Command                  | Reason                                                       | 
| ------------------------ | ------------------------------------------------------------ | 
| `send_composite_objects` | Replaced with `send_static_composite_objects` and `send_dynamic_composite_objects` | 

### Output Data 

#### New Output Data 

| Output Data               | Description                                              |
| ------------------------- | -------------------------------------------------------- |
| `CompositeObjectsStatic`  | Static composite object data.                            |
| `CompositeObjectsDynamic` | Dynamic composite object data.                           |
| `OculusTouchButtons`      | Which Oculus Touch controller buttons have been pressed. |
| `StaticOculusTouch`       | Static data for the Oculus Touch rig.                    |

#### Modified Output Data

| Output Data | Modification                                                 |
| ----------- | ------------------------------------------------------------ |
| `VRRig`     | Added: `get_held_left()` Returns the IDs of the objects held by the left hand.<br>Added: `get_held_right()` Returns the IDs of the objects held by the right hand. |

#### Deprecated Output Data 

| Output Data        | Reason                                                       | 
| ------------------ | ------------------------------------------------------------ | 
| `CompositeObjects` | Replaced with `CompositeObjectsStatic` and `CompositeObjectsDynamic` | 

### `tdw` module

- Added: `OculusTouch` an add-on for the Oculus Touch VR rig.
  - Added abstract base class `VR`
- Added the following VR data classes:
  - `OculusTouchButton` Enum values for Oculus Touch buttons.
  - `RigType` Enum values for VR rigs.
- Added: `CompositeObjectManager` an add-on for managing composite object data. 
- Added the following composite object data classes: 
  - `CompositeObjectStatic` Static data for a composite object and its sub-objects. 
    - `LightStatic` Static data for a light sub-object of a composite object. 
    - `MotorStatic` Static data for a motor sub-object of a composite object. 
    - `SpringStatic` Static data for a spring sub-object of a composite object. 
    - `HingeStatic` Static data for a hinge sub-object of a composite object. 
    - `PrismaticJointStatic` Static data for a prismatic joint sub-object of a composite object. 
    - `NonMachineStatic` Static data for a non-machine sub-object of a composite object. 
  - `CompositeObjectDynamic` Dynamic data for a composite object and its sub-objects. 
    - `LightDynamic` Dynamic data for a light sub-object of a composite object. 
    - `HingeDynamic` Dynamic data for a hinge, motor, or spring sub-object of a composite object. 
- `PyImpact` will create impact sounds for VR nodes (e.g. hands).
  - Added: `VR_HUMAN_MATERIAL` and `VR_HUMAN_BOUNCINESS`
- Fixed some bad-sound scrape materials in `PyImpact`: `sandpaper`, `vinyl`, and `poplar_wood`
- Fixed: `InteriorSceneLighting` sets the random number generator incorrectly such that all other attempts to create a numpy RandomState fail.
- Fixed: `TDWUtils.set_default_libraries()` raises an exception if `model_library` isn't set and one of the set paths is a string.
- Fixed: `AssetBundleCreator.write_physics_quality()` resets remote URLs for Windows asset bundles.

### Model library

- Added models `models_core.json` and `models_full.json`: b03\_aluminum\_pan\_composite, b03\_ka90ivi20r\_2013\_\_vray\_composite, b04\_db\_apps\_tech\_08\_03\_composite, cabinet\_24\_single\_door\_wood\_beech\_honey\_composite, cabinet\_24\_single\_door\_wood\_oak\_white\_composite, cabinet\_24\_two\_door\_wood\_beech\_honey\_composite, cabinet\_24\_two\_door\_wood\_oak\_white\_composite, cabinet\_full\_height\_wood\_beech\_honey\_composite, cabinet\_full\_height\_wood\_oak\_white\_composite, db\_apps\_tech\_08\_10\_composite, dishwasher\_4\_composite, gas\_stove\_composite, kenmore\_refr\_74049\_composite, pot\_composite, sink\_cabinet\_unit\_wood\_beech\_honey\_chrome\_composite, sink\_cabinet\_unit\_wood\_beech\_honey\_porcelain\_composite, sink\_cabinet\_unit\_wood\_oak\_white\_chrome\_composite, sink\_cabinet\_unit\_wood\_oak\_white\_porcelain\_composite, vm\_v5\_070\_composite, vray\_062\_composite

### Build

- Dropped support for Flex in VR (this never worked very well).

### Example Controllers

- Edited `physx/composite_object.py` to use the `CompositeObjectManager`
- Removed `physx/kinematic_composite_object.py`
- Added `physx/composite_object_open.py`
- Added `physx/composite_object_torque.py`
- Moved `humans/keyboard_controls.py` to `keyboard/keyboard_controls.py`
- Moved `humans/keyboard_minimal.py` to `keyboard/keyboard_minimal.py`
- Removed `humans/vr_minimal.py` 
- Removed `humans/vr_observed_objects.py`
- Added `vr/oculus_touch_button_listener.py`
- Added `vr/oculus_touch_composite_object.py`
- Added `vr/oculus_touch_image_capture.py`
- Added `vr/oculus_touch_minimal.py` 
- Added `vr/oculus_touch_output_data.py`
- Added `vr/oculus_touch_py_impact.py`

### Documentation 

#### New Documentation 

| Document                                                     | Description                                                |
| ------------------------------------------------------------ | ---------------------------------------------------------- |
| `python/add_ons/composite_object_manager.md`                 | API document for `CompositeObjectManager`                  |
| `python/object_data/composite_object/composite_object_static.md`<br>`python/object_data/composite_object/composite_object_dynamic.md`<br>`python/object_data/composite_object/sub_object/sub_object_static.md`<br>`python/object_data/composite_object/sub_object/light_static.md`<br>`python/object_data/composite_object/sub_object/hinge_static_base.md`<br>`python/object_data/composite_object/sub_object/motor_static.md`<br>`python/object_data/composite_object/sub_object/spring_static.md`<br>`python/object_data/composite_object/sub_object/hinge_static.md`<br>`python/object_data/composite_object/sub_object/prismatic_joint_static.md`<br>`python/object_data/composite_object/sub_object/non_machine_static.md`<br>`python/object_data/composite_object/sub_object/sub_object_dynamic.md`<br>`python/object_data/composite_object/sub_object/light_dynamic.md`<br>`python/object_data/composite_object/sub_object/hinge_dynamic.md` | API documents for composite object data classes.           |
| `lessons/vr/overview.md`                                     | Overview of VR.                                            |
| `lessons/vr/oculus_touch.md`                                 | Tutorial on the Oculus Touch rig and `OculusTouch` add-on. |
| `python/add_ons/oculus_touch.md`                             | API document for `OculusTouch` add-on.                     |
| `python/add_ons/vr.md`                                       | API document for `VR` abstract class.                      |
| `python/vr_data/oculus_touch_button`<br>`python/vr_data/rig_type.md` | API documents for VR data classes.                         |

#### Modified Documentation 

| Document                             | Modification                                                 |
| ------------------------------------ | ------------------------------------------------------------ |
| `lessons/physx/composite_objects.md` | Rewrote most of the document to explain how to use the `CompositeObjectManager`.<br>Added a section explaining how to determine if an object is "open".<br>Clarified the difference between sub-meshes and sub-objects.<br>Added more example code. |
| `lessons/agents/overview.md`         | Split "Humans" section into "Keyboard controls" and "VR".    |
| `lessons/humans/keyboard.md`         | Moved to: `lessons/keyboard/keyboard.md`                     |

#### Removed Documentation

| Document               | Reason                                          |
| ---------------------- | ----------------------------------------------- |
| `lessons/humans/vr.md` | Replaced with new VR documentation (see above). |

## v1.9.4

### Command API

#### New Commands

| Command                      | Description                          |
| ---------------------------- | ------------------------------------ |
| `set_spring_target_position` | Set the target position of a spring. |
| `set_spring_damper`          | Set the damper value of a spring.    |
| `set_spring_force`           | Set the force of a spring.           |
| `set_motor_target_velocity`  | Set the target velocity of a motor.  |
| `set_motor_force`            | Set the force of a motor.            |

#### Removed Commands

| Command      | Reason                                                       |
| ------------ | ------------------------------------------------------------ |
| `set_spring` | Replaced with `set_spring_target_position`                   |
| `set_motor`  | Replaced with `set_motor_target_velocity` and `set_motor_force` |

### `tdw` module

- Fixed: Can't override the visual materials of scrape surfaces in `PyImpact`
- Added: `TDWUtils.get_segmentation_colors(id_pass)`. Returns a list of unique colors in the ID pass. 
- Added: `TDWUtils.download_asset_bundles(path, models, scenes, materials, hdri_skyboxes, robots, humanoids, humanoid_animations)` 
- Added: `TDWUtils.set_default_libraries(model_library=None, scene_library=None, material_library=None, hdri_skybox_library=None, robot_library=None, humanoid_library=None, humanoid_animation_library=None)` Set the path to the default libraries.

### Model library

- Flagged models as do_not_use in `models_core.json` and `models_full.json`:  b03_object05, b03_pot, b05_ikea_nutid_side_by_side_refrigerator

### Documentation

#### New Documentation

| Document                                 | Description                            |
| ---------------------------------------- | -------------------------------------- |
| `lessons/misc/download_asset_bundles.md` | How and why to download asset bundles. |

## v1.9.3

### Command API

#### New Commands

| Command                                | Description                                                  |
| -------------------------------------- | ------------------------------------------------------------ |
| `set_composite_object_kinematic_state` | Set the top-level Rigidbody of a composite object to be kinematic or not. Optionally, set the same state for all of its sub-objects. A kinematic object won't respond to PhysX physics. |
| `add_compass_rose`                     | Add a visual compass rose to the scene. It will show which way is north, south, etc. as well as positive X, negative X, etc. |
| `destroy_compass_rose`                 | Destroy a compass rose in the scene.                         |
| `add_line_renderer`                    | Add a 3D line to the scene.                                  |
| `add_points_to_line_renderer`          | Add points to an existing line in the scene.                 |
| `destroy_line_renderer`                | Destroy an existing line in the scene from the scene.        |
| `remove_points_from_line_renderer`     | Remove points from an existing line in the scene.            |
| `simplify_line_renderer`               | Simplify a 3D line to the scene by removing intermediate points. |

#### Modified Commands

| Command               | Description                                                  |
| --------------------- | ------------------------------------------------------------ |
| `set_kinematic_state` | For composite objects, this sets the state only for the top-level object (previous,  it set the state for all sub-objects as well). See: `set_composite_object_kinematic_state` |

### `tdw` module

- Added: `OccupancyMap.reset()` Reset the occupancy map. Call this when resetting a scene.
- Replaced `ThirdPersonCamera.look_at_target` with  `ThirdPersonCamera.look_at(target)` in order to allow the camera to look at a target on the next `communicate()` call.
- Improved how cross-fading works in `PyImpact` between audio chunks during a scrape.
- Added: `InteriorSceneLighting` Add an HDRI skybox to the scene from a curated list of skyboxes and set post-processing values.
- Fixed: `AudioUtils` (and, by extension, `PhysicsAudioRecorder`) doesn't work on OS X.

### Model library

- Flagged models as do_not_use in `models_full.json`: b03_radiator_old, b05_ikea_nutid_side_by_side_refrigerator
- Added to `models_core.json`:  b03_radiator_alum_12, b05_castironradiator, radiator_pub_2015, fredericia_spine_stool_1, mater_high_stool_al_69, tolix_bar_stool

### Example controllers

- Added: `non_physics/compass_rose.py`
- Added: `non_physics/line_renderer.py`

### Documentation

#### New Documentation

| Documentation                               | Description                                                  |
| ------------------------------------------- | ------------------------------------------------------------ |
| `lessons/non_physics/compass_rose.md`       | Tutorial document explaining the compass rose.               |
| `lessons/non_physics/line_renderers.md`     | Tutorial document explaining line renderers.                 |
| `lessons/photorealism/interior_lighting.md` | Tutorial document explaining how to use the new `InteriorSceneLighting` add-on. |
| `python/add_ons/interior_scene_lighting.md` | API document for `InteriorSceneLighting`.                    |

#### Modified Documentation

| Document                                                  | Modification                                                 |
| --------------------------------------------------------- | ------------------------------------------------------------ |
| `lessons/physx/composite_objects.md`                      | Clarified how to use various means to set kinematic states of sub-objects. |
| `lessons/navigation/occupancy_maps.md`                    | Added a section for resetting a scene.                       |
| `lessons/photorealism/lighting.md`                        | Added an example of how to convert the HDRI skybox library data to a .csv file. |
| `lessons/objects_and_scenes/materials_textures_colors.md` | Added a missing line of code in one of the examples.         |
| `lessons/audio/recording_audio.md`                        | Added instructions for installing fmedia on all platforms (including OS X) |
| `lessons/troubleshooting/common_errors.md`                | Added a section for low render quality.                      |

## v1.9.2

### Command API

#### New Commands

| Command                   | Description                                                  |
| ------------------------- | ------------------------------------------------------------ |
| `parent_object_to_object` | Parent an object to an object. In a non-physics simulation or on the frame that the two objects are first created, rotating or moving the parent object will rotate or move the child object. In subsequent physics steps, the child will move independently of the parent object (like any object). |
| `set_hinge_limits` | Set the angle limits of a hinge joint. This will work with hinges, motors, and springs. |
| `set_object_physics_solver_iterations` | Set the physics solver iterations for an object, which affects its overall accuracy of the physics engine. |

#### Modified Commands

| Command             | Modification                                                 |
| ------------------- | ------------------------------------------------------------ |
| `send_model_report` | Added tests for prismatic joint mechanisms (ConfigureableJoint components) |

### `tdw` module

- Added optional parameter `unity_editor_path` to the `AssetBundleCreator`constructor to optionally explicitly set the path to the Unity Editor executable.
- Added: `AssetBundleCreator.cleanup()` Clean up intermediary files.
- Added optional parameter `unity_editor_path` to the `RobotCreator`constructor to optionally explicitly set the path to the Unity Editor executable.
- Changed the names of all undocumented fields in `AssetBundleCreator` and `RobotCreator` to private (added an `_` to the start of the variable names).
- Added optional parameters `description_infix` and `branch` to `RobotCreator.create_asset_bundles()` to handle unexpected .urdf URLs.

### Build

- Added new composite object mechanism type: `prismatic_joint`

### Model Library

- Added to `models_core.json`: large_mesh_basket, trashbin, b04_11_02_041, b04_kevin_reilly_pattern_floor_lamp, duncan_floor_lamp_crate_and_barrel, b03_restoration_hardware_pedestal_salvaged_round_tables, b04_03_077, gas_stove

### Robot Library

- Fixed various issues with fetch robot's wheels:
  - Added four revolute joints for the non-motorized wheels: non_motorized_wheel_front_left, non_motorized_wheel_front_right, non_motorized_wheel_back_left, non_motorized_wheel_back_right.
  - Removed bellows_link_2 as a joint (it was causing fetch to turn and was otherwise non-functional) but kept the visual mesh.
  - Removed estop_link as a joint (it didn't do anything) but kept the visual mesh.
  - Removed laser_link fixed joint and visual mesh (it didn't do anything).

### Example Controllers

- Added: `physx/kinematic_composite_object.py`

### Documentation

#### Modified Documentation

| Document                             | Modification                                                 |
| ------------------------------------ | ------------------------------------------------------------ |
| `lessons/physx/composite_objects.md` | Added example code for setting kinematic states of sub-objects. |
| `lessons/3d_models/custom_models.md` | Added a section regarding .fbx unit scales; .fbx files must be in meters.<br>Added a section explaining how to manually set the Unity Editor path. |
| `lessons/robots/custom_robots.md`    | Added a section explaining how to manually set the Unity Editor path. |

#### Removed Documentation

| Document                                         | Reason                                                       |
| ------------------------------------------------ | ------------------------------------------------------------ |
| `composite_objects/creating_composite_object.md` | This is not a feature we expect most users to be able to do because it requires Unity Editor experience. This document has been edited and moved to the private TDWBase repo. |

## v1.9.1

### Command API

#### New Commands

| Command          | Description             |
| ---------------- | ----------------------- |
| `stop_all_audio` | Stop all ongoing audio. |
| `rotate_object_around` | Rotate an object by an angle and axis around a position. |

#### Modified Commands

| Command                       | Modification                                                 |
| ----------------------------- | ------------------------------------------------------------ |
| `rotate_directional_light_by` | The directional light rotates within the local coordinate space (not the world coordinate space). |

### `tdw` module

- Fixed: `PyImpact` seems to be "missing" impact sounds because roll sounds haven't been implemented yet. Now, all "roll" events are handled as "impact events".
- Fixed: `PyImpact.reset()` doesn't stop ongoing audio.
- Fixed: `PyImpact` scrape sounds are often rougher-sounding than they should be (`PyImpact` now uses smoother-sounding scrape materials).
- Replaced `resonance` parameter in all `PyImpact` functions with `primary_resonance` and `secondary_resonance` parameters.
- Adjusted some default static object audio values.
- Added: `TDWUtils.bytes_to_megabytes(b)` Convert a quantity of bytes to a quantity of megabytes.
- Added: `TDWUtils.get_circle_mask(arr, row, column, radius)`. Get elements in an array within a circle.
- Added: `QuaternionUtils.is_left_of(origin, target, forward)` Returns True if `target` is to the left of `origin` otherwise returns False.
- Modifed `TDWUtils.get_bounds_extents`:
  - The function now accepts either `Bounds` output data or a cached bounds dictionary from `record.bounds` (in which case the `index` parameter is ignored).
  - The order of the returned array is: width, height, length (was width, length, height).
- Fixed: `TDWUtils.get_pil_images()` doesn't work for `_depth` or `_depth_simple`.


### Model library

- Added to `models_core.json`: apple, b03_banana_01_high, b04_banana, banana_fix2, cgaxis_models_65_06_vray, cgaxis_models_65_14_vray, b04_bottle-2014-2018, b04_bottle_2_max, int_kitchen_accessories_le_creuset_bowl_30cm, b03_loafbread, bread, b03_iron_candle_vray, b04_candle_holder_metal, b05_candles_max_vray2, b05_candlestick_with_candles002_max2017_vray, b05_cgaxis_models_37_17_vray, candles_max_vray, cgaxis_models_20_05_vray, cgaxis_models_37_15_vray, lantern_2010, chair_thonet_marshall, b05_snickers, chocolate_bar001, b05_coffee_grinder, cafe_2010, cgaxis_models_61_17_vray, coffee_grinder, kitchen_aid_coffee_grinder, b06_circle, ripple, coffeecup004_fix, cup, b03_db_apps_tech_08_04_composite, b03_db_apps_tech_08_07_composite, b03_db_apps_tech_08_08_composite, b04_db_apps_tech_08_03, b05_db_apps_tech_08_09, b05_db_apps_tech_08_09_composite, vray_032, pcylinder222, vk0010_dinner_fork_subd0, vk0011_dessert_fork_subd0, vk0056_tablefork, vk0067_fishfork, cgaxis_models_50_12_vray, cgaxis_models_50_24_vray, b04_3d_jar_180_gr_01, b04_honey_jar, b04_honey_jar_max_2014, b05_sugerjar_a001_2015, b03_pot, b04_low, stelton_emma_tea_vacuum_jug, vk0007_steak_knife, vk0014_dinner_knife_subd2, vk0055_tableknife, b03_bosch_cbg675bs1b_2013\_\_vray_composite, b05_whirlpool_microwave_wmc30516as_v-ray, cgaxis_models_10_11_vray, vm_v5_070, vray_062, b04_orange_00, orange, b03_696615_object001, b03_object05, int_kitchen_accessories_le_creuset_frying_pan_28cm, measuring_pan, object05, pan01, pan02, pan03, pan04, pan05, b03_pen, b05_ball-point_pen-obj, cylinder01, wooden_pepper_mill, plate05, plate06, plate07, b03_aluminum_pan, b03_cooking_pot_01, pan1, pan3, b03_ka90ivi20r_2013\_\_vray, b05_db_apps_tech_06_02_2, b05_ikea_nutid_side_by_side_refrigerator, b05_cylinder001, b03_burger, b04_scissors_2013, b05_bathroom_dispenser, b05_gold_glass_soap_dispenser(max), blue_edition_liquid_soap02, filler_2010, kosmos_black_soap_dispenser, soap_dispenser_01, b01_spatula, vk0002_teaspoon, vk0054_teaspoon, vk0058_tablespoon, vk0060_dessertspoon, vk0078_fruitspoon, vk0080_soupspoon, b05_beko_oie_22500x_2013\_\_corona, b05_dacor_double_wall_oven, b05_max2013vray_oven_by_whirlpool_akzm8910ixl, duhovka, vraymax2013_oven_akzm6610ixl_by_whirlpool, metal_lab_table, teatray, kettle_2, tea_kettle_model, teakettle_01, v3_tf_04_01, vray_041, vray_044, b05_delonghi_icona_toaster, b06_21_dualit_original_toaster_4x, russell_hobbs_2013\_\_vray, vray_077, vray_083, vray_084, vray_085, amphora_jar_vase, b04_new, vase_laura_deko_vase_set, b04_cantate_crystal_wine_glass, b04_wineglass
- Flagged models as do_not_use in `models_core.json`: coffeecup004, mug, salt
- Flagged models as do_not_use in `models_full.json`: coffeecup004, mug, salt, b03_closed_soda_can, b04_chocolate, b04_coffee_grinder_sunbeam_em0700, b04_glass, b04_whyskeyglass, b05_beko_oie_22500x_2013_corona, croissant, jar, peppermill, pineapple_juice, pineapple_juice_carton, spagheti-server, b03_can-opened,  b03_db_apps_tech_08_01

### Documentation

#### Modified Documentation

| Document                             | Modification                                                 |
| ------------------------------------ | ------------------------------------------------------------ |
| `lessons/3d_models/custom_models.md` | Fixed: Two of the example controllers don't work because they try to load JSON from the file path rather than the file text. |

## v1.9.0

### New Features

- **Added add-ons.** These objects can be appended to `Controller.add_ons` to inject commands per `communicate()` call. They've been designed to simplify common tasks in TDW such as capturing images per frame or logging commands per frame.
- **Completely rewrite of documentation.** All non-API documentation has been completely rewritten. Documentation is now divided into "lessons" for specified subjects such as robotics or visual perception. You can find the complete table of contents on the README. **Even if you are an experienced TDW user, we recommend you read our new documentation.** You might learn new techniques!
- **PyImpact is now an add-on and has scrape sounds.** [Read this for more information.](lessons/audio/py_impact.md)
- (External repo) **[Magnebot](https://github.com/alters-mit/magnebot) has been upgraded to version 2.0.** Magnebot can now be used as an add-on, meaning that it can be added to any TDW controller.

### Command API

#### New Commands

| Command                                    | Description                                                  |
| ------------------------------------------ | ------------------------------------------------------------ |
| `move_avatar_towards_object`               | Move the avatar towards an object.                           |
| `move_avatar_towards_position`             | Move the avatar towards the target position.                 |
| `focus_towards_object`                     | Focus towards the depth-of-field towards the position of an object. |
| `rotate_sensor_container_towards_object`   | Rotate the sensor container towards the current position of a target object. |
| `rotate_sensor_container_towards_position` | Rotate the sensor container towards a position at a given angular speed per frame. |
| `rotate_sensor_container_towards_rotation` | Rotate the sensor container towards a target rotation.       |
| `send_static_rigidbodies`                  | Request static rigidbody data (mass, kinematic state, etc.)  |
| `parent_audio_source_to_object`            | Parent an audio source to an object. When the object moves, the audio source will move with it. |
| `send_robot_joint_velocities`              | Send velocity data for each joint of each robot in the scene. This is separate from Robot output data for the sake of speed in certain simulations. |
| `attach_empty_object`                      | Attach an empty object to an object in the scene. This is useful for tracking local space positions as the object rotates. |
| `send_empty_objects`                       | Send data each empty object in the scene.                    |

#### Modified Commands

| Command                                                | Modification                                                 |
| ------------------------------------------------------ | ------------------------------------------------------------ |
| `play_audio_data`<br>`play_point_source_data`          | Parameter ID now refers to a unique ID for the audio source (not an object ID).<br>Added parameter `position`. |
| `set_reverb_space_expert`<br>`set_reverb_space_simple` | Renamed parameter `env_id` to `region_id`                    |
| `play_humanoid_animation`                              | Added optional parameter `framerate`                         |
| `send_model_report`                                    | Added parameter `flex`. If True, this model is expected to be Flex-compatible. |

#### Renamed Commands

| Command                          | New name                |
| -------------------------------- | ----------------------- |
| `send_environments`              | `send_scene_regions`    |
| `create_flex_fluid_object`       | `set_flex_fluid_actor`  |
| `create_flex_fluid_source_actor` | `set_flex_source_actor` |
| `create_painting`                 | `create_textured_quad`                       |
| `destroy_painting`                | `destroy_textured_quad`                      |
| `rotate_painting_by`              | `rotate_textured_quad_by`                    |
| `scale_painting`                  | `scale_textured_quad`                        |
| `set_painting_texture`            | `set_textured_quad`                          |
| `show_painting`                   | `show_textured_quad`                         |
| `teleport_painting`               | `teleport_textured_quad`                     |

#### Removed Commands

| Command                                                      | Reason                                                       |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| `set_proc_gen_reflection_probe`                              | Deprecated in v1.8; use `enable_reflection_probes` instead.  |
| `rotate_flex_object_by`<br>`rotate_flex_object_by_quaternion`<br>`teleport_and_rotate_flex_object`<br>`teleport_flex_object` | Flex objects should be teleported and rotated prior to enabling them for Flex. |
| `rotate_painting_to_euler_angles`                            | Redundant and can gimbal lock.                               |
| `hide_painting`                                              | Replaced with `show_textured_quad` (set `"show"` to False)   |

### Output Data

#### New Output Data

| Output Data            | Description                                         |
| ---------------------- | --------------------------------------------------- |
| `StaticRigidbodies`    | Static rigidbody data (mass, kinematic state, etc.) |
| `RobotJointVelocities` | Velocity for a robot in the scene.                  |
| `EmptyObjects`         | The position of each empty object in the scene.     |

#### Renamed Output Data

| Output Data    | New name       |
| -------------- | -------------- |
| `Environments` | `SceneRegions` |

#### Modified Output Data

| Output Data    | Modification                                                 |
| -------------- | ------------------------------------------------------------ |
| `AudioSources` | Added: `get_samples()`. Audio samples from the audio listener. |
| `Rigidbodies`  | Removed: `get_mass(index)`, `get_kinematic(index)`. These are now in `StaticRigidbodies`. |

### Build

- Adjusted avatar type `A_Simple_Body`:
  - Fixed: Avatar bodies are centered on the avatar's pivot as opposed to halfway above it (i.e. making the pivot of the avatar the bottom-center), thus causing the avatar to "pop" out of the ground when it is first created.
  - Fixed: The cube avatar requires much more torque to turn. Its box collider has been replaced with a cube collider.
- Fixed: Warnings when repeatedly sending `send_model_report` without first unloading the scene.
- Fixed: Asset bundle commands (`add_object`, `add_material`, etc.) log an error when the connection times out, causing the build to quit. Now, they log a warning, allowing the build to continue.
- Fixed: Asset bundle commands (`add_object`, `add_material`, etc.) log an error on a status code 429 (too many requests). Now, they try to wait for approximately 60 seconds before retrying the connection.
- Updated Unity Engine from 2020.2.7f1 to 2020.3.24f1.

### `tdw` module

- **Added the following add-ons:**
  - `AudioInitializer` Initialize standard (Unity) audio. 
  - `Benchmark` Benchmark the FPS over a given number of frames.
  - `CinematicCamera` Wrapper class for third-person camera controls in TDW. These controls are "cinematic" in the sense that the camera will move, rotate, etc. towards a target at a set speed per frame. The `CinematicCamera` class is suitable for demo videos of TDW, but not for most actual experiments.
  - `CollisionManager` Manager add-on for all collisions on this frame.
  - `EmbodiedAvatar` Wrapper add-on for the `A_Simple_Body` avatar.
  - `Floorplan` Initialize a scene populated by objects in pre-scripted layouts.
  - `ImageCapture` Request image data and save the images to disk.
  - `Keyboard` Add keyboard controls to a TDW scene.
  - `Logger` Record and playback every command sent to the build.
  - `ObjectManager` A simple manager class for objects in the scene. This add-on can cache static object data (name, ID, etc.) and record dynamic data (position, velocity, etc.) per frame.
  - `OccupancyMap` Generate an occupancy map of the scene at runtime.
  - `PhysicsAudioRecorder` Record audio generated by physics events.
  - `PyImpact` Generate physics-based audio at runtime. 
  - `ResonanceAudioInitializer` Initialize Resonance Audio. 
  - `Robot` Control the joints of a robot.
  - `RobotArm` Control a robot with inverse kinematics (IK).
  - `StepPhysics` Step n+1 physics frames per communicate() call.
  - `ThirdPersonCamera` Add a third-person camera to the scene.
- Removed: `TransformInitData`, `RigidbodyInitData`, and `AudioInitData`.
- Added audio classes: 
  - `CollisionAudioEvent` Data for a collision audio event. 
  - `CollisionAudioInfo` Class containing information about collisions required by PyImpact to determine the volume of impact sounds. 
  - `CollisionAudioType` The "type" of a collision, defined by the motion of the object. 
  - `ScrapeMaterial` The scrape material type. 
  - `ScrapeModel` Data for a 3D model being used as a PyImpact scrape surface. 
  - `ScrapeSubObject` Data for a sub-object of a model being used as a scrape surface. 
  - Moved audio classes `AudioMaterial`, `Base64Sound` and `Modes` from `tdw.py_impact` to `tdw.physics_audio.audio_material`, `tdw.physics_audio.base64_sound`, and `tdw.physics_audio.modes` 
  - Renamed `ObjectInfo` to `ObjectAudioStatic` and moved it from `tdw.py_impact` to `tdw.physics_audio.object_audio_static` 
- Added backend object data classes:
  - `Transform` Transform data (position, forward, rotation).
  - `Rigidbody` Dynamic rigidbody data (velocity, angular velocity, sleeping).
  - `Bound` Dynamic bounds data for a single object (as opposed to `Bounds` output data).
  - `ObjectStatic` Static object data (name, mass, etc.).
- Added backend robot data classes:
  - `Drive` Static data for a joint drive.
  - `JointDynamic` Dynamic data for a joint.
  - `JointStatic` Static data for a joint.
  - `NonMoving` Static data for a non-joint body part of a robot.
  - `RobotDynamic` Dynamic data for a robot.
  - `RobotStatic` Static data for a robot.
  - `JointType` The type of joint, e.g. `revolute`.
- Removed `DebugController` (replaced with `Logger` add-on)
- Removed `KeyboardController` (replaced with `Keyboard` add-on)
- Removed `FloorplanController` (replaced with `Floorplan` add-on)
- Moved `CollisionObjObj` and `CollisionObjEnv` from `tdw.collision` to `tdw.collision_data`
  - Removed `collisons.py`
- Made more objects in the floorplan layouts kinematic.
- Moved `AudioUtils` from `tdw.tdw_utils` to `tdw.audio_utils` 
- Added: `AudioConstants` Various audio constants. 
- Added: `RemoteBuildLauncher`
- (Backend) Added `ModelVerifier` add-on plus the following `ModelTest` classes:
  - `ModelReport`
  - `PhysicsQuality`
  - `MissingMaterials`
- Moved `tdw.flex.fluid_types.FluidType` to `tdw.flex_data.fluid_type.FluidType`
- Removed `tdw.flex.fluid_types.FluidTypes` Default fluid type data is now stored in a dictionary: `tdw.flex_data.fluid_type.FLUID_TYPES`
- Updated `asset_bundle_creator`. To upgrade: Delete `~/asset_bundle_creator` (assuming that it exists). It will be re-created next time you create a model asset bundle.
- Updated `robot_creator`. To upgrade: Delete `~/robot_creator` (assuming that it exists). It will be re-created next time you create a robot asset bundle.

#### `Controller`

- **Added: `Controller.add_ons`** A list of add-ons that will inject commands every time `communicate()` is called.
- **Removed: `Controller.start()`** The command it used to send is automatically sent in the Controller constructor. 
- **Removed: `Controller.add_object(model_name)`** Use `Controller.get_add_object(model_name)` instead.
- **Removed: `Controller.load_streamed_scene(scene)`** Use `Controller.get_add_scene(scene_name)` instead.
- Removed `check_build_process` from the constructor because it's too slow to be useful.
- Added: `self.get_add_physics_object()`.  Add an object to the scene with physics values (mass, friction coefficients, etc.).
- Added: `DEFAULT_PHYSICS_VALUES`. A dictionary of default `ObjectInfo` per object. This corresponds to `PyImpact.get_object_info()`.
- Removed all cached librarian fields (`self.model_librarian`, `self.scene_librarian`, etc.) and replaced them with class variable dictionaries that automatically cache librarians (`Controller.MODEL_LIBRARIANS`, `Controller.SCENE_LIBRARIANS`, etc.) This allows multiple librarian objects to be cached at the same time and allows other classes to access them.
- All asset bundle wrapper functions (`get_add_object()`, `get_add_scene()`, etc.) are now static.

#### `TDWUtils`

- Fixed: Unhandled ZeroDivisionError  in `get_unit_scale(record)` if bounds are all 0 (if so, returns 1).

#### `PyImpact`

- **Complete refactor of PyImpact** 
  - PyImpact is now an add-on 
  - Small improvements to impact event detection 
  - Added scrape sounds 
- Added: `STATIC_FRICTION` and `DYNAMIC_FRICTION`. Dictionaries of friction coefficients per audio material.

#### `paths` (backend)

- Added: `EXAMPLE_CONTROLLER_OUTPUT_PATH`
- Removed: `VALIDATOR_REPORT_PATH`

#### Model Pipeline (backend)

- Removed: `model_pipeline/missing_materials.py`, `model_pipeline/validator.py`, `model_pipeline/write_physics_quality.py` (replaced with the `ModelVerifier` add-on)
  - Improved the accuracy of the physics quality test.

#### `SceneBounds` and `RoomBounds`

- Renamed `RoomBounds` to `RegionBounds`
- Moved `scene_bounds.py` and `room_bounds.py` from `scene/` to `scene_data/`.

### Model Library 

- Added `volume` field to each model record. 
- Copied models from models_full.json to models_core.json: bench, toy_monkey_medium, wood_board, metal_lab_shelf, skateboard_1, tray_02, b05_table_new, enzo_industrial_loft_pine_metal_round_dining_table,quatre_dining_table 
- Fixed: Some models that have ``flex` set to True in their records are not Flex-compatible. These models now have `flex` set to False.

### Use Cases

- Removed `single_object.py` and `multi_env.py`; they have been replaced with [`tdw_image_dataset`](https://github.com/alters-mit/tdw_image_dataset), a separate repo.
- Removed IntPhys demo.

### Benchmark

- Use the new `Benchmark` add-on for all benchmark controllers.
- Updated performance benchmarks. Removed obsolete tests.
- Added: `tdw.backend.performance_benchmark_controller.PerformanceBenchmarkController`

# v1.8.x

To upgrade from TDW v1.7 to v1.8, read [this guide](upgrade_guides/v1.7_to_v1.8.md).

## v1.8.29

### Command API

### New Commands

| Command                           | Description                                   |
| --------------------------------- | --------------------------------------------- |
| `send_material_properties_report` | Send a report of the material property values |

#### Modified Commands

| Command        | Modification                                     |
| -------------- | ------------------------------------------------ |
| `add_material` | Fixed: Transparent materials aren't transparent. |

### Material Library

- Fixed: Some variants/platform versions of glass_clear aren't transparent 

## v1.8.28

### Command API

#### Modified Commands

| Command                                       | Modification                                                 |
| --------------------------------------------- | ------------------------------------------------------------ |
| `play_audio_data`<br>`play_point_source_data` | Fixed: Unhandled exception if one of the objects is a robot joint. |
| `set_kinematic_state`                         | Fixed: If the object is a composite object, only the root object is set. |

### `tdw` module

#### `PyImpact`

- Added optional parameter `robot_joints` to `get_impact_sound_command()`. A list of known robot joints.
- If the controller has sent `send_robots` with frequency set to always, `PyImpact.get_audio_commands()` will automatically get a list of robot joint IDs and pass them to `get_impact_sound_command()`.

### Example controllers

- Added: `robot_impact_sound.py`

### Documentation

#### Modified Documentation

| Document                        | Modification                                                 |
| ------------------------------- | ------------------------------------------------------------ |
| `creating_composite_objects.md` | Fixed incorrect documentation regarding how joint chains should be set up. |

## v1.8.27

### Command API

#### New Commands

| Command | Description |
| --- | --- |
| `add_smpl_humanoid` | Add a parameterized humanoid to the scene using [SMPL](https://smpl.is.tue.mpg.de). Each parameter scales an aspect of the humanoid and must be between -1 and 1. For example, if the height is -1, then the humanoid will be the shortest possible height. Because all of these parameters blend together to create the overall shape, it isn't possible to document specific body shape values, such as overall height, that might correspond to this command's parameters. |

### Humanoid libraries

- Added: `smpl_humanoids.json` HumanoidLibrarian. There are two SMPL humanoid asset bundles in this library.

### Humanoid animation libraries:

- Added: `smpl_animations.json`  These animations were extracted from the SMPL unity project. A SMPL humanoid can use non-SMPL animations and vice-versa; these animations have been grouped into their own library merely for organizational convenience.

### Build

- Fixed: NullReferenceException when sending `send_vr_rig`.
- Fixed: Possible race condition when sending `send_vr_rig` soon after the VR rig is created.

### Example Controllers

- Added: `smpl_humanoid.py` Add a [SMPL humanoid](https://smpl.is.tue.mpg.de) to the scene. Set its body parameters and play an animation.

### Documentation

#### Modified Documentation

| Document       | Modification                               |
| -------------- | ------------------------------------------ |
| `humanoids.md` | Rewrote document and added SMPL humanoids. |

## v1.8.26

### Build

- Fixed: NullReferenceException when sending `destroy_object` for a composite object.

## v1.8.25

### Command API

#### New Commands

| Command | Description |
| --- | --- |
| `add_torque_to_revolute`  | Add a torque to a revolute joint.  |
| `add_force_to_prismatic`  | Add a force to a prismatic joint.  |
| `add_torque_to_spherical` | Add a torque to a spherical joint. |

### `tdw` module

#### `PyPi`

- (Backend) Added optional parameter `comparison` to `PyPi.required_tdw_version_is_installed()`. Options: `"=="`, `">"`, and `">="`.

### Example Controllers

- Added: `robot_torque.py`

### Docker

- Updated Dockerfile to Ubuntu 18 and removed packages required for Flex and for audio+video recording.
- Added two new Docker files:
  - `Dockerfile_audio` includes pulseaudio and ffmpeg (audio+video recording).
  - `Dockerfile_flex` is Ubuntu 16 and includes CUDA (Flex).

### Documentation

#### Modified Documentation

| Document   | Modification                                                |
| ---------- | ----------------------------------------------------------- |
| `video.md` | Added steps for building an audio-enabled Docker container. |

## v1.8.24

### Command API

#### New Commands

| Command           | Description                         |
| ----------------- | ----------------------------------- |
| `send_categories` | Send the category names and colors. |

#### Modified Commands

| Command               | Modification                                                 |
| --------------------- | ------------------------------------------------------------ |
| `use_pre_signed_urls` | Default value for all Linux distros is True (was True only for Ubuntu 20 and otherwise False). |
| `set_magnebot_wheels_during_move` | Output data will report that the motion was not a success if the Magnebot overshoots the distance. |

### Output Data

#### New Output Data

| Output Data  | Description                |
| ------------ | -------------------------- |
| `Categories` | Category names and colors. |

#### Modified Output Data

| Output Data          | Modification                   |
| -------------------- | ------------------------------ |
| `SegmentationColors` | Added: `get_object_category()` |
| `Rigidbodies`        | Added: `get_kinematic()`       |

### Build

- Fixed: `send_occlusion` gives a occlusion value of 0 when there is occlusion. This has been fixed but the command is somewhat slower now.
- Fixed: race condition when requesting collision data for objects that have just been destroyed.
- Fixed: crash to desktop if collision detection is enabled (`send_collisions`) for a robot with a fixed immovable joint that has colliders. Now, fixed immovable joints with colliders (ur5, ur10, etc.) have colliders but will never send `Collision` output data.

### Robot Library

- Added: `RobotRecord.targets`. A dictionary of "canonical" joint targets to set a pose such that none of the joints are intersecting with the floor, assuming that the robot's starting position is (0, 0, 0). Key = The name of the joint. Value = A dictionary: `"type"` is the type of joint (`"revolute"`, `"prismatic"`, `"sphereical"`) and `"target"` is the target angle or position.

## v1.8.23

**THIS IS A CRITICAL UPDATE.** You are **strongly** advised to upgrade to this version of TDW.

### Command API

#### New Commands

| Command                                 | Description                                                  |
| --------------------------------------- | ------------------------------------------------------------ |
| `adjust_directional_light_intensity_by` | Adjust the intensity of the directional light (the sun) by a factor. |
| `set_directional_light_color`           | Set the color of the directional light (the sun).            |
| `adjust_point_lights_intensity_by`      | Adjust the intensity of all point lights in the scene by a factor. |
| `send_occlusion` | Send occlusion data to the controller. |
| `send_lights`                           | Send data for each directional light and point light in the scene. |

#### Modified Commands

| Command               | Modification                                                 |
| --------------------- | ------------------------------------------------------------ |
| `set_socket_timeout`  | This command is no longer deprecated.<br />The `timeout` parameter is now measured in milliseconds and the default value is 1000.<br />Added `max_retries` parameter: The number of retries before the socket is terminated and reconnected. |
| `set_network_logging` | This command no longer logs the name of each command as it is executed (it still logs the raw message sent by the controller). |

### Output Data

#### New Output Data

| Output Data | Description                                                  |
| ----------- | ------------------------------------------------------------ |
| `Occlusion` | To what extent parts of the scene environment (such as walls) are occluding objects. |
| `Lights`    | Data for all lights in the scene. |

### Build

- **Fixed: On Linux, the build will often try to read the same message twice.** This can result in anomalous behavior such as the build executing a `destroy_object` command when the object doesn't exist (because it was already destroyed on the previous frame). **It is still possible for the build to read the same message twice, however to the best of our knowledge it is extremely unlikely.** 
- Fixed: When the build automatically terminates its network socket, reconnects, and requests that the controller resend the most recent message, the build also advances one physics frame.

### `tdw` module

- (Backend) Added `packaging` as a required module.

#### `Build` (backend)

- Added optional parameter `check_head` to `get_url()`. If True, check the HTTP headers to make sure that the release exists.

#### `PyPi` (backend)

- Added: `required_tdw_version_is_installed(required_version, build_version)` Check whether the correct version of TDW is installed. This is useful for other modules such as the Magnebot API that rely on certain versions of TDW. 

### Example Controllers

- Added: `occlusion.py`
- Added: `lights_output_data.py`

### Benchmark

- Added occlusion to `benchmarker.py`

### Documentation

#### Modified Documentation

| Document              | Modification                             |
| --------------------- | ---------------------------------------- |
| `observation_data.md` | Added `Occlusion` section and benchmark. |

## v1.8.22

**THIS IS A CRITICAL UPDATE.** You are **strongly** advised to upgrade to this version of TDW.

### Command API

#### New Commands

| Command                            | Description                                                  |
| ---------------------------------- | ------------------------------------------------------------ |
| `rotate_directional_light_by`      | Rotate the directional light (the sun) by an angle and axis. |
| `reset_directional_light_rotation` | Reset the rotation of the directional light (the sun).       |
| `parent_object_to_avatar`          | Parent an object to an avatar.                               |
| `unparent_object`                  | Unparent an object from its current parent.                  |
| `set_network_logging`              | If True, the build will log every message received from the controller and will log every command that is executed. |

#### Modified Commands

| Command               | Modification                                                 |
| --------------------- | ------------------------------------------------------------ |
| `use_pre_signed_urls` | Default value on Ubuntu 20 is True and default value for all other platforms is False (previously, default value was False for all platforms) |

#### Deprecated Commands

| Command              | Reason                                                       |
| -------------------- | ------------------------------------------------------------ |
| `set_socket_timeout` | The TCP socket no longer use a timeout; this command doesn't do anything. |

### `tdw` module

#### `Controller`

- Reverted how `get_unique_id()` works to v1.8.20
- Removed `Controller.reset_unique_id()`

### Build

- **FIXED CRITICAL NETWORK BUGS:**
  - Fixed: Occasionally, the build will receive the same message twice.
  - Fixed: Dictionary key errors when adding objects, avatars, etc. due to the aforementioned doubling of received messages.
  - Fixed: The build will hang indefinitely due to the TCP socket repeatedly timing out.
  - Fixed: Rare race conditions due to commands being executed out of order.
- Fixed: (Unity Editor only) Logged error when sending `set_physic_material` because the material can't be destroyed to prevent memory loss.
- Fixed: Warnings when destroying sub-objects of a composite object because they aren't in the main cache.

### Example Controllers

- Added: `directional_light.py`

## v1.8.21

### `tdw` module

#### `Controller`

- Fixed: As of a few updates ago, the controller often sends non-unique object IDs. We are still trying to determine what changed in the build's code, but in the meantime, `Controller.get_unique_id()` will always return a unique ID.
  - Added `Controller.reset_unique_id()` to prevent overflow errors.

### Build

- Fixed: Rare bug where the build won't receive the full JSON string for very long lists of commands. In these cases, the build will request that the controller resend the message.
- Fixed: Rare bug in which the controller enters an infinite loop trying to resend messages to the build. Now, it will quit with an error after a certain number of retries.

## v1.8.20

### Command API

#### New Commands

| Command                              | Description                                                  |
| ------------------------------------ | ------------------------------------------------------------ |
| `set_magnebot_wheels_during_move`    | Set the friction coefficients of the Magnebot's wheels during a move_by() or move_to() action, given a target position. The friction coefficients will increase as the Magnebot approaches the target position and the command will announce if the Magnebot arrives at the target position. |
| `set_magnebot_wheels_during_turn_by` | Set the friction coefficients of the Magnebot's wheels during a turn_by() action, given a target angle. The friction coefficients will increase as the Magnebot approaches the target angle and the command will announce if the Magnebot aligns with the target angle. |
| `set_magnebot_wheels_during_turn_to` | Set the friction coefficients of the Magnebot's wheels during a turn_to() action, given a target angle. The friction coefficients will increase as the Magnebot approaches the target angle and the command will announce if the Magnebot aligns with the target angle. Because the Magnebot will move slightly while rotating, this command has an additional position parameter to re-check for alignment with the target. |
| `set_robot_joint_friction`           | Set the friction coefficient of a robot joint.               |
| `perlin_noise_terrain` | Initialize a scene environment with procedurally generated "terrain" using Perlin noise. This command will return Meshes output data which will contain the mesh data of the terrain. |

### Output Data

#### New Output Data

| Output Data      | Description                                         |
| ---------------- | --------------------------------------------------- |
| `MagnebotWheels` | A message sent when a Magnebot arrives at a target. |

#### Modified Output Data

| Output Data | Modification                                                 |
| ----------- | ------------------------------------------------------------ |
| `Overlap`   | Added: `get_walls()`. Returns True if there is a non-floor environment object in the overlap (such as a wall). |

### `tdw` Module

- Added `SceneBounds` and `RoomBounds`. Convenient wrapper classes for scenes and room environments.

### Build

- Fixed: Unhandled ArgumentException when trying to add an object with an existing ID.
- Fixed: Rare object ID clashes with internal avatar ID integers. Internal avatar IDs are now far less likely to be the same as an object ID.

### Example Controllers

- Added: `perlin_noise_terrain.py` Example of how to create a scene with procedurally generated terrain.

### Use Cases

- Fixed: `single_object.py` crashes when including the `--materials` flag.

## v1.8.19

### Command API

#### Modified Commands

| Command                                                      | Modification                                                 |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| `send_overlap_box`<br>`send_overlap_capsule`<br>`send_overlap_sphere` | Removed the `"frequency"` parameter; these commands now send data exactly once (never per-frame).<br>It's now possible to receive multiple `Overlap` output data objects per frame instead of just one. |

### Build

- Fixed: Resonance Audio doesn't work on OS X.

### Python

- Fixed: RuntimeWarning in `QuaternionUtils.get_y_angle()` due to a NaN value.

## v1.8.18

### Build

- Fixed: `rotate_object_by`, `rotate_object_to`, and `robot_object_to_euler_angles` incorrectly translate the object if `use_centroid == True`.

### Model Library

-  Marked salt_shaker as do_not_use
- Updated objects.csv with new objects

## v1.8.17

### Command API

#### New Commands

| Command               | Description                                                  |
| --------------------- | ------------------------------------------------------------ |
| `use_pre_signed_urls` | Toggle whether to download asset bundles (models, scenes, etc.) directly from byte streams of S3 objects, or from temporary URLs that expire after ten minutes. Only send this command and set this to True if you're experiencing segfaults when downloading models from models_full.json Initial value = False (download S3 objects directly, without using temporary URLs) |

### Model library

- Marked cylinder001 as do_not_use

### Python

- Added optional argument `--temp_urls` to `screenshotter.py` (If included, sends `use_pre_signed_urls`).
- `screenshotter.py` no longer automatically launches the build.
- Added optional argument `--temp_urls` to `single_object.py` (If included, sends `use_pre_signed_urls`).

### Documentation

#### Modified Documentation

| Document       | Modification                                             |
| -------------- | -------------------------------------------------------- |
| `debug_tdw.md` | Added a section for how and when to use pre-signed URLs. |

## v1.8.16

### Command API

#### Removed Commands

| Command     | Reason                                                       |
| ----------- | ------------------------------------------------------------ |
| `start_udp` | It's very unreliable and works differently depending on the OS (see below for replacement) |

### `tdw` module

#### `Controller`

- Removed `udp` parameter from the constructor
- Removed UDP heartbeat. Replaced it with a simpler heartbeat that checks whether the build process is up (assuming that the build process is running locally; if not, the controller doesn't start the heartbeat)
- Added `check_build_process` parameter to the constructor, which handles the check described above

### Build

- Fixed: `set_visual_material` doesn't work after sending `set_flex_soft_actor`.

### Model library

- Added models from models_full.json to models_core.json: alarm_clock, backpack, b04_backpack, b04_glass_06_vray, cgaxis_models_23_19_vray, holy_bible, b04_bowl_smooth, b04_default, calculator, 034_vray, cgaxis_models_volume_59_15_vray, b04_cassete, b04_dat, steam-punk_gear_29, steam-punk_gear_25, steam-punk_gear_27, hair_comb_2010, coffeecup004, coffee_cup, mug, b04_geosphere001, b05_48_body_shop_hair_brush, b04_comb, engineers_hammer_vray, b04_headphones_31_12, kitchen_sieve, cucharon_utensilios, lighter, b04_lighter, zippo, b03_padlock, cylinder001, b03_pen_01_001, 868580_pliers_max2016, b04_wire_pincers, remote_vr_2012, salt_shaker, scissors, b03_old_scissors, b04_screwdriver_v2_texture_, b04_screwdriver_render, b04_roller_new, b03_roller_skate, b03_spoon_001, b03_morphy_2013__vray, vray_043, b04_champions_trophy, trophy01, trophy02, omega_seamaster_set, mouse_02_vray, b05_champagne_cup_vray, ball_peen_hammer, b05_vray_cassette_render_scene, generic_toothbrush_001, toothbrush, apple_ipod_touch_yellow_vray
- Marked models as do_not_use: b03_dice and b03_mando_samsung_max

### Example Controllers

- Added: `minimal_audio_dataset.py` Minimal example of how to generate an audio dataset.

### Use Cases

- `single_object.py` is set to `launch_build=False` (was `True`) and now has an optional `--launch_build` command line arg.

### Documentation

#### Modified Documentation

| Document    | Modification                                                 |
| ----------- | ------------------------------------------------------------ |
| `README.md` | Removed link to tdw_sound20k                                 |
| `getting_started.md` | Removed paragraph about UDP heartbeat and reverted network diagram. |
| `video.md`  | Added a sentence directing the reader to minimal_audio_dataset.py |

## v1.8.15

### Command API

#### New Commands

| Command              | Description                                                  |
| -------------------- | ------------------------------------------------------------ |
| `set_error_handling` | Set whether TDW will quit when it logs different types of messages. |
| `start_udp`          | Start a UDP heartbeat. The heartbeat will continue until the build process is killed. This command is always sent by the controller as soon as it receives an initial message from the build. In nearly all cases, you shouldn't send this command again while TDW is running. If you do send this command again, it will override the previous UDP heartbeat. |
| `unload_unused_assets` | Unload lingering assets (scenes, models, textures, etc.) from memory. Send this command if you're rapidly adding and removing objects or scenes in order to prevent apparent memory leaks. |

#### Modified Commands

| Command     | Modification                                                 |
| ----------- | ------------------------------------------------------------ |
| `terminate` | Sends a `QuitSignal` indicating that the build quit gracefully. |

### Output Data

#### New Output Data

| Output Data  | Description                              |
| ------------ | ---------------------------------------- |
| `QuitSignal` | A signal indicating that the build quit. |

### `tdw` module

#### `Controller`

- The controller will always send `[set_error_handling, start_udp, send_version]` as an initial message to the build.
- Per `communicate()` call, the controller will check for a `QuitSignal`. If there is one, it will quit. 
- Added optional `udp` parameter to the constructor.
- (Backend) Added `self._udp()` which is automatically called after the build launches. This is handled in a separate thread and it listens to the UDP heartbeat signal from the build.
- (Backend) `Controller._check_build_version()` no longer needs to send `send_version` in a `communicate()` call.
- (Backend) Added `self._print_build_log()` Prints the expected location of the build log.
- (Backend) Added `self._is_standalone`, `self._tdw_version`, and `self._unity_version` fields.
- (Backend) Added `self._done` Boolean flag used for the UDP heartbeat thread.

### Build

- Fixed: For most commands involving objects, if `"id"` is set to an ID not currently in the cache, the build will have an infinite loop of NullReferenceExceptions rather than logging an error only once.

### Documentation

#### Modified Documentation

| Document             | Modification                                                 |
| -------------------- | ------------------------------------------------------------ |
| `getting_started.md` | Updated network diagram to include the UDP heartbeat.<br>Added a section explaining the UDP heartbeat. |

## v1.8.14


### Command API

#### New Commands

| Command                 | Description                                                  |
| ----------------------- | ------------------------------------------------------------ |
| `send_local_transforms` | Send Transform (position and rotation) data of objects in the scene relative to their parent object. |

### Output Data

#### New Output Data

| Output Data       | Description                                                  |
| ----------------- | ------------------------------------------------------------ |
| `LocalTransforms` | Data about the Transform component of objects (position and rotation) relative to its parent objects. |

### `tdw` module

- Added: `TDWUtils.euler_angles_to_rpy(euler_angles)` Convert Euler angles to ROS RPY.
- **Updated PyImpact audio materials.** Object audio data `ObjectInfo` now has a `size` parameter (0-5). This is automatically handled in `PyImpact.get_object_info()` (i.e. the default audio data loaded from objects.csv). Audio generated by PyImpact will sound different (and better!) than it did in previous versions of TDW.
  - Added: `ObjectInfo.size`
  - The default value of `initial_amp` in the PyImpact constructor is now 0.5 (was 0.25)
  - Updated default static friction and dynamic friction values per audio material
  - Replaced all existing audio materials with new audio materials, each with size variants. For a full list, see the PyImpact API document.
  - Updated `PyImpact.DENSITIES` with new materials and density values.
  - (Backend) Removed a lot of audio .json files that weren't being used.

## v1.8.13

### Build

- Fixed: Unhandled PhysX errors after sending `set_physic_material` or `set_robot_joint_physic_material` many times because there are more than 64k physic materials in memory.
- Fixed: Potential memory leak when sending `destroy_all_objects` due to object assets not being cleaned up correctly.
- Fixed: Potential memory leak when loading a new scene because mesh data is still in memory.

## v1.8.12

### Command API

### New Commands

| Command                          | Description                               |
| -------------------------------- | ----------------------------------------- |
| `make_robot_nav_mesh_obstacle`   | Make a robot a NavMesh obstacle.          |
| `remove_nav_mesh_obstacle`       | Remove a NavMesh obstacle from an object. |
| `remove_robot_nav_mesh_obstacle` | Remove a NavMesh obstacle from a robot.   |

#### Modified Commands

| Command                  | Modification                                                 |
| ------------------------ | ------------------------------------------------------------ |
| `bake_nav_mesh`          | Added optional parameter `ignore`: Ignore objects or robots in this list.<br>Fixed: Unhandled exception if collider meshes are read-only; read-only meshes are now ignored. |
| `make_nav_mesh_obstacle` | Added optional parameter `shape`: The shape of the carver.   |

## v1.8.11

### Command API

#### Modified Commands

| Command              | Modification                                                 |
| -------------------- | ------------------------------------------------------------ |
| `send_collisions`    | Fixed: collision data can be sent from an object after it's destroyed, resulting in warnings in the player log. |
| `set_floorplan_roof` | Fixed: The roof can be re-enabled after being disabled.      |

### Model Library

- Added to `models_core.json`: camera_box, iron_box, coffeemug, b04_ramlosa_bottle_2015_vray, moet_chandon_bottle_vray, b04_whiskeybottle, 102_pepsi_can_12_fl_oz_vray, candlestick1, golf, b03_toothbrush, b05_calculator, b05_tag_heuer_max2014, b05_executive_pen

### `tdw` module

- Added: `TDWUtils.get_bounds_extents()` Returns the width, length, height of an object's bounds.
- Updated many audio values in `objects.csv`.

## v1.8.10

### Command API

#### New Commands

| Command        | Description                                          |
| -------------- | ---------------------------------------------------- |
| `send_boxcast` | Cast a box along a direction and return the results. |

#### Modified Commands

| Command                             | Modification                                                 |
| ----------------------------------- | ------------------------------------------------------------ |
| `send_raycast`<br>`send_spherecast` | Fixed: Only the last raycast command in the list returns data.<br>Removed parameter `frequency`. These commands will always function as if `"frequency" == "once"`. |

## v1.8.9

### Command API

#### New Commands

| Command                           | Description                                                  |
| --------------------------------- | ------------------------------------------------------------ |
| `set_render_order`                | Set the order in which the avatar's camera will render relative to other cameras in the scene. |
| `set_robot_joint_physic_material` | Set the physic material of a robot joint.                    |

### `tdw` module

#### `Controller`

- Fixed: Constructor doesn't pass port number to the build if `launch_build == True`

### Build

- **Fixed: Can't launch TDW.app by double-clicking it.** If you download the build from the Releases page on the repo, you can run `setup.sh` (located in the same directory as `TDW.app`). If you download the build by launching a controller, i.e. `c = Controller()`, the controller will automatically fix TDW.app before launching it.
- Fixed a potential memory leak in `set_physic_material` and `set_avatar_physic_material`.

### Docker

- Fixed: `pull.sh` fails with error: `unary operator expected`

## v1.8.8

### Command API

#### Modified Commands

| Command                | Modification                                                 |
| ---------------------- | ------------------------------------------------------------ |
| `unload_asset_bundles` | Does a garbage collector call on the same frame (which can fix apparent memory leaks when quickly loading and unloading big asset bundles) |

### Output Data

#### Modified Output Data

| Output Data | Modification                       |
| ----------- | ---------------------------------- |
| `Robots`    | Added: `get_immovable()`           |
| `Magnebots` | Fixed: `get_id()` always returns 0 |

## v1.8.7

### Command API

#### Modified Commands

| Command         | Modification                                                 |
| --------------- | ------------------------------------------------------------ |
| `follow_object` | Added optional parameter `rotation`. If True, set the avatar's rotation to the object's rotation. |

## v1.8.6

### `tdw` module

#### `PyImpact`

- Fixed: PyImpact sometimes creates a droning audio effect or distorts audio due to the same object having more than one collision in a given frame. PyImpact will only select one collision event per object per frame, and can filter out events in which (`enter` and `stay`) or (`enter` and `exit`) occurred on the same frame for the same object.

### Output Data

#### Modified Output Data

| Output Data    | Description                                                  |
| -------------- | ------------------------------------------------------------ |
| `ImageSensors` | Added: `get_sensor_forward()` Returns the forward directional vector of the sensor. |

## v1.8.5

### Command API

#### New Commands

| Command                  | Description                              |
| ------------------------ | ---------------------------------------- |
| `apply_torque_to_object` | Apply a torque to an object's rigidbody. |

#### Modified Commands

| Command              | Description                                                  |
| -------------------- | ------------------------------------------------------------ |
| `send_version`       | Added optional parameter `log` to log the TDW version in the Player or Editor log (default value is True). |
| `add_fixed_joint`    | Un-deprecated because it's still being used.                 |
| `detach_from_magnet` | Fixed: Kinematic objects attached to the magnet become non-kinematic when dropped. |

### Model Library

- Marked refridgerator_slim as do_not_use (colliders are rotated)
- Added: 4ft_wood_shelving, 5ft_shelf_metal, 5ft_wood_shelving, 6ft_shelf_metal, 6ft_wood_shelving

### Scene Library

- Added: mm_craftroom_1a, mm_craftroom_1b, mm_craftroom_2a, mm_craftroom_2b, mm_craftroom_3a, mm_craftroom_3b, mm_craftroom_4a, mm_craftroom_4b

### `tdw` module

#### `PyImpact`

- Added and update many object audio values in objects.csv
- Fixed: PyImpact sometimes creates a droning audio effect. To prevent this, PyImpact will ignore collision events if the same pair of objects registers an `enter` and `stay` collision event on the same frame.

### Documentation

#### Modified Documentation

| Document           | Description                                                  |
| ------------------ | ------------------------------------------------------------ |
| `impact_sounds.md` | Added a section and code example for how to prevent audio droning. |

## v1.8.4

### Command API

#### Modified Commands

| Command                   | Description                                                  |
| ------------------------- | ------------------------------------------------------------ |
| `set_reverb_space_simple` | Added optional parameters `min_room_volume` and `max_room_volume`. |

### `tdw` module

#### `PyImpact`

- Added: `get_audio_commands(resp, wall, floor)`. This *greatly* simplifies PyImpact by doing all collision detection and command creation under the hood using default audio values.
- Added: `set_default_audio_info(object_names)`. Set the default audio values and cache the names of each object in the scene.  
- Added fields: `object_info` (cached default object info), `object_names` (cached object IDs and their names in the current scene), `env_id` (dummy ID for the environment)
- Fixed: Objects not present in the Rigidbody output data don't create audio. (This can happen if  your controller set the `ids` value in `send_rigidbodies` to exclude some objects, or if there is a robot in the scene.) As a fallback, PyImpact will try to use default audio values.
- Fixed: Distorted sound if an object scrapes along a wall. Now, scrapes on walls are ignored.
- Fixed: Distorted sound if the sound's amp is <= -1
- Fixed: Distorted sound if an object scrapes along a floor.

### Scene Library

- Added: mm_kitchen_1b, mm_kitchen_2a, mm_kitchen_2b, mm_kitchen_3a, mm_kitchen_3b, mm_kitchen_4a, mm_kitchen_4b

### Example Controllers

- Re-wrote `impact_sounds.py` to use the simplified PyImpact API (i.e. `get_audio_commands()`).

### Build

- Upgraded to Unity 2020.2.7
- Fixed: `rotate_sensor_container_by` rotations around a local axis instead of a world axis
- Fixed: If `set_kinematic_state` is sent more than once in a row to the same object with `kinematic=True`, the collision detection mode will be set incorrectly.
- Fixed: Audio glitches when using Resonance Audio because the playback is doubled.
- Fixed: ZMQ error if the build is launched a few seconds before the controller is launched.
- Fixed: Can't draw Flex particles in Linux (see note in upgrade guide).
- Fixed: A potential rare infinite loop if a JSON message can't be deserialized.

### Documentation

#### Modified Documentation

| Document           | Description                                                  |
| ------------------ | ------------------------------------------------------------ |
| `impact_sounds.md` | Added a "simple usage" section and updated the example controller code. |

## v1.8.3

### Command API

### New Commands

| Command                    | Description                                                  |
| -------------------------- | ------------------------------------------------------------ |
| `set_ambient_light`        | Set how much the ambient light from the source affects the scene. |
| `set_hdri_skybox_exposure` | Set the exposure of the HDRI skybox to a given value.        |

#### Modified Commands

| Command                                                | Modification                                                 |
| ------------------------------------------------------ | ------------------------------------------------------------ |
| `set_reverb_space_expert`<br>`set_reverb_space_simple` | Added new materials: `"metal"` and `"wood"`<br>Set the default value of `env_id` to -1 (was 0).<br>If `env_id == -1`, the reverb space will encapsulate the entire scene. |
| `add_position_marker`                                  | Added new shapes: `"circle"` and `"square"`                  |

### Build

- **Fixed: A major bug that causes the build to hang. You are STRONGLY encouraged to upgrade to this version of TDW!**

### Model Library

- Added: basic_cork_2, button_two_hole_green_mottled, square_coaster_001_cork, shoebox_fused, key_dull_metal, round_coaster_indent_wood, square_coaster_001_marble, button_two_hole_red_wood, round_coaster_cherry, button_two_hole_grey, square_coaster_rubber, 4ft_shelf_metal, button_four_hole_red_plastic, key_shiny, tapered_cork, cork_plastic_black, square_coaster_wood, button_four_hole_wood, champagne_cork, round_coaster_indent_stone, aaa_battery, square_coaster_stone, button_four_hole_white_plastic, button_four_hole_mottled, button_four_hole_large_black, bung, basic_cork, round_coaster_indent_rubber, round_coaster_stone, square_coaster_001_wood, 9v_battery, button_four_hole_large_wood, key_brass, tapered_cork_w_hole, round_coaster_stone_dark, button_two_hole_red_mottled, cork_plastic

### Scene Library

- Added: mm_kitchen_1a

## v1.8.2

### `tdw` module

### `Controller`

- Fixed: When checking for TDW updates, the recommendation to upgrade gives the incorrect release version if the third number in the version is above 9 (e.g. 1.7.16)

#### `RobotCreator`

- Added: `robot_creator.py` **Frontend users can now add robots to TDW, given the URL of a .urdf or .xacro file.** See: `tdw/Documenation/misc_frontend/robotics.md` and `tdw/Documentation/python/robot_creator.md`

#### Backend

- Added: `asset_bundle_creator_base.py` Shared code between `asset_bundle_creator.py` and `robot_creator.py`

### Robot Library

- Added new robots: Baxter, Sawyer, Niryo One, Fetch, Shadowhand, UR5, and UR10

### Build

- Upgraded to Unity 2020.2.5

### Example Controllers

- `robot_arm.py` uses the UR5 robot instead of the UR3 robot

### Documentation

#### New Documentation

| Document | Description |
| --- | --- |
| `robot_creator.md`             | API documentation for `RobotCreator` as well as installation instructions and troubleshooting tips. |
| `asset_bundle_creator_base.md` | API documentation for `AssetBundleCreatorBase`               |

#### Modified Documentation

| Document                       | Modification                                                 |
| ------------------------------ | ------------------------------------------------------------ |
| `robots.md`                    | Added a section for how to start using the new `RobotCreator` |

## v1.8.1

### Command API

#### New Commands

| Command              | Description                                                  |
| -------------------- | ------------------------------------------------------------ |
| `set_socket_timeout` | Set the timeout duration for the socket used to communicate with the controller. |

### `tdw` module

#### `Controller`

- **Fixed: The connection to the build will occasionally fail, causing the controller to hang indefinitely.** Now, the build will close its socket, open a new socket, and alert the controller that it should re-send the previous message. This won't advance the simulation in any way but you might notice a few-second hiccup between messages.

### Benchmarking

- Increased the default number of trials from `benchmarker.py` from 10,000 to 50,000
- Fixed: `build_simulator.py` doesn't terminate automatically.
- Fixed: `controller_simulator.py` doesn't work.
- Removed: `req_test_controller.py` because ReqTest isn't supported in TDW anymore.
- Removed: `req_test_builder.py`

### Documentation

#### Modified Documentation

| Document        | Modification                                                 |
| --------------- | ------------------------------------------------------------ |
| `unity_loop.md` | Removed test results that involve ReqTest because they aren't actually that meaningful. |
| `debug_tdw.md`  | Added some information about what to do if the network connection hangs. |

## v1.8.0

### New Features

- Added a robotics API to TDW. For now, the total number of robots is small, but we'll add more over time.
  - Added the Magnebot to TDW.
  - Deprecated the Sticky Mitten Avatar (see [upgrade guide](upgrade_guides/v1.7_to_v1.8.md)).
- Significant graphics improvements in certain scenes because many models didn't cast shadows or reflect light correctly.
- Updated Unity Engine from 2019.4 to 2020.2
- Fixed: OS X and Linux builds don't have executable flags. In order to preserve permissions, they are now stored online as .tar.gz files instead of .zip files.

### Known bugs

#### Bug: Can't create a Linux build without deleting some Flex shader files

_(This is relevant only to users who have access to the C# source code in the private TDWBase repo.)_

To create a Linux build, delete all Flex shaders located in `TDWBase/Assets/NVIDIA/Flex/Resources/Shaders` that have `DrawParticles` or `Fluid` in their name. Otherwise, the Editor will crash to desktop. This is handled automatically when we build and upload TDW releases to GitHub.

#### Bug: Can't draw Flex particles on Linux

It's currently not possible to draw Flex particles (`"draw_particles"` in the Command API) in Linux. Attempting to create a build with the Flex particle shaders for Linux results in a crash-to-desktop. This is new as of Unity 2020.2.2 and it is likely that a future Unity Engine upgrade (i.e. to Unity 2020.2.x) will fix it. As a matter of course, we apply minor Unity Engine updates to TDW whenever they're available. Should one of these updates fix this particular issue, we'll note it in the changelog.

### Command API

#### New Commands

| Command                    | Description                                                  |
| -------------------------- | ------------------------------------------------------------ |
| `add_magnebot`             | Add a Magnebot to the scene.                                 |
| `add_robot`                | Add a robot to the scene.                                    |
| `destroy_robot`            | Destroy a robot in the scene.                                |
| `parent_avatar_to_robot`   | Parent an avatar to a robot.                                 |
| `set_immovable`            | Set whether or not the root object of the robot is immovable. |
| `teleport_robot`           | Teleport the robot to a new position and rotation.           |
| `detach_from_magnet`       | Detach an object from a Magnebot magnet.                     |
| `set_magnet_targets`       | Set the objects that the Magnebot magnet will try to pick up. |
| `set_robot_joint_drive`    | Set static joint drive parameters for a robot joint.         |
| `set_robot_joint_mass`     | Set the mass of a robot joint.                               |
| `set_prismatic_target`     | Set the target position of a prismatic robot joint.          |
| `set_revolute_target`      | Set the target angle of a revolute robot joint.              |
| `set_spherical_target`     | Set the target angles (x, y, z) of a spherical robot joint.  |
| `send_magnebots`           | Send data for each Magnebot in the scene.                    |
| `send_robots`              | Send dynamic data (position, rotation, velocity, etc.) of each robot and each robot's body parts in the scene. |
| `send_static_robots`       | Send static data that doesn't update per frame (such as segmentation colors) for each robot in the scene. |
| `add_trigger_color`        | Add a non-physics trigger collider to an object.             |
| `set_legacy_shaders`       | Set whether TDW should use legacy shaders (pre-v1.8) for its models. |
| `enable_reflection_probes` | Enable or disable the reflection probes in the scene.        |

#### Modified Commands

| Command | Modification |
| --- | --- |
| `set_vingette` | By default, the post-processing vignette is disabled, i.e. the parameter  `enabled = False` (was `True`). |
| `rotate_object_to_euler_angles` | Added optional parameter `use_centroid` |
| `rotate_object_to` | Added optional parameter `use_centroid` |

#### Removed Commands

| Command               | Reason                                                   |
| --------------------- | -------------------------------------------------------- |
| `toggle_image_sensor` | Deprecated in v1.7<br>Use `enable_image_sensor` instead. |

#### Deprecated Commands

| Command                                                      | Reason                                                       |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| `set_avatar_rigidbody_constraints`<br>`rotate_head_by`<br>`rotate_waist`<br>`set_sticky_mitten_profile`<br>`stop_arm_joint`<br>`bend_arm_joint_by`<br>`bend_arm_joint_to`<br>`adjust_joint_angular_drag_by`<br>`set_joint_angular_drag`<br>`adjust_joint_damper_by`<br>`adjust_joint_force_by`<br>`set_joint_damper`<br>`set_joint_force`<br>`put_down`<br>`set_stickiness`<br>`pick_up`<br>`pick_up_proximity` | The Sticky Mitten Avatar has been deprecated (see "Features"). |
| `add_fixed_joint`                                            | Very buggy and used only in the Sticky Mitten Avatar high-level API, which has been deprecated. |
| `set_proc_gen_reflection_probe`                              | Use `enable_reflection_probes` instead.                      |

### Output Data

#### New Output Data

| Output Data        | Description                                     |
| ------------------ | ----------------------------------------------- |
| `Magnebot`         | Data for a Magnebot.                            |
| `Robot`            | Data for a robot.                               |
| `StaticRobot`      | Static data for a robot.                        |
| `TriggerCollision` | Data for a non-physics trigger collision event. |

### Modified Output Data

| Output Data            | Modification            |
| ---------------------- | ----------------------- |
| `EnvironmentCollision` | Added: `get_is_floor()` |

### `tdw` module

#### `Controller`

- Added: `get_add_robot()`. Returns a valid `add_robot` command.

#### `FloorplanController`

- Updated floorplans to allow the Magnebot to move around. Removed rugs.
- Made some more objects kinematic.
- Replaced white_shopping_bag with blue_satchal.

#### `TDWUtils`

- Removed: `get_collisions()`

#### `QuaternionUtils`

- Renamed `_UP` to `UP`
- Added: `FORWARD` and `IDENTITY`

#### `AssetBundleCreator`

- Now requires Unity 2020.2

#### Misc.

- Added: `collisions.py` A useful wrapper for collision data.
- Added: `int_pair.py` A pair of unordered hashable integers. Use this class for dictionary keys.
- Added: `RobotLibrarian` and `RobotRecord`.
- Fixed: `missing_materials.py` will launch the build (which isn't useful for tests).
- Updated `build.py` to download OS X and Linux builds correctly. Removed the `chmod()` function because it's no longer needed.

### Model Library

- Fixed: sixty-four models in `models_full.json`(*not* `models_core.json`) have `flex == True` in the metadata record but have non-readable meshes (meaning that they can't be used in Flex). They now have `flex == False` in the metadata record. 

### Scene Library

- Updated the asset bundle for `archviz_house_2018` and renamed it to `archviz_house`.
- Updated the asset bundle for `tdw_room_2018` and renamed it to `tdw_room`.

### Build

- Image capture is slightly faster.
- Log messages written to the player log (and console log in Unity Editor) include the type of object that logged the message. This doesn't affect the text sent by `send_log_messages`.
- Fixed: Many models don't cast shadows or reflect light correctly.
- Fixed: The bounds of objects aren't set correctly if `add_object["rotation"]` isn't (0, 0, 0)
- Fixed: The build often returns `EnvironmentCollision` data when it should return `Collision` data.
- Fixed: `_normals` pass is inaccurate.

### Example Controllers

- Added: `collisions.py`  Receive collision output data and read it as a `Collisions` object.
- Added: `magnebot.py` Example of how to use the Magnebot.
- Added: `robot_arm.py` Add a robot to the scene and bend its arm.
- Added: `robot_camera.py` Add a camera to a Magnebot.
- Removed: `open_box.py` (it uses the Sticky Mitten Avatar, which has been deprecated).
- Removed: `sticky_mitten_avatar.py` (it uses the Sticky Mitten Avatar, which has been deprecated).
- Fixed: `avatar_drag.py` doesn't work.
- Fixed: `composite_object.py` doesn't work on OS X.

### Documentation

#### New Documentation

| Document             | Description                             |
| -------------------- | --------------------------------------- |
| `v1.7_to_v1.8.md`    | Upgrade guide.                          |
| `robots.md`          | Overview of the robotics API.           |
| `robot_librarian.md` | API documentation for `RobotLibrarian`. |

### Benchmarking

- Removed `variance_avatar.py` test because the Sticky Mitten Avatar has been deprecated.

# v1.7.x

To upgrade from TDW v1.6 to v1.7, read [this guide](upgrade_guides/v1.6_to_v1.7.md).

## v1.7.16

### Command API

#### Modified Commands

| Command            | Modification                            |
| ------------------ | --------------------------------------- |
| `rotate_object_by` | Added optional parameter `use_centroid` |

### `tdw` module

#### `Controller`

- Fixed: Crash at start in certain Pyhon environments because there is no version number at the expected position of a string from PyPi.

#### Model Library

- Fixed: The colliders of pipe, torus, bowl, and dumbbell in `models.flex.json` are single convex meshes instead of a group of convex hulls.

## v1.7.15

### Output Data

#### Modified Output Data

| Output Data | Modification                                                 |
| ----------- | ------------------------------------------------------------ |
| `Images`    | Removed: `get_uv_starts_at_top()` (it's not actually useful). |

### `tdw` module

#### `TDWUtils`

- Added optional parameters `far_plane` and `near_plane` to `get_depth_values()`.
- Added optional parameters `far_plane` and `near_plane` to `get_point_cloud()`.

### Build

- **Fixed: `_depth` and `_depth_simple` passes are inaccurate.** Both passes now correctly encode depth values.

### Documentation

#### New Documentation

| Document   | Description                   |
| ---------- | ----------------------------- |
| `depth.md` | How to use depth maps in TDW. |

#### Modified Documentation

| Document             | Description                                                  |
| -------------------- | ------------------------------------------------------------ |
| `getting_started.md` | Fixed: Instructions for how to run TDW on a remote server are incorrect. |

## v1.7.14

### Output Data

#### Modified Output Data

| Output Data | Modification                                                 |
| ----------- | ------------------------------------------------------------ |
| `Images`    | Added: `get_width()`, `get_height()`, and `get_uv_starts_at_top()`<br>The `_depth` and `_depth_simple` passes are now raw RGB render texture data instead of png files (they can still be saved as png files via `TDWUtils.save_images()`). |

### `tdw` module

#### `TDWUtils`

- Added optional parameters `width`, `height`, and `uv_starts_at_top` to `get_depth_values()`.
- Added: `get_point_cloud()`. Create a point cloud from an numpy array of depth values.
- Added: `get_shaped_depth_pass()`. Reshape a depth pass into a 2D RGB array.

### Build

- Fixed: `_depth` and `_depth_simple` passes are (still) inaccurate.

### Example Controllers

- `depth_shader.py` generates a depth values plot and saves out a point cloud file.

## v1.7.13

### `tdw` module

#### `TDWUtils`

- Added optional parameter `depth_pass` to `get_depth_values()` to allow the function to decode data from a `_depth_simple` pass.

### Build

- Fixed: `_depth` and `_depth_simple` passes are inaccurate.

## v1.7.12

### Command API

#### New Commands

| Command         | Description                                                  |
| --------------- | ------------------------------------------------------------ |
| `follow_object` | Teleport the avatar to a position relative to a target. This must be sent per-frame to continuously follow the target. |

### `tdw` module

#### `QuaternionUtils`

- Added: `get_inverse()` Returns the inverse quaternion.
- Added: `world_to_local_vector()` Convert a vector position in absolute world coordinates to relative local coordinates.

## v1.7.11

### Command API

#### New Commands

| Command                 | Description                                                  |
| ----------------------- | ------------------------------------------------------------ |
| `send_screen_positions` | Given a list of worldspace positions, return the screenspace positions according to each of the avatar's camera. |

#### Modified Commands

| Command               | Modification                                                 |
| --------------------- | ------------------------------------------------------------ |
| `add_position_marker` | Fixed: The `a` value of `color` doesn't adjust the transparency.<br>Added: optional parameter `shape`. |

### Output Data

#### New Output Data

| Output Data      | Description                                       |
| ---------------- | ------------------------------------------------- |
| `ScreenPosition` | A worldspace position in screenspace coordinates. |

## v1.7.10

### Command API

#### Modified Commands

| Command          | Description                                                  |
| ---------------- | ------------------------------------------------------------ |
| `set_pass_masks` | Added `_albedo` pass. This only color and texture,  as if lit with only ambient light. |

### `tdw` module

#### `QuaternionUtils`

- Added: `get_y_angle()` The angle between two quaternions in degrees around the y axis.

## v1.7.9

### Command API

#### New Commands

| Command         | Description                  |
| --------------- | ---------------------------- |
| `send_keyboard` | Request keyboard input data. |

### Output Data

#### New Output Data

| Output Data | Description          |
| ----------- | -------------------- |
| `Keyboard`  | Keyboard input data. |

### `tdw` module

- Removed `keyboard` as a required module.

#### `KeyboardController`

- Controller now uses `Keyboard` output data from the simulator to detect keyboard input instead of the Python `keyboard` module, which is less reliable and doesn't work on OS X.

## v1.7.8

### Python

#### `AssetBundleCreator`

- **`AssetBundleCreator` works on Linux.**
- Added optional `display` parameter to constructor.

### Build

- Fixed: Output from the NavMeshAvatar isn't synced with TDW's simulation steps.

### Benchmark

- Added: `benchmarking/variance.py` Test how deterministic the physics simulation is.
- Added: `benchmarking/variance_avatar.py` Test how deterministic the physics simulation with a Sticky Mitten Avatar is.

### Documentation

#### New Documentation

| Document         | Description                    |
| ---------------- | ------------------------------ |
| `determinism.md` | Physics determinism benchmark. |

#### Modified Documentation

| Document    | Modification                                                 |
| ----------- | ------------------------------------------------------------ |
| `README.md` | Fixed: Some links aren't full URLs (this is ok for GitHub but results in dead links on the PyPi page). |

## v1.7.7

### Build

- When the build fails to deserialize a list of commands, the error message is more informative.
- Fixed: Various graphics glitches when enabling/disabling cameras.
- Fixed: `Bounds` output data is incorrect.

### Documentation

#### Modified Documentation

| Document       | Modification                                       |
| -------------- | -------------------------------------------------- |
| `debug_tdw.md` | Added a section for JSON serialization exceptions. |

## v1.7.6

### Command API

#### New Commands

| Command                            | Description                                              |
| ---------------------------------- | -------------------------------------------------------- |
| `set_avatar_rigidbody_constraints` | Set the rigidbody constraints of a Sticky Mitten Avatar. |
| `add_fixed_joint`                  | Attach one object to another.                            |

#### Modified Commands

| Command            | Modification                        |
| ------------------ | ----------------------------------- |
| `rotate_object_to` | Added optional `physics` parameter. |

### `tdw` module

#### `TDWUtils`

- Added: `get_collisions()` Returns a list of collisions on this frame.
- Added: `get_bounds_dict()` Converts bounds data to a dictionary.
- Added: `get_closest_position_in_bounds()` Returns the position on the object bounds closest to `origin`.
- Added: `get_angle()` Returns the angle in degrees between `forward` and the direction vector from `origin` to `position`.
- Added: `get_angle_between()` Returns the angle in degrees between two directional vectors.
- Added: `rotate_position_around()` Returns a position rotated by a given angle around a given origin.

### Benchmarking

- Benchmark controllers no longer automatically launches the build.

## v1.7.5

### Command API

#### New Commands

| Command               | Modification             |
| --------------------- | ------------------------ |
| `enable_image_sensor` | Turn a sensor on or off. |

#### Modified Commands

| Command              | Modification                                                 |
| -------------------- | ------------------------------------------------------------ |
| `send_nav_mesh_path` | Removed parameter `frequency`.<br/>Fixed: Can only receive one `NavMeshPath` output data object. |

#### Deprecated Commands

| Command               | Reason                                                       |
| --------------------- | ------------------------------------------------------------ |
| `toggle_image_sensor` | Functionality can be replicated with `enable_image_sensor` (which is easier to use). |

## v1.7.4

### `tdw` module

#### `FloorplanController`

- Replaced some furniture in floorplan layouts.

### Command API

#### New Commands

| Command                  | Description                                                  |
| ------------------------ | ------------------------------------------------------------ |
| `make_nav_mesh_obstacle` | Make a specific object a NavMesh obstacle.                   |
| `send_nav_mesh_path`     | Tell the build to send data of a path on the NavMesh from the origin to the destination. |

#### Modified Commands

| Command           | Modification                            |
| ----------------- | --------------------------------------- |
| `send_spherecast` | Added optional parameter `id`.          |
| `send_raycast`    | Renamed parameter `raycast_id` to `id`. |

### Output Data

#### New Output Data

| Output Data   | Description                    |
| ------------- | ------------------------------ |
| `NavMeshPath` | A path on the scene's NavMesh. |

## v1.7.3

### `tdw` module

#### `TDWUtils`

- Added: `color_to_hashable()`. Convert a color to a hashable integer.
- Added: `hashable_to_color()`. Convert a hashable integer to a color.

### Model Library

- Added to `models_core.json`:
  - hexagonal_toy

### Build

- Fixed: The objects created by `add_position_marker` initially have colliders, potentially causing physics interactions.

## v1.7.2

### Command API

#### New Commands

| Command                        | Description                                                  |
| ------------------------------ | ------------------------------------------------------------ |
| `adjust_joint_angular_drag_by` | Adjust the angular drag of a joint of a Sticky Mitten Avatar by a delta. |
| `set_joint_angular_drag`       | Set the angular drag of a joint of a Sticky Mitten Avatar.   |
| `set_joint_damper`             | Set the current damper of a joint of a Sticky Mitten Avatar. |
| `set_joint_force`              | Set the force of a joint of a Sticky Mitten Avatar.          |

#### Modified Commands

| Command                     | Modification                                  |
| --------------------------- | --------------------------------------------- |
| `set_sticky_mitten_profile` | Added parameter `angular_drag` to each joint. |

### `tdw` module

#### `FloorplanController`

- Removed the floor and objects from the "patio" area of floorplan_4a, floorplan_4b, and floorplan_4c
- Removed "container" objects from all layouts.

### Model Library

- Added to `models_core.json`:
  - h-shape_wood_block
  - half_circle_wood_block
  - pentagon_wood_block
  - t-shape_wood_block
  - square_wood_block
  - star_wood_block
  - rectangle_wood_block
  - l-shape_wood_block

### Documentation

#### Modified Documentation

| Document                  | Modification                                        |
| ------------------------- | --------------------------------------------------- |
| `sticky_mitten_avatar.md` | Updated example JSON for the sticky mitten profile. |

## v1.7.1

### Command API

#### Modified Commands

| Command                     | Modification                                                 |
| --------------------------- | ------------------------------------------------------------ |
| `set_sticky_mitten_profile` | Fixed: This command doesn't work.<br>Removed `mitten` (redundant because of `wrist_pitch`). |

### Python

#### Use Cases

- Fixed: `rube_goldberg.py` doesn't work.

#### Benchmarking

- Added: `struct_deserialization.py` Test the speed of deserializing structs such as Vector3 and Quaternion.

### Build

- Increased deserialization speed of many commands.

### Documentation

#### Modified Documentation

| Document                     | Modification                                 |
| ---------------------------- | -------------------------------------------- |
| `command_deserialization.md` | Added results of `struct_deserialization.py` |

## v1.7.0

### Command API

#### New Commands

| Command                | Description                                      |
| ---------------------- | ------------------------------------------------ |
| `send_overlap_box`     | Check what a box-shaped space overlaps with.     |
| `send_overlap_capsule` | Check what a capsule-shaped space overlaps with. |
| `send_overlap_sphere`  | Check what a sphere-shaped space overlaps with.  |

#### Modified Commands

| Command                               | Modification                                                 |
| ------------------------------------- | ------------------------------------------------------------ |
| `set_avatar_collision_detection_mode` | Default value of `mode` is `"continuous_dynamic"` (was `"continuous_speculative"`).<br>Added additional values for `mode`: `"continuous"` and `"discrete"`. |
| `set_object_collision_detection_mode` | Default value of `mode` is `"continuous_dynamic"` (was `"continuous_speculative"`).<br/>Added additional values for `mode`: `"continuous"` and `"discrete"`. |

### Output Data

#### New Output Data

| Output Data | Description                                    |
| ----------- | ---------------------------------------------- |
| `Overlap`   | The IDs of every object that a shape overlaps. |

### `tdw` module

#### `TDWUtils`

- Fixed: `get_depth_values()` is inaccurate due to overflow errors.

#### `AssetBundleCreator`

- Upgraded the `asset_bundle_creator` Unity project from Unity 2019.2 to Unity 2019.4 (see `v1.6_to_v1.7.md`).

### Scene Library

- Removed: `roman_villa`

### Use Cases

- Removed `roman_villa` from scenes that `humanoid_video.py` will use.

### Build

- **Upgraded Unity3D Engine from 2019.2 to 2019.4**
  - Upgrade PhysX, which overall improves the quality of physics simulations.
  - Enabled "Enhanced Determinism". Physics is much more deterministic.
- Set the default collision detection mode of all objects and avatars to `continuous_dynamic` (was `continuous_speculative`, which is less accurate.)

### Documentation

#### New Documentation

| Document          | Description    |
| ----------------- | -------------- |
| `v1.6_to_v1.7.md` | Upgrade guide. |

#### Modified Documentation

| Document       | Description                                                  |
| -------------- | ------------------------------------------------------------ |
| `debug_tdw.md` | Clarified where to find the player log.<br>Added a section for network errors. |

# v1.6.x

## v1.6.14

### `tdw` module

- Added: `tdw.tdw_utils.QuaternionUtils` Utility functions for quaternions.

#### `TDWUtils`

- Moved `euler_to_quaternion()` to `QuaternionUtils`
  - Renamed function to `euler_angles_to_quaternion()`
  - Parameter `euler` is a numpy array (was a tuple).
  - Return type is a numpy array (was a list of floats).
- Moved `quaternion_to_euler_angles()` to `QuaternionUtils`

#### `PyImpact`

 - Fixed:  relative amp values aren't handled correctly.

### Python

- Fixed: `screenshotter.py` and `empty_scene` don't work on Linux.

### Scene Library

- Fixed: `box_room_2018` doesn't have colliders on the walls or ceiling.

### Build

- Fixed: `send_collisions` doesn't reset correctly when sent multiple times with different values for `enter`, `exit`, or `stay`.

## v1.6.13

### `tdw` module

#### `PyImpact`

- Added audio values for more objects.

#### `FloorplanController`

- Updated floorplan 4, layout 0
- Added scenes `1a`, `1b`, and `1c`, which have layouts `1`, `2`, and `3`.
- Added scenes `5a`, `5b`, and `5c`, which have layouts `1`, `2`, and `3`.

### Scene Library

- Added scenes:
  - floorplan_1a
  - floorplan_1b
  - floorplan_1c

## v1.6.12

### Command API

#### New Commands

| Command           | Description                                                  |
| ----------------- | ------------------------------------------------------------ |
| `send_spherecast` | Cast a sphere along a direction and return the results. The can be multiple hits, each of which will be sent to the controller as Raycast data. |

### Output Data

#### Modified Output Data

| Output Data | Modification                                                 |
| ----------- | ------------------------------------------------------------ |
| `Raycast`   | Added: `get_hit_object()` Returns true if the raycast hit an object. |

### `tdw module`

#### `PyImpact`

- Added parameter `resonance` to `ObjectInfo`.
- Added optional parameter `logging` to PyImpact's constructor.
- Added: `PyImpact.get_log()`
- Added: `PyImpact.log_modes()`
- Added parameter `resonance` to `PyImpact.get_sound()`,   `PyImpact.get_impact_sound_command()`, `PyImpact.make_impact_audio()`, `PyImpact.get_impulse_response()`,  and`PyImpact.synth_impact_modes()`
- Added resonance values to `objects.csv`.

#### `FloorplanController`

- For scenes `2a`, `2b`, and `2c`, added layouts `1` and `2`
- Added scenes `4a`, `4b`, and `4c`, which have layouts `1`, `2`, and `3`.

### Model Library

- Added to `models_core.json` and `models_full.json`:
  - basket_18inx18inx12iin
  - basket_18inx18inx12iin_bamboo
  - basket_18inx18inx12iin_plastic_lattice
  - basket_18inx18inx12iin_wicker
  - basket_18inx18inx12iin_wood_mesh
  - box_18inx18inx12in_cardboard
  - box_24inx18inx12in_cherry
  - box_tapered_beech
  - box_tapered_white_mesh
  - round_bowl_large_metal_perf
  - round_bowl_large_padauk
  - round_bowl_large_thin
  - round_bowl_small_beech
  - round_bowl_small_walnut
  - round_bowl_talll_wenge
  - shallow_basket_white_mesh
  - shallow_basket_wicker
- In `models_core.json` and `models_full.json`, flagged `rope_table_lamp`, `salt`, and `jigsaw_puzzle_composite` as `do_not_use` due to bad physics behavior.

### Build

- Fixed: `Environments.get_center()` (output data) is sometimes inaccurate. 

### Use Cases

- `rube_goldberg.py` logs audio mode data.

## v1.6.11

### `tdw` module

- Added: `FloorplanController`. Load a interior environment scene and populate it with furniture and props.
- Added: object initialization data classes:
  - `TransformInitData`: Create object and set their positions, rotations, etc.
  - `RigidbodyInitData`: Create objects and set their positions, rotations, and physics properties.
  - `AudioInitData`: Create objects and set their positions, rotations, and physics properties from their PyImpact audio values.
- Added: `floorplan_layouts.json` Floorplan layouts recipes are stored in this file.

#### `PyImpact`

- Added default audio values for many more objects.

### Model Library

- Added to `models_core.json` and `models_full.json`:
  - 24_in_wall_cabinet_white_wood
  - 24_in_wall_cabinet_wood_beach_honey
  - 36_in_wall_cabinet_white_wood
  - 36_in_wall_cabinet_wood_beach_honey
  - bed01
  - bed01_blue
  - bed01_red
  - blue_rug
  - cabinet_24_door_drawer_wood_beach_honey
  - cabinet_24_singledoor_wood_beach_honey
  - cabinet_24_two_drawer_white_wood
  - cabinet_24_two_drawer_wood_beach_honey
  - cabinet_24_white_wood
  - cabinet_24_wood_beach_honey
  - cabinet_36_white_wood
  - cabinet_36_wood_beach_honey
  - cabinet_full_height_white_wood
  - cabinet_full_height_wood_beach_honey
  - carpet_rug
  - elf_painting
  - flat_woven_rug
  - fruit_basket
  - its_about_time_painting
  - purple_woven_rug
  - silver_frame_painting
  - sink_base_white_wood
  - sink_base_wood_beach_honey
- Removed from `models_core.json` and `models_full.json`:
  - `flat-woven-rug`

### Scene Library

- Added new scenes:
  - floorplan_2a
  - floorplan_2b
  - floorplan_2c
  - floorplan_3a
  - floorplan_3b
  - floorplan_3c
  - floorplan_4a
  - floorplan_4b
  - floorplan_4c
  - floorplan_5a
  - floorplan_5b
  - floorplan_5c

### Documentation

#### New Documentation

| Document                  | Description                                                  |
| ------------------------- | ------------------------------------------------------------ |
| `floorplan_controller.md` | API document for `FloorplanController`                       |
| `object_init_data.md`     | API document for `TransformInitData`, `RigidbodyInitData`, and `AudioInitData` |

## v1.6.10

### Command API

#### New Commands

| Command        | Description                                    |
| -------------- | ---------------------------------------------- |
| `send_raycast` | Cast a ray from the origin to the destination. |

#### Modified Commands

| Command          | Modification                                                 |
| ---------------- | ------------------------------------------------------------ |
| `set_pass_masks` | Added `_depth_simple` pass. This is a grayscale image that is less precise than the `_depth` pass, but is faster and easier to use. |

### Output Data

#### New Output Data

| Output Data | Description                                                  |
| ----------- | ------------------------------------------------------------ |
| `Raycast`   | A ray cast from an origin to a destination and what, if anything, it hit. |

### Model Libraries

- Added to `models_core.json` and `models_full.json`:
  - dining_room_table
  - flat-woven-rug
  - framed_painting

## v1.6.9

### Build

- Fixed: `pick_up` and `pick_up_proximity` sometimes try to pick up StickyMittenAvatar body parts.
- Fixed: In `AvatarSegmentationColor` output data, the ID of the root object of a StickyMittenAvatar (`A_StickyMitten_Adult(Clone)_<id>_` or `A_StickyMitten_Baby(Clone)_<id>_`) doesn't match `AvatarSegmentationColor.get_id()`.
- Fixed: Collisions between two body parts of a StickyMittenAvatar are processed as `EnvironmentCollision` output data (they are now ignored).
- Fixed: `teleport_object` doesn't update the positions of an object's `Bounds` data.

## v1.6.8

### Output Data

#### Modified Output Data

| Output Data          | Modification                                                 |
| -------------------- | ------------------------------------------------------------ |
| `AvatarStickyMitten` | Added functions to get the position, rotation, and forward of the center of the mittens (as opposed to the joint location. |

### Example Controllers

- Added: `pass_masks.py` Generate each pass mask.

### Build

- Fixed: `_mask` image pass doesn't work.

### Documentation

#### Modified Documentation

| Document | Modification |
| --- | --- |
| `command_api.md` | Added explanations and images for each `PassMask` in `set_pass_masks`. |
| `observation_data.md` | Added a link to `set_pass_masks` documentation in the Command API. |

## v1.6.7

### `tdw` module

#### `Controller`

- Fixed: Build doesn't launch in Windows.

#### `AssetBundleCreator`

- Fixed: `AssetBundleCreator.get_local_urls()` doesn't add the OS X URL.
- Fixed: `AssetBundleCreator.get_local_urls()` generates paths with `\` instead of `/`.

#### `TDWUtils`

- Added: `quaternion_to_euler_angles()` Convert a quaternion to Euler angles.

#### `PyImpact`

- Added: `get_impulse_response()` Generate an impulse response from specified modes for two objects.

#### `Base64Sound` (in `tdw.py_impact`)

- Added new field: `bytes` The byte data before it is encoded to base64.

#### Librarian (`tdw.librarian`)

- Fixed: Relative URLs in records don't work as expected.

### `asset_bundle_creator` (Unity project)

- Fixed: The names of objects in the substructure data always include the suffix `(Clone)`. To apply this bug fix, delete the directory `~/asset_bundle_creator` where `~` is your home directory. The next time you create a local asset bundle, the Unity project will be recreated.

## v1.6.6

### Command API

#### New Commands

| Command                               | Description                                       |
| ------------------------------------- | ------------------------------------------------------------ |
| `look_at_avatar`                       | Look at another avatar. |
| `add_position_marker` | Create a non-physics, non-interactive sphere to mark a position in the scene. |
| `remove_position_markers` | Remove all position markers from the scene. |

#### Modified Commands

| Command | Modification |
| --- | --- |
| `set_stickiness` | Added optional parameter `show`. If true, colorize the sides of the mitten that are sticky. |

#### Deprecated Commands

| Command | Reason |
| --- | --- |
| `send_avatar_children_names` | This info can be found via `send_avatar_segmentation_colors` |

### Output Data

#### Modified Output Data

| Output Data | Modification |
| --- | --- |
| `AvatarStickyMitten` | Added: `get_angles_left()` and `get_angles_right()` Returns current joint angles. |

### `tdw` module

#### `Controller`

- Fixed: Controller tries to launch a build, then check the version, and then delete the build if the version is out of date (all builds now include a `version.txt` file that the controller will read before trying to launch a build).

#### `AssetBundleCreator`

- **Added support for OS X.**

#### Backend

  - Moved Windows binaries used in `AssetBundleCreator` from `exe/` to `binaries/Windows`
  - Added OS X binaries for `AssetBundleCreator`: `binaries/Darwin`

### Example Controllers

- `local_object.py` works in OS X (previously it only worked in Windows)

### Build

- Fixed: The `scale_object` command doesn't update the object's `Bounds` data.

### Documentation

#### Modified Documentation

| Document       | Description                                                  |
| -------------- | ------------------------------------------------------------ |
| `debug_tdw.md` | Added a section on common problems when installing TDW. Reorganized the list of player log messages. Added a section for Unity credential problems. |
| `add_local_object.md` | Added note that AssetBundleCreator works in OS X. |
| `shapenet.md` | Added note that shapenet.py runs in OS X. |

## v1.6.5

### `tdw` module

- Added required modules: `pyinstaller` and `keyboard`
- Added `tdw.keyboard_controller` A controller that can listen to keyboard input.

#### `Controller`

- Removed optional `display` parameter. It doesn't actually work; Linux users should instead launch the controller with a `DISPLAY` environment variable.

#### Backend

- Adjusted how Flatbuffers imports numpy so that frozen controller code works.

### Example Controllers

- Renamed `keyboard.py` to `keyboard_controller.py` to avoid a name clash with the `keyboard` module. Rewrote the code to use the `KeyboardController` class.

### Build

- Fixed: Segmentation colors are often non-unique.

### Misc.

- Added `freeze.py`. "Freeze" your controller into a portable binary executable.
  - Added `controller.spec` (used for freezing controller code).

### Documentation

#### New Documentation

| Document                 | Description                                                  |
| ------------------------ | ------------------------------------------------------------ |
| `freeze.md`              | How to freeze your controller code into a binary executable. |
| `keyboard_controller.md` | API for KeyboardController.                                  |

#### Modified Documentation

| Document             | Description                                                |
| -------------------- | ---------------------------------------------------------- |
| `getting_started.md` | Fixed instructions for how to start a controller in Linux. |
| `docker.md`          | Fixed some broken links.                                   |

## v1.6.4

### `tdw` module

#### `Controller`

- Don't check the version of the build or download a new build if `launch_build == False`
- Edited the message for when you are using code from the tdw repo that is ahead of PyPi.

#### `TDWUtils`

- Fixed: `validate_amazon_s3()` raises exceptions even if credentials are valid.

#### `PyImpact`

- Added backend code for differentiating between an impact, a scrape, and a roll.
  - `py_impact.CollisionType` An enum of different collision "types"
  - `py_impact.CollisionTypesOnFrame` Contains each type of  collision that a "collider" object experiences in a given frame (for  example, impacts one object while scraping another)

#### `AssetBundleCreator`

- Removed parameter `build_path` from `write_physics_quality()` (obsolete; build is launched automatically)
- Removed parameter `build_path` from `validate()` (obsolete; build is launched automatically)

#### Backend

- Removed parameter `build_path` from `Validator` constructor and `--build_path` command line argument from `validator.py`.
- Removed `--build_path` command line argument from `write_physics_quality.py`.

### Example Controllers

- Added `getting_started.py` This is the controller in the Getting Started guide.

### Docker

- Fixed: Docker file doesn't work.
- Added audio libraries and ffmpeg to the Docker container.
- Updated `docker_controller.py`
- [**Added Docker container to DockerHub**](https://hub.docker.com/r/alters/tdw)
- Added scripts:
  - `docker_tag.sh`: Get the tag for the Docker image installed on this machine.
  - `pull.sh`: Check if your Docker image matches your installed TDW version. If not, pull the correct image.
  - `record_audio_video.sh`: Copied into the container for recording video+audio.
  - `start_container_audio_video.sh`: Start the container and record video+audio.
  - `tdw_version.py`: Print the TDW version.
- Revised `start_container.sh` and `start_container_xpra.sh` to use the new Docker container.

### Documentation

#### New Documentation

| Document             | Description                                             |
| -------------------- | ------------------------------------------------------- |
| `c_sharp_sources.md` | When, and how, to request access to the C# source code. |

#### Modified Documentation

| Document             | Modification                                                 |
| -------------------- | ------------------------------------------------------------ |
| `README.md`          | Removed BinaryManager from `tdw` module table (it's not part of the `tdw` module). |
| `tdw.md`             | Updated for v1.6 and expanded table(s) of contents.          |
| `getting_started.md` | The initial test for new users is `getting_started.py` instead of `objects_and_images.py`.<br/>Added a link to `getting_started.py`.<br/>Edited the example controller code (`getting_started.py`) for clarity. |
| `docker.md` | Rewrote requirements and contents of the container.<br>Added instructions for how to pull the image.<br>Added a list of bash scripts included in the repo. |
| `video.md` | Added better instructions for setting the simulation framerate.<br>**Added instructions for how to record audio+video on a headless server.**<br>Added instructions for using ffmpeg on Windows and OS X. |

## v1.6.3

### `tdw` module

#### `Controller`

- Fixed: Permissions error when launching the build in OS X.

### Build

- Fixed: Non-`_img` pass images don't align with the `_img` pass if the screen size isn't a square.

## v1.6.2

### `tdw` module

- Fixed: `tdw` module doesn't work in virtualenv.

#### `DebugController`

- Added parameters `launch_build` and `display`.

### Build

- Fixed: Downloaded builds don't have execute permissions in OS X or Linux (the downloader now runs `chmod` after extracting the .zip file)
- Fixed: `NullReferenceException` when Sticky Mitten Avatar tries to put down an object that was never held.

### Documentation

#### Modified Documentation

| Document             | Description                                                  |
| -------------------- | ------------------------------------------------------------ |
| `getting_started.md` | 1. The example uses `models_core.json` so it works for everybody.<br>2. Better explanation for how to get object IDs.<br>3. Added image saving to the example. |

## v1.6.1

### New Features

- **Added a working pip module.** It is no longer necessary to download the whole repo to use TDW.
- **The build will automatically launch when you launch a controller.** 
- When you launch a controller, it will automatically check to make sure that your local TDW install it is up-to-date and, if not, offer suggestions for how to upgrade.

For more information, please read Getting Started.

### `tdw` module

- `setup.py` now actually works when doing a `pip install`.
- Removed `pymongo` requirement.
- Added `requests` requirement.
- Added `__init__.py` files in `tdw/` and in subdirectories.
- Added new scripts:
    - `tdw/release/build.py` Helper functions for downloading a build from the repo.
    - `tdw/release/pypi.py` Helper functions for version checks vs. PyPi.

#### `Controller`

- Added new constructor parameters:
    - `launch_build` If `True`, the controller will automatically launch a build. If there is no build at the expected location, the controller will download one. Default = `True`
    - `display` If not `None`, and if this is a Linux machine, and if `launch_build == True`, this will launch the build on the matching display.
- If `check_version == True`:
    - The controller will compare the installed `tdw` Python module to the latest PyPi version. If there is a mis-match, it will recommend upgrading; the recommendation it gives will depend on the mismatch (`1.6.0` vs. `1.6.1`; `1.6.1` vs. `1.7.0`, etc.)
    - The controller will compare the version of the downloaded build to the version of the install `tdw` Python module. If they are different versions, it will show the user how to upgrade/downgrade.
- Added: `Controller.launch_build()` Launch the build. If there is no build in the expected location, download one.

#### `tdw.backend.paths`

- Added: `SYSTEM_TO_EXECUTABLE` and `SYSTEM_TO_RELEASE`

### Example Controllers

- `minimal.py` terminates the build after its test.

### Backend

- Added `MANIFEST.in` to `tdw` module.
- Removed `Python/README.md` (this was a copy of the repo's README and is not actually needed for PyPi).
- Removed `tdw.version.last_stable_version` (not needed)

### Documentation

#### New Documentation

| Document | Description |
| --- | --- |
| `build.md` | `Build` class API. |
| `pypi.md` | `PyPi` class API. |

#### Modified Documentation

| Document | Modification |
| --- | --- |
| `getting_started.md` | 1. Added a section for expected coding knowledge.<br>2. Re-wrote instructions for how to install TDW using the pip module.<br>3. Expanded installation instructions for remote servers.<br>4. Explicitly mention when it is required to clone this repo. |
| `releases.md` | Added a section about how version-checking works. |

## v1.6.0

This changelog is only for the _frontend_ of TDW. If you are a backend developer, or are looking for changes prior to v1.6.0, please refer to the changelog in TDWBase.

### New Features

- **Began new `tdw` repo (split from the private dev `TDWBase` repo).**
  - Removed backend scripts and documentation (they are still in `TDWBase`).

### Command API

#### Modified Commands

| Command                               | Modification                                                 |
| ------------------------------------- | ------------------------------------------------------------ |
| `create_avatar`                       | Parameter `id` now has a default value: `"a"`.               |
| `set_rendering_quality`               | Parameter `render_quality` now has a default value: `5`      |
| `scale_avatar`                        | Parameter `scale_factor` now has a default value: `{"x": 1, "y": 1, "z": 1}` |
| `set_avatar_collision_detection_mode` | Parameter `mode` now has a default value: `"continuous_speculative"`. |
| `set_avatar_forward`                  | Parameter `forward` now has a default value: `{"x": 0, "y": 0, "z": 1}` |
| `set_field_of_view`                   | Parameter `field_of_view` now has a default value: `35`      |
| `apply_force_to_avatar`               | Parameter `direction` now has a default value: `{"x": 0, "y": 0, "z": 1}` |
| `apply_force_to_object`               | Parameter `force` now has a default value: `{"x": 0, "y": 0, "z": 1}` |
| `scale_object`                        | Parameter `scale_factor` now has a default value: `{"x": 1, "y": 1, "z": 1}` |
| `set_object_collision_detection_mode` | Parameter `mode` now has a default value: `"continuous_speculative"`. |
| `send_collisions`                     | Default values for `stay` and `exit` are `False` (both were `True`) |
| `bake_nav_mesh` | Replaced parameters `carve` and `carve_only_stationary` with new parameter `carve_type`. |

#### Removed Commands

| Command                       | Reason                                                       |
| ----------------------------- | ------------------------------------------------------------ |
| `set_day_night`               | This command enabled/disabled all lights in the scene; HDRI skyboxes can be used for *far* better results. |
| `set_material_from_resources` | Only usable in forked versions of TDWBase with extra materials in Resources/. Functionality can be replicated with local material asset bundles. |
| `set_semantic_material`       | Always sets the material as `"undefined"` (because visual materials are, as yet, unclassified). Note: `set_semantic_material_to` is still in the Command API. |
| `update_flex_container`       | Deprecated in v1.5                                           |
| `set_gravity` | Doesn't work as advertised (it makes objects kinematic too).<br>Functionality overlaps with `set_kinematic_state`, `simulate_physics`, and `set_gravity_vector`. |
| `set_shadows` | Functionality can be replicated via: `{"$type": "set_render_quality", "render_quality": 0}`<br>Note: `set_shadow_strength`, a different command, hasn't been removed. |

### Asset Bundle Libraries

- **Updated asset bundle URLs for every asset bundle.** The URLs now point towards binaries stored in the `tdw-public` and `tdw-private` S3 buckets.

#### Models

##### `models_full.json`

- **All models in `models_full.json` that are not also in `models_core.json` ("non-free models") now require S3 access keys in order to download.**

### Python

- Set default `--library` value in `multi_env.py` to `models_full.json` (was `models_core.json`)
- Slight efficiency improvements in `single_object.py`

### Docker

- Updated Docker file, bash scripts, controller, and documentation for v1.6
- Docker file always downloads the latest TDW release.

### Documentation

#### New Documentation

| Document      | Description                                        |
| ------------- | -------------------------------------------------- |
| `releases.md` | Overview of how TDW releases and versioning works. |

#### Modified Documentation

| Document | Modification |
| -------- | ------------ |
| `command_api.md` | _Many_ adjustments to the command descriptions, such as removing obsolete or misleading info, links to other docs, and minor clarifications.<br>Added a reference for all Asset Bundle Commands to their associated wrapper functions (e.g. `add_object` -> `Controller.get_add_object`).<br>Added a note for how to format the URL of a local asset bundle.<br>Clarified which "destroy" commands (e.g. `destroy_object`) retain the cached asset bundle in memory.<br>Grouped humanoid commands into a "Humanoid Command" section.<br>Converted many references to other documents into URLs. |
| `README.md` | Removed links to backend documentation. |
| `getting_started.md` | Updated for `v1.6.0` |
| `command_api_guide.md` | Added a few more examples.<br>Added a section explaining default parameter values. |
| `models_full.md` | Added optional instruction to run the screenshotter. |
| `doc_gen.md` | Extensive rewrite based on the new functionality. |
| `machine_performance.md` | Removed links to TDWBase Issues. |
| `flex.md` | Removed links to TDWBase Issues. |
| `impact_sounds.md` | Fixed a bad link. |
| `shapenet.md` | Fixed a bad link. |
| `video.md` | Fixed a bad link. |

#### Removed Documentation

- Removed all backend documentation from this repo.