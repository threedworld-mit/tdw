# ThreeDWorld (TDW)

**ThreeDWorld (TDW)** is a platform for interactive multi-modal physical simulation. With TDW, users can simulate high-fidelity sensory data and physical interactions between mobile agents and objects in a wide variety of rich 3D environments.

![](splash.jpg)

- [Code of Conduct](https://github.com/threedworld-mit/tdw/blob/master/code_of_conduct.md)
- [Changelog](https://github.com/threedworld-mit/tdw/blob/master/Documentation/Changelog.md)
- [License](https://github.com/threedworld-mit/tdw/blob/master/LICENSE.txt)
- [Website](http://threedworld.org/)
- [Example controllers](https://github.com/threedworld-mit/tdw/tree/master/Python/example_controllers)

# 1. General guide to TDW

## 1.1 Setup

1. [Install TDW](Documentation/lessons/setup/install.md)
3. [Upgrade TDW](Documentation/lessons/setup/upgrade.md)

## 1.2 Core Concepts

1. [The controller](Documentation/lessons/core_concepts/controller.md)
2. [Auto-launching the TDW build](Documentation/lessons/core_concepts/launch_build.md)
3. [Commands](Documentation/lessons/core_concepts/commands.md)
4. [Design philosophy of TDW](Documentation/lessons/core_concepts/design_philosophy.md)
5. [Scenes](Documentation/lessons/core_concepts/scenes.md)
6. [Avatars and cameras](Documentation/lessons/core_concepts/avatars.md)
7. [Add-ons and the `ThirdPersonCamera`](Documentation/lessons/core_concepts/add_ons.md)
8. [Objects](Documentation/lessons/core_concepts/objects.md)
9. [Output data](Documentation/lessons/core_concepts/output_data.md)
10. [Images](Documentation/lessons/core_concepts/images.md)

## 1.3 Troubleshooting

1. [How to report an issue](Documentation/lessons/troubleshooting/issues.md)
2. [Common errors](Documentation/lessons/troubleshooting/common_errors.md)
3. [Performance optimizations](Documentation/lessons/troubleshooting/performance_optimizations.md)
4. [Good coding practices](Documentation/lessons/troubleshooting/good_coding_practices.md)
5. [The `Logger` add-on](Documentation/lessons/troubleshooting/logger.md)

# 2. Tutorials

## 2.1 Objects and Scenes

1. [Overview](Documentation/lessons/objects_and_scenes/overview.md)
2. [Scripted object placement (floorplan layouts)](Documentation/lessons/objects_and_scenes/floorplans.md)
3. [Visual materials, textures, and colors](Documentation/lessons/objects_and_scenes/materials_textures_colors.md)
4. [Procedural generation (scenes)](Documentation/lessons/objects_and_scenes/proc_gen_room.md)
5. [Units and data formats](Documentation/lessons/objects_and_scenes/units.md)
6. [`Bounds` output data](Documentation/lessons/objects_and_scenes/bounds.md)
7. [Procedural generation (objects)](Documentation/lessons/objects_and_scenes/proc_gen_objects.md)
8. [`Raycast` output data](Documentation/lessons/objects_and_scenes/raycast.md)
9. [`Overlap` output data](Documentation/lessons/objects_and_scenes/overlap.md)
10. [Reset a scene](Documentation/lessons/objects_and_scenes/reset_scene.md)

High-level API: [Floorplan](Documentation/python/add_ons/floorplan.md)

## 2.2 3D Model Libraries

1. [Overview](Documentation/lessons/3d_models/overview.md)
2. [Free models](Documentation/lessons/3d_models/free_models.md)
3. [Non-free models](Documentation/lessons/3d_models/non_free_models.md)
4. [Add your own models to TDW](Documentation/lessons/3d_models/custom_models.md)
5. [Add ShapeNet models to TDW](Documentation/lessons/3d_models/shapenet.md)

## 2.3 Visual Perception

1. [Overview](Documentation/lessons/visual_perception/overview.md)
2. [Instance ID segmentation colors (`_id` pass)](Documentation/lessons/visual_perception/id.md)
3. [Semantic category segmentation colors (`_category` pass)](Documentation/lessons/visual_perception/category.md)
4. [Depth maps (`_depth` and `_depth_simple` passes)](Documentation/lessons/visual_perception/depth.md)
5. [Motion perception (`_flow` pass)](Documentation/lessons/visual_perception/flow.md)
6. [Other image passes (`_mask`, `_normals`, and `_albedo` passes)](Documentation/lessons/visual_perception/other_passes.md)
7. [`Occlusion` output data](Documentation/lessons/visual_perception/occlusion.md)

## 2.4 Camera Controls

1. [Overview](Documentation/lessons/camera/overview.md)
2. [Move a camera](Documentation/lessons/camera/position.md)
3. [Rotate a camera](Documentation/lessons/camera/rotation.md)
4. [Follow an object](Documentation/lessons/camera/follow.md)
4. [The `CinematicCamera` add-on](Documentation/lessons/camera/cinematic_camera.md)

## 2.5 Photorealism

1. [Overview](Documentation/lessons/photorealism/overview.md)
2. [Lighting (HDRI skyboxes)](Documentation/lessons/photorealism/lighting.md)
3. [Post-processing](Documentation/lessons/photorealism/post_processing.md)
4. [Depth of field](Documentation/lessons/photorealism/depth_of_field.md)

High-level API: [tdw_image_dataset](https://github.com/alters-mit/tdw_image_dataset)

## 2.6 Physics

**[Overview](Documentation/lessons/physx/overview.md)**

### 2.6.1 Physics (PhysX)

1. [PhysX](Documentation/lessons/physx/physx.md)
2. [Object physics parameters](Documentation/lessons/physx/physics_objects.md)
3. [`Rigidbodies` output data](Documentation/lessons/physx/rigidbodies.md)
4. [`Collision` output data](Documentation/lessons/physx/collisions.md)
5. [Apply forces to objects](Documentation/lessons/physx/forces.md)
6. [Composite objects (objects with affordances)](Documentation/lessons/physx/composite_objects.md)
7. [Skip physics frames](Documentation/lessons/physx/step_physics.md)
8. [Disable physics](Documentation/lessons/physx/disable_physics.md)

High-level API: [tdw_physics](https://github.com/alters-mit/tdw_physics)

### 2.6.2 Physics (Flex)

1. [Flex](Documentation/lessons/flex/flex.md)
2. [Solid and soft actors](Documentation/lessons/flex/solid_and_soft.md)
3. [Cloth actors](Documentation/lessons/flex/cloth.md)
4. [Fluid and source actors](Documentation/lessons/flex/fluid_and_source.md)
5. [Move, rotate, and scale Flex objects](Documentation/lessons/flex/transform.md)
6. [`FlexParticles` output data](Documentation/lessons/flex/output_data.md)
7. [Apply forces to Flex objects](Documentation/lessons/flex/forces.md)
8. [Reset a Flex scene](Documentation/lessons/flex/reset_scene.md)
8. [Other Flex commands](Documentation/lessons/flex/other_commands.md)

High-level API: [tdw_physics](https://github.com/alters-mit/tdw_physics)

## 2.8 Audio

1. [Overview](Documentation/lessons/audio/overview.md)
2. [Initialize audio and play .wav files](Documentation/lessons/audio/initialize_audio.md)
3. [Resonance Audio](Documentation/lessons/audio/resonance_audio.md)
4. [`PyImpact` (dynamic impact sounds)](Documentation/lessons/audio/py_impact.md)
6. [Recording audio](Documentation/lessons/audio/record_audio.md)
6. [`PyImpact` (advanced API)](Documentation/lessons/audio/py_impact_advanced.md)
7. [Audio perception](Documentation/lessons/audio/audio_perception.md)

## 2.9 Video Recording

1. [Overview](Documentation/lessons/video/overview.md)
2. [Image-only video](Documentation/lessons/video/images.md)
3. [Video with audio](Documentation/lessons/video/audio.md)

## 2.10 Agents

[**Overview**](Documentation/lessons/agents/overview.md)

### 2.10.1 Robots

1. [Overview](Documentation/lessons/robots/overview.md)
2. [The `Robot` add-on](Documentation/lessons/robots/robot_add_on.md)
3. [Robot arm add-ons](Documentation/lessons/robots/robot_arm.md)
4. [Robot collision detection](Documentation/lessons/robots/collision_detection.md)
5. [Select a robot](Documentation/lessons/robots/select_robot.md)
6. [Add your own robots to TDW](Documentation/lessons/robots/custom_robots.md)
7. [Robotics API (low-level)](Documentation/lessons/robots/custom_robots.md)
8. [Add a camera to a robot](Documentation/lessons/robots/add_camera.md)

### 2.10.2 Magnebots

1. [Magnebot API (external repo)](https://github.com/alters-mit/magnebot)

### 2.10.3 Human user interaction

1. [Overview](Documentation/lessons/humans/overview.md)
2. [Keyboard controls](Documentation/lessons/humans/overview.md)
3. [Virtual reality](Documentation/lessons/humans/vr.md)

### 2.10.4 Embodied avatars

1. [The `EmbodiedAvatar`](Documentation/lessons/embodied_avatars/embodied_avatar.md)

## 2.11 Multi-agent simulations

1. [Overview](Documentation/lessons/multi_agent/overview.md)
2. [Custom agent classes](Documentation/lessons/multi_agent/custom_agent_classes.md)

## 2.12 Navigation

1. [Overview](Documentation/lessons/navigation/overview.md)
2. [NavMesh pathfinding](Documentation/lessons/navigation/nav_mesh.md)
3. [Occupancy maps](Documentation/lessons/navigation/occupancy_maps.md)

## 2.13 Non-physics objects

1. [Overview](Documentation/lessons/non_physics/overview.md)
2. [Position markers](Documentation/lessons/non_physics/position_markers.md)
3. [Textured quads](Documentation/lessons/non_physics/textured_quads.md)
4. [Non-physics humanoids](Documentation/lessons/non_physics/humanoids.md)

## 2.14 Misc. remote server topics

1. [Launch a TDW build on a remote server from a personal computer](Documentation/lessons/remote/launch_build.md)
2. [Remote rendering with xpra](Documentation/lessons/remote/xpra.md)

## 2.15 Misc. other topics

1. [C# source code](Documentation/lessons/misc/c_sharp_sources.md)
2. [Freezing your code](Documentation/lessons/misc/freeze.md)

# 3. API Documentation

## 3.1 Command API

- [Command API](Documentation/api/command_api.md)
- [Output Data](Documentation/api/output_data.md)

## 3.2 `tdw` module API

**tdw**

- [AssetBundleCreator](Documentation/python/asset_bundle_creator.md)
- [AssetBundleCreatorBase](Documentation/python/asset_bundle_creator_base.md)
- [AudioUtils](Documentation/python/audio_utils.md)
- [Controller](Documentation/python/controller.md)
- [IntPair](Documentation/python/int_pair.md)
- [QuaternionUtils](Documentation/python/quaternion_utils.md)
- [RemoteBuildLauncher](Documentation/python/remote_build_launcher.md)
- [RobotCreator](Documentation/python/robot_creator.md)
- [TDWUtils](Documentation/python/tdw_utils.md)

**tdw.add_ons**

- [AddOn](Documentation/python/add_ons/add_on.md)
- [AudioInitializer](Documentation/python/add_ons/audio_initializer.md)
- [AudioInitializerBase](Documentation/python/add_ons/audio_initializer_base.md)
- [AvatarBody](Documentation/python/add_ons/avatar_body.md)
- [Benchmark](Documentation/python/add_ons/benchmark.md)
- [CinematicCamera](Documentation/python/add_ons/cinematic_camera.md)
- [CollisionManager](Documentation/python/add_ons/collision_manager.md)
- [EmbodiedAvatar](Documentation/python/add_ons/embodied_avatar.md)
- [Floorplan](Documentation/python/add_ons/floorplan.md)
- [ImageCapture](Documentation/python/add_ons/image_capture.md)
- [Keyboard](Documentation/python/add_ons/keyboard.md)
- [Logger](Documentation/python/add_ons/logger.md)
- [ModelVerifier](Documentation/python/add_ons/model_verifier.md)
- [ObjectManager](Documentation/python/add_ons/object_manager.md)
- [OccupancyMap](Documentation/python/add_ons/occupancy_map.md)
- [PhysicsAudioRecorder](Documentation/python/add_ons/physics_audio_recorder.md)
- [PyImpact](Documentation/python/add_ons/py_impact.md)
- [ResonanceAudioInitializer](Documentation/python/add_ons/resonance_audio_initializer.md)
- [Robot](Documentation/python/add_ons/robot.md)
- [RobotArm](Documentation/python/add_ons/robot_arm.md)
- [RobotBase](Documentation/python/add_ons/robot_base.md)
- [StepPhysics](Documentation/python/add_ons/step_physics.md)
- [ThirdPersonCamera](Documentation/python/add_ons/third_person_camera.md)
- [ThirdPersonCameraBase](Documentation/python/add_ons/third_person_camera_base.md)

**tdw.collision_data**

- [CollisionBase](Documentation/python/collision_data/collision_base.md)
- [CollisionObjEnv](Documentation/python/collision_data/collision_obj_env.md)
- [CollisionObjObj](Documentation/python/collision_data/collision_obj_obj.md)

**tdw.flex_data**

- [FluidType](Documentation/python/flex_data/fluid_type.md)

**tdw.librarian**

- [HdriSkyboxLibrarian](Documentation/python/librarian/hdri_skybox_librarian.md)
- [HumanoidAnimationLibrarian](Documentation/python/librarian/humanoid_animation_librarian.md)
- [HumanoidLibrarian](Documentation/python/librarian/humanoid_librarian.md)
- [MaterialLibrarian](Documentation/python/librarian/material_librarian.md)
- [ModelLibrarian](Documentation/python/librarian/model_librarian.md)
- [RobotLibrarian](Documentation/python/librarian/robot_librarian.md)
- [SceneLibrarian](Documentation/python/librarian/scene_librarian.md)

**tdw.model_tests**

- [MissingMaterials](Documentation/python/model_tests/missing_materials.md)
- [ModelReport](Documentation/python/model_tests/model_report.md)
- [ModelTest](Documentation/python/model_tests/model_test.md)
- [PhysicsQuality](Documentation/python/model_tests/physics_quality.md)
- [RotateObjectTest](Documentation/python/model_tests/rotate_object_test.md)

**tdw.object_data**

- [Bound](Documentation/python/object_data/bound.md)
- [ObjectStatic](Documentation/python/object_data/object_static.md)
- [Rigidbody](Documentation/python/object_data/rigidbody.md)
- [Transform](Documentation/python/object_data/transform.md)

**tdw.physics_audio**

- [AudioMaterial](Documentation/python/physics_audio/audio_material.md)
- [Base64Sound](Documentation/python/physics_audio/base64_sound.md)
- [CollisionAudioEvent](Documentation/python/physics_audio/collision_audio_event.md)
- [CollisionAudioInfo](Documentation/python/physics_audio/collision_audio_info.md)
- [CollisionAudioType](Documentation/python/physics_audio/collision_audio_type.md)
- [Modes](Documentation/python/physics_audio/modes.md)
- [ObjectAudioStatic](Documentation/python/physics_audio/object_audio_static.md)
- [ScrapeMaterial](Documentation/python/physics_audio/scrape_material.md)
- [ScrapeModel](Documentation/python/physics_audio/scrape_model.md)
- [ScrapeSubObject](Documentation/python/physics_audio/scrape_sub_object.md)

**tdw.release**

- [Build](Documentation/python/release/build.md)
- [Pypi](Documentation/python/release/pypi.md)

**tdw.robot_data**

- [Drive](Documentation/python/robot_data/drive.md)
- [JointDynamic](Documentation/python/robot_data/joint_dynamic.md)
- [JointStatic](Documentation/python/robot_data/joint_static.md)
- [JointType](Documentation/python/robot_data/joint_type.md)
- [NonMoving](Documentation/python/robot_data/non_moving.md)
- [RobotDynamic](Documentation/python/robot_data/robot_dynamic.md)
- [RobotStatic](Documentation/python/robot_data/robot_static.md)

**tdw.scene_data**

- [RegionBounds](Documentation/python/scene_data/region_bounds.md)
- [SceneBounds](Documentation/python/scene_data/scene_bounds.md)

# 4. Performance benchmarks
1. [Performance benchmarks](Documentation/benchmark/benchmark.md)
2. [Image capture](Documentation/benchmark/image_capture.md)
3. [Object data](Documentation/benchmark/object_data.md)
4. [Command deserialization](Documentation/benchmark/command_deserialization.md)

