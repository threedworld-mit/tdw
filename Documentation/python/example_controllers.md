# Example Controllers

Each TDW release includes many example controllers. They can be found in: `<root>/Python/example_controllers/`

| Controller | Description |
| --- | --- |
| `add_materials.py` | Different ways to add the same material to a scene. |
| `add_objects.py` | Different ways to add the same object to a scene. |
| `animate_humanoid.py` | Create a humanoid and play some animations. |
| `audio.py` | - Create a scene with a reverb space and audio sensor.<br>- Test how object positions can affect reverb. |
| `avatar_drag.py` | Set the avatar's drag values to control its speed while in mid-air. |
| `avatar_movement.py` | A basic example of how to move a physics-enabled (non-kinematic) avatar. |
| `cloth_drape.py` | Using NVIDIA Flex, drape a cloth over an object. |
| `collisions.py` | Receive collision output data and read it as a `Collisions` object. |
| `collisions_and_friction.py` | - Listen for collisions between objects.<br>- Adjust the friction values of objects. |
| `composite_object.py` | Create a composite object from a local asset bundle.<br>Test that the object loaded correctly.<br>Apply sub-object commands to the sub-objects. |
| `debug.py` | Create a debug controller. After running a simple physics simulation, play back all of the commands. |
| `depth_shader.py` | Capture a _depth image and calculate the depth values of each pixel. |
| `directional_light.py` | Rotate the directional light in the scene. |
| `flex_cloth_fixed_particle.py` | Create a Flex cloth object and "fix" one of its corners in mid-air. |
| `flex_fluid_object.py` | Create a fluid "container" with the NVIDIA Flex physics engine. Run several trials, dropping ball objects of increasing mass into the fluid. |
| `flex_fluid_source.py` | Create a Flex FluidSource, or "hose pipe", simulation of a fluid stream. |
| `flex_soft_body.py` | Create a soft-body object with the NVIDIA Flex physics engine. |
| `forcefield.py` | Simulate a "forcefield" that objects will bounce off of. |
| `getting_started.py` | 1. Add a table and place an object on the table.<br>2. Add a camera and receive an image. |
| `hdri.py` | Create an object and avatar and capture images of the scene, rotating the HDRI skybox by 15 degrees<br>for each image. |
| `impact_sounds.py` | - Listen for collisions between objects.<br>- Generate an impact sound with py_impact upon impact and play the sound in the build. |
| `keyboard_controls.py` | Use WASD or arrow keys to move an avatar. |
| `local_object.py` | Create a local asset bundle and load it into TDW.<br><br>See `Documentation/misc_frontend/add_local_object.md` for how to run the Asset Bundle Creator. |
| `magnebot.py` | Add a Magnebot and move it around the scene. |
| `minimal.py` | A minimal example of how to connect to the build and receive data. |
| `minimal_audio_dataset.py` | A minimal example of how to generate audio datasets. |
| `minimal_remote.py` | A minimal example of how to use the launch binaries daemon to<br>start and connect to a build on a remote node. Note: the remote<br>must be running launch_binaries.py. |
| `nav_mesh.py` | - Create a NavMeshAvatar and a simple procedurally-generated room.<br>- Tell the avatar to navigate to different destinations. |
| `objects_and_images.py` | Create a few objects, and avatar, and capture images of the objects. |
| `occlusion.py` | Use occlusion data to measure to what extent objects in the scene are occluded. |
| `paintings.py` | Add a painting to the scene. |
| `panorama.py` | Capture a series of images around a model to form a 360-degree panorama. |
| `pass_masks.py` | Create one image per pass of a scene. |
| `perlin_noise_terrain.py` | Generate Perlin noise terrain and roll a ball down the terrain. |
| `photoreal.py` | Create a photorealistic scene, focusing on post-processing and other effects.<br>The "archviz_house" environment is used due to its maximal photorealistic lighting. |
| `proc_gen_interior_design.py` | Procedurally furnish a room with basic relational semantic rules. |
| `proc_gen_room.py` | - Procedurally generate rooms with different layouts.<br>- Create a ceiling and delete a portion of it.<br>- Set the floor and wall materials. |
| `proc_gen_room_from_image.py` | Generate a proc-gen room from this image: ![](../../Python/example_controllers/room.png)<br>Each pixel corresponds to a grid point.<br>For more information, see TDWUtils documentation. |
| `records.py` | - Use Librarian objects to search for model and material records.<br>- Set the visual material(s) of an object.<br>For documentation, see `Documentation/python/librarian.md`. |
| `robot_arm.py` | Add a robot to TDW and bend its arm. |
| `robot_camera.py` | Add a camera to a Magnebot. |
| `visual_material_quality.py` | Adjust the render quality of visual materials. |
| `vr.py` | 1. Create an Oculus VR rig.<br>2. Add a few objects to the scene that can be picked up, moved, put down, etc. |
| `vr_flex.py` | 1. Create an Oculus VR rig.<br>2. Create Flex-enabled objects.<br>3. Receive Flex particle data. |
| `vr_observed_objects.py` | Create a VR rig and gather observed object data by attaching an avatar and using IdPassSegmentationColors output data. |
