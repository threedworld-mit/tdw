# ThreeDWorld (TDW)
### A Platform for Interactive Multi-Modal Physical Simulation

**ThreeDWorld (TDW)** is a platform for interactive multi-modal physical simulation. With TDW, users can simulate high-fidelity sensory data and physical interactions between mobile agents and objects in a wide variety of rich 3D environments.

### [Getting Started](https://github.com/threedworld-mit/tdw/blob/master/Documentation/getting_started.md) (Read this first!)

### [Code of Conduct](https://github.com/threedworld-mit/tdw/blob/master/code_of_conduct.md)

### [Changelog](https://github.com/threedworld-mit/tdw/blob/master/Documentation/Changelog.md)

### [Website](http://threedworld.org/)

### [C# Code](https://github.com/threedworld-mit/tdw/blob/master/Documentation/contributions/c_sharp_sources.md)

### [License](https://github.com/threedworld-mit/tdw/blob/LICENSE.txt)

### [How to upgrade from TDW v1.6 to v1.7](https://github.com/threedworld-mit/tdw/blob/master/Documentation/v1.6_to_v1.7.md)

# API

#### Commands and Output Data

| Document                                                    | Description                                                  |
| ----------------------------------------------------------- | ------------------------------------------------------------ |
| [Command API](https://github.com/threedworld-mit/tdw/blob/master/Documentation/api/command_api.md)             | API for every command a controller can send to the build.    |
| [Command API Guide](https://github.com/threedworld-mit/tdw/blob/master/Documentation/api/command_api_guide.md) | Overview of how to send commands to the build.               |
| [Output Data](https://github.com/threedworld-mit/tdw/blob/master/Documentation/api/output_data.md)             | API for all output data a controller can receive from the build. |

#### Python `tdw` module

##### Frontend

| Document                                                     | Description                                                  |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| [`tdw` module](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/tdw.md) | Overview of the Python `tdw` module.                         |
| [Controller](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/controller.md) | Base class for all controllers.                              |
| [TDWUtils](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/tdw_utils.md) | Utility class.                                               |
| [AssetBundleCreator](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/asset_bundle_creator.md) | Covert 3D models into TDW-compatible asset bundles.          |
| [PyImpact](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/py_impact.md) | Generate impact sounds at runtime.                           |
| [DebugController](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/debug_controller.md) | Child class of `Controller` that has useful debug features.  |
| [KeyboardController](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/keyboard_controller.md) | Child class of `Controller` that can listen for keyboard input. |
| [FloorplanController](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/floorplan_controller.md) | Child class of `Controller` that creates an interior environment and populates it with objects. |
| [Librarian](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/librarian/librarian.md) | "Librarians" hold asset bundle metadata records.             |
| [FluidTypes](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/fluid_types.md) | Access different NVIDIA Flex fluid types.                    |
| [Object Init Data](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/object_init_data.md) | Wrapper classes for storing object initialization data.      |


##### Backend

| Document                                                     | Description                                                  |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| [Build](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/build.md) | Helper functions for downloading the build.                  |
| [PyPi](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/pypi.md) | Helper functions for checking the version of the `tdw` module on PyPi. |

# Audio and Video

| Document                                                     | Description                                       |
| ------------------------------------------------------------ | ------------------------------------------------- |
| [Impact Sounds](https://github.com/threedworld-mit/tdw/blob/master/Documentation/misc_frontend/impact_sounds.md) | Generate impact sounds at runtime using PyImpact. |
| [PyImpact](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/py_impact.md)                | PyImpact API.                                     |
| [Audio/Video Recording](https://github.com/threedworld-mit/tdw/blob/master/Documentation/misc_frontend/video.md) | Record audio, video, or audio+video.              |
| [Remote rendering](https://github.com/threedworld-mit/tdw/blob/master/Documentation/misc_frontend/xpra.md)      | How to render using xpra.                         |

# Avatars (Agents)

| Document                                                     | Description                                                  |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| [Observation Data](https://github.com/threedworld-mit/tdw/blob/master/Documentation/benchmark/observation_data.md) | Different means of determining what an agent is observing.   |
| [Avatar Movement](https://github.com/threedworld-mit/tdw/blob/master/Documentation/misc_frontend/avatar_movement.md) | Different techniques for moving agents.                      |
| [Sticky Mitten Avatar (low-level)](https://github.com/threedworld-mit/tdw/blob/master/Documentation/misc_frontend/sticky_mitten_avatar.md) | Comprehensive documentation for a physics-driven agent with "sticky mittens". |
| [Sticky Mitten Avatar (high-level)](https://github.com/alters-mit/sticky_mitten_avatar) | High-level API for the Sticky Mitten Avatar.                 |

# Benchmarks and Speed

| Document                                                     | Description                |
| ------------------------------------------------------------ | -------------------------- |
| [Benchmarks](https://github.com/threedworld-mit/tdw/blob/master/Documentation/benchmark/benchmark.md)           | Performance benchmarks.    |
| [Performance Optimizations](https://github.com/threedworld-mit/tdw/blob/master/Documentation/benchmark/performance_optimizations.md) | Increase simulation speed. |

# Examples

| Document                                                     | Description                                                |
| ------------------------------------------------------------ | ---------------------------------------------------------- |
| [Example Controllers](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/example_controllers.md) | Index of all example controllers in the repo.              |
| Use Cases (see below)                                        | The "use cases" section showcases "advanced" usage of TDW. |

# Misc.

| Document                                                     | Description                          |
| ------------------------------------------------------------ | ------------------------------------ |
| [VR](https://github.com/threedworld-mit/tdw/blob/master/Documentation/misc_frontend/vr.md) | VR in TDW.                           |
| [Humanoids](https://github.com/threedworld-mit/tdw/blob/master/Documentation/misc_frontend/humanoids.md) | Add "humanoids" and play animations. |

# Physics (PhysX and Flex)

| Document                                                     | Description                                |
| ------------------------------------------------------------ | ------------------------------------------ |
| [Physics](https://github.com/threedworld-mit/tdw/blob/master/Documentation/misc_frontend/physics.md) | Common physics problems and solutions.     |
| [NVIDIA Flex](https://github.com/threedworld-mit/tdw/blob/master/Documentation/misc_frontend/flex.md) | Add soft bodies, cloth, and fluids to TDW. |
| [FluidTypes](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/fluid_types.md) | Access different NVIDIA Flex fluid types.  |
| [Physics Determinism](https://github.com/threedworld-mit/tdw/blob/master/Documentation/benchmark/determinism.md) | Benchmark of PhysX physics determinism.    |
| [tdw_physics](https://github.com/alters-mit/sticky_mitten_avatar)     | Generate a physics dataset.                |
| [Sticky Mitten Avatar API](https://github.com/alters-mit/sticky_mitten_avatar) | High-level API for the Sticky Mitten Avatar. |
| [Rube Goldberg (demo)](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/use_cases/rube_goldberg.md) | Demo of complex physical interactions between objects, with PyImpact generation of impact sounds, set in a photorealistic scene.    |

# Releases

| Document | Description |
| --- | --- |
| [C# code](https://github.com/threedworld-mit/tdw/blob/master/Documentation/contributions/c_sharp_sources.md) | Access to C# backend source code |
| [Releases](https://github.com/threedworld-mit/tdw/blob/master/Documentation/misc_frontend/releases.md) | Release versioning in TDW.           |
| [Freezing your code](https://github.com/threedworld-mit/tdw/blob/master/Documentation/misc_frontend/freeze.md) | "Freeze" your controller into a compiled executable. |
| [v1.6 to v1.7](https://github.com/threedworld-mit/tdw/blob/master/Documentation/v1.6_to_v1.7.md) | How to upgrade from TDW v1.6 to TDW v1.7 |

# Remote Server

| Document                                                | Description                                                 |
| ------------------------------------------------------- | ----------------------------------------------------------- |
| [Docker](https://github.com/threedworld-mit/tdw/blob/master/Documentation/Docker/docker.md)                | Create a Docker container for TDW.                          |
| [Remote rendering](https://github.com/threedworld-mit/tdw/blob/master/Documentation/misc_frontend/xpra.md) | How to render using xpra.                                   |
| [BinaryManager](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/binary_manager.md) | Manage multiple instances of TDW builds on a remote server. |
| [bash scripts](https://github.com/threedworld-mit/tdw/blob/master/Documentation/misc_frontend/bash.md)     | Useful bash scripts for Linux.                              |

# Rendering and Photorealism

| Document                                                     | Description                                                  |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| [Asset Bundle Librarians](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/librarian/librarian.md) | Overview of what asset bundles are, how to add objects, scenes, materials, HDRI skyboxes, and humanoids, and how to access each asset bundle's metadata. |
| [Model Screenshotter](https://github.com/threedworld-mit/tdw/blob/master/Documentation/utility_applications/model_screenshotter.md) | Generate images of every model in TDW.                       |
| [Material Screenshotter](https://github.com/threedworld-mit/tdw/blob/master/Documentation/utility_applications/material_screenshotter.md) | Generate images of every material in TDW.                    |
| [Materials, textures, and colors](https://github.com/threedworld-mit/tdw/blob/master/Documentation/misc_frontend/materials_textures_colors.md) | Defines materials, textures, and colors.                     |
| [Depth of Field](https://github.com/threedworld-mit/tdw/blob/master/Documentation/misc_frontend/depth_of_field_and_image_blurriness.md) | Prevent blurry images and increase realism.                  |
| [Remote rendering](https://github.com/threedworld-mit/tdw/blob/master/Documentation/misc_frontend/xpra.md) | How to render using xpra.                                    |
| [Observation Data](https://github.com/threedworld-mit/tdw/blob/master/Documentation/benchmark/observation_data.md) | Different means of determining what an agent is observing.   |

# Scene Setup

| Document                                                     | Description                                                  |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| [Scene Setup](https://github.com/threedworld-mit/tdw/blob/master/Documentation/misc_frontend/scene_setup.md) | Overview of how to set up a scene.                           |
| [Asset Bundle Librarians](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/librarian/librarian.md) | Overview of what asset bundles are, how to add objects, scenes, materials, HDRI skyboxes, and humanoids, and how to access each asset bundle's metadata. |
| [Model Librarian](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/librarian/model_librarian.md) | Overview of how to add objects and access metadata.          |
| [Rotation](https://github.com/threedworld-mit/tdw/blob/master/Documentation/misc_frontend/rotation.md) | Different means of rotating objects and agents in a scene.   |
| [Scene Reset](https://github.com/threedworld-mit/tdw/blob/master/Documentation/misc_frontend/reset_scene.md) | How to reset a scene.                                        |
| [FloorplanController](Documentation/python/floorplan_controller.md) | Child class of `Controller` that creates an interior environment and populates it with objects. |

# TDW and 3D Objects

| Document                                                     | Description                                                  |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| [Model Librarian](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/librarian/model_librarian.md) | Overview of how to add objects and access metadata.          |
| [Model Screenshotter](https://github.com/threedworld-mit/tdw/blob/master/Documentation/utility_applications/model_screenshotter.md) | Generate images of every model in TDW.                       |
| [Non-free models](https://github.com/threedworld-mit/tdw/blob/master/Documentation/misc_frontend/models_full.md) | Access the TDW "full model library".                         |
| [Local 3D models](https://github.com/threedworld-mit/tdw/blob/master/Documentation/misc_frontend/add_local_object.md) | Add your own objects to TDW.                                 |
| [ShapeNet models](https://github.com/threedworld-mit/tdw/blob/master/Documentation/misc_frontend/shapenet.md)   | Convert ShapeNET models into TDW objects.                    |
| [Composite Objects](Documentation/composite_objects/composite_objects.md)<br>[Creating Composite Objects](https://github.com/threedworld-mit/tdw/blob/master/Documentation/composite_objects/creating_composite_objects.md) | Use and create "composite objects".                          |
| [AssetBundleCreator](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/asset_bundle_creator.md) | API for the `AssetBundleCreator` class (used to convert 3D models into TDW-compatible asset bundles). |
| [Rotation](https://github.com/threedworld-mit/tdw/blob/master/Documentation/misc_frontend/rotation.md)          | Different means of rotating objects and agents in a scene.   |

# Troubleshooting TDW

| Document                                                     | Description                                           |
| ------------------------------------------------------------ | ----------------------------------------------------- |
| [Debug TDW](https://github.com/threedworld-mit/tdw/blob/master/Documentation/misc_frontend/debug_tdw.md) | Several strategies for debugging errors in your code. |
| [DebugController](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/debug_controller.md) | API for the `DebugController` class.                  |
| [Depth of Field](https://github.com/threedworld-mit/tdw/blob/master/Documentation/misc_frontend/depth_of_field_and_image_blurriness.md) | Prevent blurry images and increase realism.           |
| [Performance Optimizations](https://github.com/threedworld-mit/tdw/blob/master/Documentation/benchmark/performance_optimizations.md) | Increase simulation speed.                            |
| [OS X](https://github.com/threedworld-mit/tdw/blob/master/Documentation/misc_frontend/osx.md) | Common OS X problems and solutions.                   |
| [Physics](https://github.com/threedworld-mit/tdw/blob/master/Documentation/misc_frontend/physics.md) | Common physics problems and solutions.                |

# Use Cases

| Use Case                                                     | Description                                |
| ------------------------------------------------------------ | ------------------------------------------ |
| [Image dataset](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/use_cases/single_object.md) | Generate 1.3M photorealistic images.       |
| [IntPhys (demo)](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/use_cases/int_phys.md) | Demo of how to simulate IntPhys in TDW.    |
| [Humanoid videos](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/use_cases/humanoid_video.md) | Generate a dataset of humanoid animations. |
| [tdw_sound20k](https://github.com/alters-mit/tdw_sound20k)   | Generate an audio dataset.                 |
| [tdw_physics](https://github.com/alters-mit/tdw_physics)     | Generate a physics dataset.                |
| [Rube Goldberg (demo)](https://github.com/threedworld-mit/tdw/blob/master/Documentation/python/use_cases/rube_goldberg.md) | Demo of complex physical interactions between objects, with PyImpact generation of impact sounds, set in a photorealistic scene.    |
| [Sticky Mitten Avatar API](https://github.com/alters-mit/sticky_mitten_avatar) | High-level API for the Sticky Mitten Avatar. |