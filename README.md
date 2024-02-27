# ThreeDWorld (TDW)

**ThreeDWorld (TDW)** is a platform for interactive multi-modal physical simulation. With TDW, users can simulate high-fidelity sensory data and physical interactions between mobile agents and objects in a wide variety of rich 3D environments.

![](splash.jpg)

- [Code of Conduct](https://github.com/threedworld-mit/tdw/blob/master/code_of_conduct.md)
- [Changelog](https://github.com/threedworld-mit/tdw/blob/master/Documentation/Changelog.md)
- [License](https://github.com/threedworld-mit/tdw/blob/master/LICENSE.txt)
- [Website](https://threedworld.org/)
- [Example controllers](https://github.com/threedworld-mit/tdw/tree/master/Python/example_controllers)

# General guide to TDW

## Setup

### 1.1 Installation (Read this first!)

1. [Install TDW](Documentation/lessons/setup/install.md)
   - [On a personal computer (Linux, MacOS, Windows)](Documentation/lessons/setup/pc.md)
   - [On a server](Documentation/lessons/setup/server.md)
   - [On a personal computer + a server](Documentation/lessons/setup/pc_server.md)
2. [Upgrade TDW](Documentation/lessons/setup/upgrade.md)

### 1.2 How to run TDW on a Linux server

1. [Overview](Documentation/lessons/remote/overview.md)
2. [Launch a TDW build on a remote server from a personal computer](Documentation/lessons/remote/launch_build.md)
3. [Remote rendering with xpra](Documentation/lessons/remote/xpra.md)
4. [X11 forwarding](Documentation/lessons/remote/x11_forwarding.md)

## Core Concepts

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
11. [Outdoor scenes](Documentation/lessons/core_concepts/outdoor_scenes.md)

## Troubleshooting

1. [How to report an issue](Documentation/lessons/troubleshooting/issues.md)
2. [Common errors](Documentation/lessons/troubleshooting/common_errors.md)
3. [Performance optimizations](Documentation/lessons/troubleshooting/performance_optimizations.md)
4. [Good coding practices](Documentation/lessons/troubleshooting/good_coding_practices.md)

# Tutorials

## 1. Scene Setup

**[Overview](Documentation/lessons/scene_setup/overview.md)**

### 1.1 Scene Setup (High-Level APIs)

1. [Overview](Documentation/lessons/scene_setup_high_level/overview.md)
2. [Procedural generation (the `ProcGenKitchen` add-on)](Documentation/lessons/scene_setup_high_level/proc_gen_kitchen.md)
2. [Regions, interior regions, and rooms](Documentation/lessons/scene_setup_high_level/rooms.md)
3. [Procedural object arrangements](Documentation/lessons/scene_setup_high_level/arrangements.md)
4. [Scripted object placement (floorplan layouts)](Documentation/lessons/scene_setup_high_level/floorplans.md)
5. [Reset a scene](Documentation/lessons/scene_setup_high_level/reset_scene.md)

High-level APs: [Floorplan](Documentation/python/add_ons/floorplan.md) and [ProcGenKitchen](Documentation/python/add_ons/proc_gen_kitchen.md)

### 1.2 Scene Setup (Low-Level APIs)

1. [Overview](Documentation/lessons/scene_setup_low_level/overview.md)
2. [Units and data formats](Documentation/lessons/scene_setup_low_level/units.md)
3. [`Bounds` output data](Documentation/lessons/scene_setup_low_level/bounds.md)
4. [Visual materials, textures, and colors](Documentation/lessons/scene_setup_low_level/materials_textures_colors.md)
5. [ProcGenRoom](Documentation/lessons/scene_setup_low_level/proc_gen_room.md)

## 2. 3D Models

### 2.1 Other model libraries

1. [Overview](Documentation/lessons/3d_models/overview.md)
2. [Free models](Documentation/lessons/3d_models/free_models.md)
3. [Non-free models](Documentation/lessons/3d_models/non_free_models.md)

### 2.2 Custom models

1. [Add your own models to TDW](Documentation/lessons/custom_models/custom_models.md)
2. [Add ShapeNet models to TDW](Documentation/lessons/custom_models/shapenet.md)

### 2.3 Composite (articulated) objects

1. [Overview](Documentation/lessons/composite_objects/overview.md)
2. [Composite objects in TDW](Documentation/lessons/composite_objects/composite_objects.md)
3. [Create a composite object from a prefab](Documentation/lessons/composite_objects/create_from_prefab.md)
4. [Create a composite object from a .urdf file](Documentation/lessons/composite_objects/create_from_urdf.md)

## 3. Read/Write to Disk

1. [Overview](Documentation/lessons/read_write/overview.md)
2. [The `Logger` and `LogPlayback` add-ons](Documentation/lessons/read_write/logger.md)
3. [The `JsonWriter` add-on](Documentation/lessons/read_write/json.md)
4. [The `OutputDataWriter` add-on](Documentation/lessons/read_write/output_data_writer.md)
5. [Create a custom data writer](Documentation/lessons/read_write/custom_writers.md)
6. [Import .sdf and .lisdf files](Documentation/lessons/read_write/lisdf.md)
7. [Images](Documentation/lessons/core_concepts/images.md) (Cross-referenced with "Core Concepts")
8. [Audio](Documentation/lessons/audio/overview.md) (Cross-referenced with "Audio")
9. [Video](Documentation/lessons/video/overview.md) (Cross-referenced with "Video Recording")

## 4. Semantic States

1. [Overview](Documentation/lessons/semantic_states/overview.md)
2. [Line of sight (`Raycast` output data)](Documentation/lessons/semantic_states/raycast.md)
3. [Proximity to region (`Overlap` output data)](Documentation/lessons/semantic_states/overlap.md)
3. [Proximity to other objects (the `TriggerCollisionManager` add-on)](Documentation/lessons/semantic_states/trigger_collisions.md)
3. [Containment (the `ContainerManager` add-on)](Documentation/lessons/semantic_states/containment.md)
4. [Open and closed states](Documentation/lessons/semantic_states/openness.md)
4. [Grasped objects](Documentation/lessons/semantic_states/grasped.md)

## 5. Visual Perception

1. [Overview](Documentation/lessons/visual_perception/overview.md)
2. [Instance ID segmentation colors (`_id` pass)](Documentation/lessons/visual_perception/id.md)
3. [Semantic category segmentation colors (`_category` pass)](Documentation/lessons/visual_perception/category.md)
4. [Depth maps (`_depth` and `_depth_simple` passes)](Documentation/lessons/visual_perception/depth.md)
5. [Motion perception (`_flow` pass)](Documentation/lessons/visual_perception/flow.md)
6. [Other image passes (`_mask`, `_normals`, and `_albedo` passes)](Documentation/lessons/visual_perception/other_passes.md)
7. [`Occlusion` output data](Documentation/lessons/visual_perception/occlusion.md)

## 6. Camera Controls

1. [Overview](Documentation/lessons/camera/overview.md)
2. [Move a camera](Documentation/lessons/camera/position.md)
3. [Rotate a camera](Documentation/lessons/camera/rotation.md)
4. [Follow an object](Documentation/lessons/camera/follow.md)
4. [The `CinematicCamera` add-on](Documentation/lessons/camera/cinematic_camera.md)

## 7. Photorealism

1. [Overview](Documentation/lessons/photorealism/overview.md)
2. [Lighting (HDRI skyboxes)](Documentation/lessons/photorealism/lighting.md)
3. [Post-processing](Documentation/lessons/photorealism/post_processing.md)
4. [Interior lighting (the `InteriorSceneLighting` add-on)](Documentation/lessons/photorealism/interior_lighting.md)
5. [Depth of field](Documentation/lessons/photorealism/depth_of_field.md)
6. [V-Ray Rendering](Documentation/lessons/photorealism/vray.md)

High-level API: [tdw_image_dataset](https://github.com/alters-mit/tdw_image_dataset)

## 8. Physics

**[Overview](Documentation/lessons/physx/overview.md)**

### 8.1 Physics (PhysX)

1. [PhysX](Documentation/lessons/physx/physx.md)
2. [Object physics parameters](Documentation/lessons/physx/physics_objects.md)
3. [`Rigidbodies` output data](Documentation/lessons/physx/rigidbodies.md)
4. [`Collision` output data](Documentation/lessons/physx/collisions.md)
5. [Apply forces to objects](Documentation/lessons/physx/forces.md)
6. [Skip physics frames](Documentation/lessons/physx/step_physics.md)
7. [Disable physics](Documentation/lessons/physx/disable_physics.md)

High-level API: [tdw_physics](https://github.com/alters-mit/tdw_physics)

### 8.2 Physics (Obi)

1. [Obi](Documentation/lessons/obi/obi.md)
2. [Fluids](Documentation/lessons/obi/fluids.md)
3. [Wind](Documentation/lessons/obi/wind.md)
4. [Cloth](Documentation/lessons/obi/cloth.md)
5. [`ObiParticles` output data](Documentation/lessons/obi/obi_particles.md)
6. [Colliders and collision materials](Documentation/lessons/obi/colliders_and_collision_materials.md)
7. [Solvers](Documentation/lessons/obi/solvers.md)
8. [Obi and robots](Documentation/lessons/obi/robots.md)

High-level API: [tdw_physics](https://github.com/alters-mit/tdw_physics)

## 9. Audio

1. [Overview](Documentation/lessons/audio/overview.md)
2. [Initialize audio and play .wav files](Documentation/lessons/audio/initialize_audio.md)
3. [Resonance Audio](Documentation/lessons/audio/resonance_audio.md)
4. [Recording audio](Documentation/lessons/audio/record_audio.md)
5. [Audio perception](Documentation/lessons/audio/audio_perception.md)

### 9.1 Clatter (Physically-derived audio)

1. [Overview](Documentation/lessons/clatter/overview.md)
2. [Object audio data](Documentation/lessons/clatter/clatter_objects.md)
3. [Recording Clatter audio with the `PhysicsAudioRecorder` add-on](Documentation/lessons/clatter/record_clatter.md)
4. [Clatter and Resonance Audio](Documentation/lessons/clatter/resonance_audio.md)
5. [Reset Clatter](Documentation/lessons/clatter/reset.md)
6. [Manually generate audio](Documentation/lessons/clatter/cli.md)
7. [Troubleshooting Clatter](Documentation/lessons/clatter/troubleshooting.md)
8. [How to contribute to Clatter](Documentation/lessons/clatter/contribute.md)

### 9.2 PyImpact (obsolete predecessor to Clatter)

1. [PyImpact](Documentation/lessons/py_impact/py_impact.md)
2. [PyImpact advanced](Documentation/lessons/py_impact/py_impact_advanced.md)
3. [PyImpact and Clatter](Documentation/lessons/py_impact/py_impact_and_clatter.md)

## 10. Video Recording

1. [Overview](Documentation/lessons/video/overview.md)
2. [Image-only video](Documentation/lessons/video/images.md)
3. [Video with audio](Documentation/lessons/video/audio.md)
   1. [Video with audio (Linux)](Documentation/lessons/video/screen_record_linux.md)
   2. [Video with audio (OS X)](Documentation/lessons/video/screen_record_osx.md)
   3. [Video with audio (Windows)](Documentation/lessons/video/screen_record_windows.md)


## 11. Agents

[**Overview**](Documentation/lessons/agents/overview.md)

### 11.1 Robots

1. [Overview](Documentation/lessons/robots/overview.md)
2. [The `Robot` add-on](Documentation/lessons/robots/robot_add_on.md)
3. [Robot arm add-ons](Documentation/lessons/robots/robot_arm.md)
4. [Robot collision detection](Documentation/lessons/robots/collision_detection.md)
5. [Select a robot](Documentation/lessons/robots/select_robot.md)
6. [Add your own robots to TDW](Documentation/lessons/robots/custom_robots.md)
7. [Robotics API (low-level)](Documentation/lessons/robots/custom_robots.md)
8. [Add a camera to a robot](Documentation/lessons/robots/add_camera.md)

### 11.2 Magnebots

1. [Magnebot API (external repo)](https://github.com/alters-mit/magnebot)

### 11.3 Replicants

1. [Overview](Documentation/lessons/replicants/overview.md)
2. [Actions](Documentation/lessons/replicants/actions.md)
3. [Output data](Documentation/lessons/replicants/output_data.md)
4. [Collision detection](Documentation/lessons/replicants/collision_detection.md)
5. [Movement](Documentation/lessons/replicants/movement.md)
6. [Animations](Documentation/lessons/replicants/animations.md)
7. [Arm articulation, pt. 1: Basics](Documentation/lessons/replicants/arm_articulation_1.md)
8. [Arm articulation, pt. 2: Grasp and drop objects](Documentation/lessons/replicants/arm_articulation_2.md)
9. [Arm articulation, pt. 3: Advanced topics](Documentation/lessons/replicants/arm_articulation_3.md)
10. [Arm articulation, pt. 4: Stacking objects](Documentation/lessons/replicants/arm_articulation_4.md)
11. [Head rotation](Documentation/lessons/replicants/head_rotation.md)
12. [Navigation](Documentation/lessons/replicants/navigation.md)
13. [Custom actions](Documentation/lessons/replicants/custom_actions.md)
14. [Multiple Replicants](Documentation/lessons/replicants/multiple_replicants.md)
15. [Reset](Documentation/lessons/replicants/reset.md)

### 11.4 Wheelchair Replicants

1. [Overview](Documentation/lessons/wheelchair_replicants/overview.md)
2. [Actions](Documentation/lessons/wheelchair_replicants/actions.md)
3. [Output data](Documentation/lessons/wheelchair_replicants/output_data.md)
4. [Collision detection](Documentation/lessons/wheelchair_replicants/collision_detection.md)
5. [Movement](Documentation/lessons/wheelchair_replicants/movement.md)
6. [Arm articulation, pt. 1: Basics](Documentation/lessons/wheelchair_replicants/arm_articulation_1.md)
7. [Arm articulation, pt. 2: Grasp and drop objects](Documentation/lessons/wheelchair_replicants/arm_articulation_2.md)
8. [Arm articulation, pt. 3: Advanced topics](Documentation/lessons/wheelchair_replicants/arm_articulation_3.md)
9. [Head rotation](Documentation/lessons/wheelchair_replicants/head_rotation.md)
10. [Navigation](Documentation/lessons/wheelchair_replicants/navigation.md)
11. [Custom actions](Documentation/lessons/wheelchair_replicants/custom_actions.md)
12. [Multiple Agents](Documentation/lessons/wheelchair_replicants/multiple_agents.md)
13. [Reset](Documentation/lessons/wheelchair_replicants/reset.md)

### 11.5 Drones

1. [Drones](Documentation/lessons/drone/drone.md)

### 11.6 Vehicles

1. [Vehicles](Documentation/lessons/vehicle/vehicle.md)

### 11.7 Virtual Reality (VR)

1. [Overview](Documentation/lessons/vr/overview.md)
2. [Oculus Touch](Documentation/lessons/vr/oculus_touch.md)
3. [Oculus Leap Motion](Documentation/lessons/vr/oculus_leap_motion.md)

### 11.8 Keyboard and Mouse

1. [Overview](Documentation/lessons/keyboard_and_mouse/overview.md)
2. [Mouse input](Documentation/lessons/keyboard_and_mouse/mouse.md)
3. [The `FirstPersonAvatar`](Documentation/lessons/keyboard_and_mouse/first_person_avatar.md)
4. [Keyboard input](Documentation/lessons/keyboard_and_mouse/keyboard.md)

### 11.9 Embodied avatars

1. [The `EmbodiedAvatar`](Documentation/lessons/embodied_avatars/embodied_avatar.md)

## 12. Multi-agent simulations

1. [Overview](Documentation/lessons/multi_agent/overview.md)
2. [Custom agent classes](Documentation/lessons/multi_agent/custom_agent_classes.md)

## 13. Navigation

1. [Overview](Documentation/lessons/navigation/overview.md)
2. [NavMesh pathfinding](Documentation/lessons/navigation/nav_mesh.md)
3. [Occupancy maps](Documentation/lessons/navigation/occupancy_maps.md)

## 14. User Interface (UI)

1. [Overview](Documentation/lessons/ui/overview.md)
2. [The `UI` add-on](Documentation/lessons/ui/ui.md)
3. [UI Widgets](Documentation/lessons/ui/widgets.md)

## 15. Non-physics objects

### 15.1 Non-physics humanoids

1. [Overview](Documentation/lessons/non_physics_humanoids/overview.md)
2. [SMPL humanoids](Documentation/lessons/non_physics_humanoids/smpl.md)
3. [Create custom non-physics humanoids](Documentation/lessons/non_physics_humanoids/custom_humanoids.md)
4. [Create custom humanoid animations](Documentation/lessons/non_physics_humanoids/custom_animations.md)

### 15.2 Misc. non-physics objects

1. [Overview](Documentation/lessons/non_physics/overview.md)
2. [Position markers](Documentation/lessons/non_physics/position_markers.md)
3. [Line renderers](Documentation/lessons/non_physics/line_renderers.md)
4. [Textured quads](Documentation/lessons/non_physics/textured_quads.md)
5. [Compass rose](Documentation/lessons/non_physics/compass_rose.md)
6. [Visual Effects](Documentation/lessons/non_physics/visual_effects.md)
7. [The `FloorplanFlood` add-on](Documentation/lessons/non_physics/floorplan_flood.md)
8. [Empty objects](Documentation/lessons/non_physics/empty_objects.md)

## 16. Misc. other topics

1. [C# source code](Documentation/lessons/misc/c_sharp_sources.md)
2. [Freezing your code](Documentation/lessons/misc/freeze.md)
3. [Download asset bundles](Documentation/lessons/misc/download_asset_bundles.md)

# API Documentation

## Command API

- [Command API](Documentation/api/command_api.md)
- [Output Data](Documentation/api/output_data.md)

## `tdw` module API

**tdw**

- [AudioConstants](Documentation/python/audio_constants.md)
- [AudioUtils](Documentation/python/audio_utils.md)
- [CardinalDirection](Documentation/python/cardinal_direction.md)
- [Controller](Documentation/python/controller.md)
- [IntPair](Documentation/python/int_pair.md)
- [OrdinalDirection](Documentation/python/ordinal_direction.md)
- [QuaternionUtils](Documentation/python/quaternion_utils.md)
- [RemoteBuildLauncher](Documentation/python/remote_build_launcher.md)
- [TDWUtils](Documentation/python/tdw_utils.md)
- [TypeAliases](Documentation/python/type_aliases.md)

**tdw.add_ons**

- [AddOn](Documentation/python/add_ons/add_on.md)
- [AudioInitializer](Documentation/python/add_ons/audio_initializer.md)
- [AudioInitializerBase](Documentation/python/add_ons/audio_initializer_base.md)
- [AvatarBody](Documentation/python/add_ons/avatar_body.md)
- [Benchmark](Documentation/python/add_ons/benchmark.md)
- [CinematicCamera](Documentation/python/add_ons/cinematic_camera.md)
- [Clatter](Documentation/python/add_ons/clatter.md)
- [CollisionManager](Documentation/python/add_ons/collision_manager.md)
- [CompositeObjectManager](Documentation/python/add_ons/composite_object_manager.md)
- [ContainerManager](Documentation/python/add_ons/container_manager.md)
- [Drone](Documentation/python/add_ons/drone.md)
- [EmbodiedAvatar](Documentation/python/add_ons/embodied_avatar.md)
- [EmptyObjectManager](Documentation/python/add_ons/empty_object_manager.md)
- [FirstPersonAvatar](Documentation/python/add_ons/first_person_avatar.md)
- [Floorplan](Documentation/python/add_ons/floorplan.md)
- [FloorplanFlood](Documentation/python/add_ons/floorplan_flood.md)
- [ImageCapture](Documentation/python/add_ons/image_capture.md)
- [InteriorSceneLighting](Documentation/python/add_ons/interior_scene_lighting.md)
- [JsonWriter](Documentation/python/add_ons/json_writer.md)
- [Keyboard](Documentation/python/add_ons/keyboard.md)
- [LisdfReader](Documentation/python/add_ons/lisdf_reader.md)
- [Logger](Documentation/python/add_ons/logger.md)
- [LogPlayback](Documentation/python/add_ons/log_playback.md)
- [ModelVerifier](Documentation/python/add_ons/model_verifier.md)
- [Mouse](Documentation/python/add_ons/mouse.md)
- [NavMesh](Documentation/python/add_ons/nav_mesh.md)
- [Obi](Documentation/python/add_ons/obi.md)
- [ObjectManager](Documentation/python/add_ons/object_manager.md)
- [OccupancyMap](Documentation/python/add_ons/occupancy_map.md)
- [OculusLeapMotion](Documentation/python/add_ons/oculus_leap_motion.md)
- [OculusTouch](Documentation/python/add_ons/oculus_touch.md)
- [OutputDataWriter](Documentation/python/add_ons/output_data_writer.md)
- [PhysicsAudioRecorder](Documentation/python/add_ons/physics_audio_recorder.md)
- [ProcGenKitchen](Documentation/python/add_ons/proc_gen_kitchen.md)
- [PyImpact](Documentation/python/add_ons/py_impact.md)
- [Replicant](Documentation/python/add_ons/replicant.md)
- [ReplicantBase](Documentation/python/add_ons/replicant_base.md)
- [ResonanceAudioInitializer](Documentation/python/add_ons/resonance_audio_initializer.md)
- [Robot](Documentation/python/add_ons/robot.md)
- [RobotArm](Documentation/python/add_ons/robot_arm.md)
- [RobotBase](Documentation/python/add_ons/robot_base.md)
- [StepPhysics](Documentation/python/add_ons/step_physics.md)
- [ThirdPersonCamera](Documentation/python/add_ons/third_person_camera.md)
- [ThirdPersonCameraBase](Documentation/python/add_ons/third_person_camera_base.md)
- [TriggerCollisionManager](Documentation/python/add_ons/trigger_collision_manager.md)
- [UI](Documentation/python/add_ons/ui.md)
- [Vehicle](Documentation/python/add_ons/vehicle.md)
- [VR](Documentation/python/add_ons/vr.md)
- [VrayExporter](Documentation/python/add_ons/vray_exporter.md)
- [WheelchairReplicant](Documentation/python/add_ons/wheelchair_replicant.md)
- [Writer](Documentation/python/add_ons/writer.md)

**tdw.add_ons.ui_widgets**

- [LoadingScreen](Documentation/python/add_ons/ui_widgets/loading_screen.md)
- [ProgressBar](Documentation/python/add_ons/ui_widgets/progress_bar.md)
- [TimerBar](Documentation/python/add_ons/ui_widgets/timer_bar.md)

**tdw.agent_data**

- [AgentDynamic](Documentation/python/agent_data/agent_dynamic.md)

**tdw.asset_bundle_creator**

- [AnimationCreator](Documentation/python/asset_bundle_creator/animation_creator.md)
- [AssetBundleCreator](Documentation/python/asset_bundle_creator/asset_bundle_creator.md)
- [CompositeObjectCreator](Documentation/python/asset_bundle_creator/composite_object_creator.md)
- [HumanoidCreator](Documentation/python/asset_bundle_creator/humanoid_creator.md)
- [HumanoidCreatorBase](Documentation/python/asset_bundle_creator/humanoid_creator_base.md)
- [ModelCreator](Documentation/python/asset_bundle_creator/model_creator.md)
- [RobotCreator](Documentation/python/asset_bundle_creator/robot_creator.md)

**tdw.backend**

- [Update](Documentation/python/backend/update.md)

**tdw.collision_data**

- [CollisionBase](Documentation/python/collision_data/collision_base.md)
- [CollisionObjEnv](Documentation/python/collision_data/collision_obj_env.md)
- [CollisionObjObj](Documentation/python/collision_data/collision_obj_obj.md)
- [TriggerColliderShape](Documentation/python/collision_data/trigger_collider_shape.md)
- [TriggerCollisionEvent](Documentation/python/collision_data/trigger_collision_event.md)

**tdw.container_data**

- [BoxContainer](Documentation/python/container_data/box_container.md)
- [ContainerShape](Documentation/python/container_data/container_shape.md)
- [ContainerTag](Documentation/python/container_data/container_tag.md)
- [ContainmentEvent](Documentation/python/container_data/containment_event.md)
- [CylinderContainer](Documentation/python/container_data/cylinder_container.md)
- [SphereContainer](Documentation/python/container_data/sphere_container.md)

**tdw.drone**

- [DroneDynamic](Documentation/python/drone/drone_dynamic.md)

**tdw.flex_data**

- [FluidType](Documentation/python/flex_data/fluid_type.md)

**tdw.lerp**

- [Lerpable](Documentation/python/lerp/lerpable.md)
- [LerpableFloat](Documentation/python/lerp/lerpable_float.md)
- [LerpableVector](Documentation/python/lerp/lerpable_vector.md)

**tdw.librarian**

- [DroneLibrarian](Documentation/python/librarian/drone_librarian.md)
- [HdriSkyboxLibrarian](Documentation/python/librarian/hdri_skybox_librarian.md)
- [HumanoidAnimationLibrarian](Documentation/python/librarian/humanoid_animation_librarian.md)
- [HumanoidLibrarian](Documentation/python/librarian/humanoid_librarian.md)
- [MaterialLibrarian](Documentation/python/librarian/material_librarian.md)
- [ModelLibrarian](Documentation/python/librarian/model_librarian.md)
- [RobotLibrarian](Documentation/python/librarian/robot_librarian.md)
- [SceneLibrarian](Documentation/python/librarian/scene_librarian.md)
- [VehicleLibrarian](Documentation/python/librarian/vehicle_librarian.md)
- [VisualEffectLibrarian](Documentation/python/librarian/visual_effect_librarian.md)

**tdw.lisdf_data**

- [LisdfRobotMetadata](Documentation/python/lisdf_data/lisdf_robot_metadata.md)

**tdw.model_tests**

- [MissingMaterials](Documentation/python/model_tests/missing_materials.md)
- [ModelReport](Documentation/python/model_tests/model_report.md)
- [ModelTest](Documentation/python/model_tests/model_test.md)
- [PhysicsQuality](Documentation/python/model_tests/physics_quality.md)
- [RotateObjectTest](Documentation/python/model_tests/rotate_object_test.md)

**tdw.obi_data**

- [ForceMode](Documentation/python/obi_data/force_mode.md)
- [ObiActor](Documentation/python/obi_data/obi_actor.md)
- [ObiBackend](Documentation/python/obi_data/obi_backend.md)
- [WindSource](Documentation/python/obi_data/wind_source.md)

**tdw.obi_data.cloth**

- [ClothMaterial](Documentation/python/obi_data/cloth/cloth_material.md)
- [SheetType](Documentation/python/obi_data/cloth/sheet_type.md)
- [TetherParticleGroup](Documentation/python/obi_data/cloth/tether_particle_group.md)
- [TetherType](Documentation/python/obi_data/cloth/tether_type.md)
- [VolumeType](Documentation/python/obi_data/cloth/volume_type.md)

**tdw.obi_data.collision_materials**

- [CollisionMaterial](Documentation/python/obi_data/collision_materials/collision_material.md)
- [MaterialCombineMode](Documentation/python/obi_data/collision_materials/material_combine_mode.md)

**tdw.obi_data.fluids**

- [CubeEmitter](Documentation/python/obi_data/fluids/cube_emitter.md)
- [DiskEmitter](Documentation/python/obi_data/fluids/disk_emitter.md)
- [EdgeEmitter](Documentation/python/obi_data/fluids/edge_emitter.md)
- [EmitterSamplingMethod](Documentation/python/obi_data/fluids/emitter_sampling_method.md)
- [EmitterShape](Documentation/python/obi_data/fluids/emitter_shape.md)
- [Fluid](Documentation/python/obi_data/fluids/fluid.md)
- [FluidBase](Documentation/python/obi_data/fluids/fluid_base.md)
- [GranularFluid](Documentation/python/obi_data/fluids/granular_fluid.md)
- [SphereEmitter](Documentation/python/obi_data/fluids/sphere_emitter.md)

**tdw.object_data**

- [Bound](Documentation/python/object_data/bound.md)
- [ObjectStatic](Documentation/python/object_data/object_static.md)
- [Rigidbody](Documentation/python/object_data/rigidbody.md)
- [Transform](Documentation/python/object_data/transform.md)

**tdw.object_data.composite_object**

- [CompositeObjectDynamic](Documentation/python/object_data/composite_object/composite_object_dynamic.md)
- [CompositeObjectStatic](Documentation/python/object_data/composite_object/composite_object_static.md)

**tdw.object_data.composite_object.sub_object**

- [HingeDynamic](Documentation/python/object_data/composite_object/sub_object/hinge_dynamic.md)
- [HingeStatic](Documentation/python/object_data/composite_object/sub_object/hinge_static.md)
- [HingeStaticBase](Documentation/python/object_data/composite_object/sub_object/hinge_static_base.md)
- [LightDynamic](Documentation/python/object_data/composite_object/sub_object/light_dynamic.md)
- [LightStatic](Documentation/python/object_data/composite_object/sub_object/light_static.md)
- [MotorStatic](Documentation/python/object_data/composite_object/sub_object/motor_static.md)
- [NonMachineStatic](Documentation/python/object_data/composite_object/sub_object/non_machine_static.md)
- [PrismaticJointStatic](Documentation/python/object_data/composite_object/sub_object/prismatic_joint_static.md)
- [SpringStatic](Documentation/python/object_data/composite_object/sub_object/spring_static.md)
- [SubObjectDynamic](Documentation/python/object_data/composite_object/sub_object/sub_object_dynamic.md)
- [SubObjectStatic](Documentation/python/object_data/composite_object/sub_object/sub_object_static.md)

**tdw.physics_audio**

- [AudioMaterial](Documentation/python/physics_audio/audio_material.md)
- [Base64Sound](Documentation/python/physics_audio/base64_sound.md)
- [ClatterObject](Documentation/python/physics_audio/clatter_object.md)
- [CollisionAudioEvent](Documentation/python/physics_audio/collision_audio_event.md)
- [CollisionAudioInfo](Documentation/python/physics_audio/collision_audio_info.md)
- [CollisionAudioType](Documentation/python/physics_audio/collision_audio_type.md)
- [ImpactMaterial](Documentation/python/physics_audio/impact_material.md)
- [Modes](Documentation/python/physics_audio/modes.md)
- [ObjectAudioStatic](Documentation/python/physics_audio/object_audio_static.md)
- [ScrapeMaterial](Documentation/python/physics_audio/scrape_material.md)
- [ScrapeModel](Documentation/python/physics_audio/scrape_model.md)
- [ScrapeSubObject](Documentation/python/physics_audio/scrape_sub_object.md)

**tdw.proc_gen.arrangements**

- [Arrangement](Documentation/python/proc_gen/arrangements/arrangement.md)
- [ArrangementAlongWall](Documentation/python/proc_gen/arrangements/arrangement_along_wall.md)
- [ArrangementWithRootObject](Documentation/python/proc_gen/arrangements/arrangement_with_root_object.md)
- [Basket](Documentation/python/proc_gen/arrangements/basket.md)
- [CupAndCoaster](Documentation/python/proc_gen/arrangements/cup_and_coaster.md)
- [Dishwasher](Documentation/python/proc_gen/arrangements/dishwasher.md)
- [KitchenCabinet](Documentation/python/proc_gen/arrangements/kitchen_cabinet.md)
- [KitchenCounter](Documentation/python/proc_gen/arrangements/kitchen_counter.md)
- [KitchenCounterTop](Documentation/python/proc_gen/arrangements/kitchen_counter_top.md)
- [KitchenTable](Documentation/python/proc_gen/arrangements/kitchen_table.md)
- [Microwave](Documentation/python/proc_gen/arrangements/microwave.md)
- [Painting](Documentation/python/proc_gen/arrangements/painting.md)
- [Plate](Documentation/python/proc_gen/arrangements/plate.md)
- [Radiator](Documentation/python/proc_gen/arrangements/radiator.md)
- [Refrigerator](Documentation/python/proc_gen/arrangements/refrigerator.md)
- [Shelf](Documentation/python/proc_gen/arrangements/shelf.md)
- [SideTable](Documentation/python/proc_gen/arrangements/side_table.md)
- [Sink](Documentation/python/proc_gen/arrangements/sink.md)
- [StackOfPlates](Documentation/python/proc_gen/arrangements/stack_of_plates.md)
- [Stool](Documentation/python/proc_gen/arrangements/stool.md)
- [Stove](Documentation/python/proc_gen/arrangements/stove.md)
- [Suitcase](Documentation/python/proc_gen/arrangements/suitcase.md)
- [TableAndChairs](Documentation/python/proc_gen/arrangements/table_and_chairs.md)
- [TableSetting](Documentation/python/proc_gen/arrangements/table_setting.md)
- [Void](Documentation/python/proc_gen/arrangements/void.md)
- [WallCabinet](Documentation/python/proc_gen/arrangements/wall_cabinet.md)

**tdw.proc_gen.arrangements.cabinetry**

- [Cabinetry](Documentation/python/proc_gen/arrangements/cabinetry/cabinetry.md)
- [CabinetryType](Documentation/python/proc_gen/arrangements/cabinetry/cabinetry_type.md)

**tdw.release**

- [Build](Documentation/python/release/build.md)
- [PyPi](Documentation/python/release/pypi.md)

**tdw.replicant**

- [ActionStatus](Documentation/python/replicant/action_status.md)
- [Arm](Documentation/python/replicant/arm.md)
- [CollisionDetection](Documentation/python/replicant/collision_detection.md)
- [ImageFrequency](Documentation/python/replicant/image_frequency.md)
- [ReplicantBodyPart](Documentation/python/replicant/replicant_body_part.md)
- [ReplicantDynamic](Documentation/python/replicant/replicant_dynamic.md)
- [ReplicantStatic](Documentation/python/replicant/replicant_static.md)

**tdw.replicant.actions**

- [Action](Documentation/python/replicant/actions/action.md)
- [Animate](Documentation/python/replicant/actions/animate.md)
- [ArmMotion](Documentation/python/replicant/actions/arm_motion.md)
- [DoNothing](Documentation/python/replicant/actions/do_nothing.md)
- [Drop](Documentation/python/replicant/actions/drop.md)
- [Grasp](Documentation/python/replicant/actions/grasp.md)
- [HeadMotion](Documentation/python/replicant/actions/head_motion.md)
- [IkMotion](Documentation/python/replicant/actions/ik_motion.md)
- [LookAt](Documentation/python/replicant/actions/look_at.md)
- [MoveBy](Documentation/python/replicant/actions/move_by.md)
- [MoveTo](Documentation/python/replicant/actions/move_to.md)
- [ReachFor](Documentation/python/replicant/actions/reach_for.md)
- [ReachForWithPlan](Documentation/python/replicant/actions/reach_for_with_plan.md)
- [ResetArm](Documentation/python/replicant/actions/reset_arm.md)
- [ResetHead](Documentation/python/replicant/actions/reset_head.md)
- [RotateHead](Documentation/python/replicant/actions/rotate_head.md)
- [TurnBy](Documentation/python/replicant/actions/turn_by.md)
- [TurnTo](Documentation/python/replicant/actions/turn_to.md)

**tdw.replicant.ik_plans**

- [IkPlan](Documentation/python/replicant/ik_plans/ik_plan.md)
- [IkPlanType](Documentation/python/replicant/ik_plans/ik_plan_type.md)
- [Reset](Documentation/python/replicant/ik_plans/reset.md)
- [VerticalHorizontal](Documentation/python/replicant/ik_plans/vertical_horizontal.md)

**tdw.robot_data**

- [Drive](Documentation/python/robot_data/drive.md)
- [JointDynamic](Documentation/python/robot_data/joint_dynamic.md)
- [JointStatic](Documentation/python/robot_data/joint_static.md)
- [JointType](Documentation/python/robot_data/joint_type.md)
- [NonMoving](Documentation/python/robot_data/non_moving.md)
- [RobotDynamic](Documentation/python/robot_data/robot_dynamic.md)
- [RobotStatic](Documentation/python/robot_data/robot_static.md)

**tdw.scene_data**

- [InteriorRegion](Documentation/python/scene_data/interior_region.md)
- [RegionBounds](Documentation/python/scene_data/region_bounds.md)
- [Room](Documentation/python/scene_data/room.md)
- [SceneBounds](Documentation/python/scene_data/scene_bounds.md)

**tdw.vehicle**

- [VehicleDynamic](Documentation/python/vehicle/vehicle_dynamic.md)

**tdw.vray_data**

- [VrayMatrix](Documentation/python/vray_data/vray_matrix.md)

**tdw.vr_data**

- [FingerBone](Documentation/python/vr_data/finger_bone.md)
- [OculusTouchButton](Documentation/python/vr_data/oculus_touch_button.md)
- [RigType](Documentation/python/vr_data/rig_type.md)

**tdw.wheelchair_replicant**

- [WheelValues](Documentation/python/wheelchair_replicant/wheel_values.md)

**tdw.wheelchair_replicant.actions**

- [MoveBy](Documentation/python/wheelchair_replicant/actions/move_by.md)
- [MoveTo](Documentation/python/wheelchair_replicant/actions/move_to.md)
- [ReachFor](Documentation/python/wheelchair_replicant/actions/reach_for.md)
- [TurnBy](Documentation/python/wheelchair_replicant/actions/turn_by.md)
- [TurnTo](Documentation/python/wheelchair_replicant/actions/turn_to.md)
- [WheelchairMotion](Documentation/python/wheelchair_replicant/actions/wheelchair_motion.md)

# Performance benchmarks
1. [Performance benchmarks](Documentation/benchmark/benchmark.md)
2. [Image capture](Documentation/benchmark/image_capture.md)
3. [Object data](Documentation/benchmark/object_data.md)
4. [Command deserialization](Documentation/benchmark/command_deserialization.md)

