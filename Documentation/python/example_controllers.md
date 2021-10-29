# Example Controllers

Each TDW release includes many example controllers. They can be found in: `<root>/Python/example_controllers/`

| Controller | Description |
| --- | --- |
| `add_ons.py` | Add multiple add-ons to a controller. |
| `animate_humanoid.py` | Create a humanoid and play some animations. |
| `avatar_drag.py` | Set the avatar's drag values to control its speed while in mid-air. |
| `avatar_movement.py` | A basic example of how to move a physics-enabled (non-kinematic) avatar. |
| `cloth_drape.py` | Using NVIDIA Flex, drape a cloth over an object. |
| `debug.py` | Create a controller with a `Debug` module.<br>After running a simple physics simulation, play back all of the commands. |
| `directional_light.py` | Rotate the directional light in the scene. |
| `flex_cloth_fixed_particle.py` | Create a Flex cloth object and "fix" one of its corners in mid-air. |
| `flex_fluid_object.py` | Create a fluid "container" with the NVIDIA Flex physics engine. Run several trials, dropping ball objects of increasing mass into the fluid. |
| `flex_fluid_source.py` | Create a Flex FluidSource, or "hose pipe", simulation of a fluid stream. |
| `flex_soft_body.py` | Create a soft-body object with the NVIDIA Flex physics engine. |
| `hdri.py` | Create an object and avatar and capture images of the scene, rotating the HDRI skybox by 15 degrees<br>for each image. |
| `keyboard_controls.py` | Use WASD or arrow keys to move an avatar. |
| `lights_output_data.py` | Load a streamed scene and received Lights output data. |
| `minimal_remote.py` | A minimal example of how to use the launch binaries daemon to<br>start and connect to a build on a remote node. Note: the remote<br>must be running launch_binaries.py. |
| `nav_mesh.py` | - Create a NavMeshAvatar and a simple procedurally-generated room.<br>- Tell the avatar to navigate to different destinations. |
| `occupancy_mapper.py` | Generate occupancy maps in a scene populated by objects.<br>For more information, [read this](add_ons/occupancy_map.md). |
| `paintings.py` | Add a painting to the scene. |
| `perlin_noise_terrain.py` | Generate Perlin noise terrain and roll a ball down the terrain. |
| `photoreal.py` | Create a photorealistic scene, focusing on post-processing and other effects.<br>The "archviz_house" environment is used due to its maximal photorealistic lighting. |
| `proc_gen_room.py` | - Procedurally generate rooms with different layouts.<br>- Create a ceiling and delete a portion of it.<br>- Set the floor and wall materials. |
| `records.py` | - Use Librarian objects to search for model and material records.<br>- Set the visual material(s) of an object.<br>For documentation, see `Documentation/python/librarian.md`. |
| `smpl_humanoid.py` | Add a [SMPL humanoid](https://smpl.is.tue.mpg.de/en) to the scene. Set its body parameters and play an animation. |
| `vr.py` | 1. Create an Oculus VR rig.<br>2. Add a few objects to the scene that can be picked up, moved, put down, etc. |
| `vr_flex.py` | 1. Create an Oculus VR rig.<br>2. Create Flex-enabled objects.<br>3. Receive Flex particle data. |
| `vr_observed_objects.py` | Create a VR rig and gather observed object data by attaching an avatar and using IdPassSegmentationColors output data. |
