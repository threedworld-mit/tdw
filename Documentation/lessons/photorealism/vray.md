##### Photorealism

# V-Ray Rendering

With the proper hardware, it is possible to render TDW simulations offline using the V-Ray renderer:

![](images/vray.jpg)

## Render time

**V-Ray rendering is not a real-time process.** Images are rendered when your simulation/trial ends using data that has been automatically cached on every communicate() call. At 1280x720 resolution and an RTX 4090 GPU, each image can be rendered in approximately 3-5 seconds.

## Requirements

### Hardware

The machine responsible for V-Ray rendering can be the same machine as the one running the controller and/or build, but it doesn't have to be. Feasibly, the controller, the build, and the V-Ray renderer can run on three separate machines.

These are the requirements for the machine running the V-Ray renderer:

- Windows 10
- [Chaos Vantage (the V-Ray renderer)](https://www.chaos.com/vantage)
- An NVidia RTX-type video card (RTX 3090 or newer)

### TDW

- **There must be exactly one camera in the your TDW scene.** If there is no camera or multiple cameras, the V-Ray rendering will fail.
- **Agents cannot be rendered in V-Ray.** This includes [robots](../robots/overview.md), [Replicants](../replicants/overview.md), and [Magnebots](https://github.com/alters-mit/magnebot). This limitation exists because it is too difficult to convert  body poses from Unity to the V-Ray renderer.
- **Only certain models and scenes can be rendered in V-Ray.** When you first run a controller with the `VRayExporter` add-on, it will download a list of all valid models and a list of all valid scenes. The lists are saved as `models.txt` and `scenes.txt` , respectively, and are located in `VRayExporter.VRAY_EXPORT_RESOURCES_PATH` (which by default is: `~/vr_export_resources/`). If your controller is trying to render models and scenes *not* on this list, you must replace them with valid models and scenes. The TDW team will add more scenes and models compatible with V-Ray rendering over time.

## Usage

Assuming you've met the software/hardware requirements, V-Ray rendering is as simple as adding a [`VRayExporter`](../../python/add_ons/vray_exporter.md) add-on to your controller. Call communicate() for each frame that you want to render. For example, if you want to render an object falling, call communicate() until the object stops moving. Then, call `launch_renderer(output_directory)` to begin rendering.

This is a minimal example:

```python
from tdw.controller import Controller
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.vray_exporter import VRayExporter


class VRayMinimal(Controller):
    """
    Create a typical TDW scene, then export using V-Ray add-on for maximum photorealism. Launch Vantage to render single output frame.
    """

    def __init__(self, output_path: str, render_host: str = "localhost", port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.render_host = render_host
        self.output_path = output_path

    def run(self):
        # Add a camera and enable export.
        camera = ThirdPersonCamera(avatar_id="a",
                                   position={"x": 3.0, "y": 1.25, "z": 1.0},
                                   look_at={"x": -1, "y": 0.5, "z": 0},
                                   field_of_view=50)
        exporter = VRayExporter(image_width=1280,
                                image_height=720,
                                scene_name="tdw_room",
                                animate=False)
        self.add_ons.extend([camera, exporter])
        # Load the scene.
        # Add the objects.
        # Adjust post-processing parameters to achieve a suitable depth of field and exposure.
        # Also adjust the ambient occlusion parameters for realistic shadowing in corners and under furniture objects.
        # Set shadow strength to near-full.
        commands = []
        commands.extend([{"$type": "set_render_quality",
                          "render_quality": 5},
                         {"$type": "set_aperture",
                          "aperture": 4.0},
                         {"$type": "set_focus_distance",
                          "focus_distance": 2.25},
                         {"$type": "set_post_exposure",
                          "post_exposure": 0.4},
                         {"$type": "set_ambient_occlusion_intensity",
                          "intensity": 0.175},
                         {"$type": "set_ambient_occlusion_thickness_modifier",
                          "thickness": 3.5},
                         {"$type": "set_shadow_strength",
                          "strength": 0.85},
                        self.get_add_scene(scene_name="tdw_room"),
                        self.get_add_object(model_name="coffee_table_glass_round",
                                            object_id=self.get_unique_id(),
                                            position={"x": -0.5, "y": 0, "z": 0},
                                            rotation={"x": 0, "y": 45, "z": 0}),
                         self.get_add_object(model_name="live_edge_coffee_table",
                                             object_id=self.get_unique_id(),
                                             position={"x": -3.25, "y": 0, "z": -0.47},
                                             rotation={"x": 0, "y": -90, "z": 0}),
                         self.get_add_object(model_name="bastone_floor_lamp",
                                             object_id=self.get_unique_id(),
                                             position={"x": -3.35, "y": 0, "z": 1},
                                             rotation={"x": 0, "y": 35, "z": 0}),
                         self.get_add_object(model_name="chair_eames_plastic_armchair",
                                             object_id=self.get_unique_id(),
                                             position={"x": -2.5, "y": 0, "z": -1.615},
                                             rotation={"x": 0, "y": 30, "z": 0}),
                         self.get_add_object(model_name="vase_05",
                                             object_id=self.get_unique_id(),
                                             position={"x": -0.5, "y": 0.3960, "z": 0},
                                             rotation={"x": 0, "y": 63.25, "z": 0}),
                         self.get_add_object(model_name="monster_beats_studio",
                                             object_id=self.get_unique_id(),
                                             position={"x": -0.3, "y": 0.428, "z": 0.1},
                                             rotation={"x": 90, "y": 20, "z": 0}),
                         self.get_add_object(model_name="zenblocks",
                                             object_id=self.get_unique_id(),
                                             position={"x": -3.25, "y": 0.3, "z": -0.517},
                                             rotation={"x": 0, "y": 70, "z": 0})])
        self.communicate(commands)
        # Launch Vantage render in headless mode; it will run to completion and automatically close.
        exporter.launch_renderer(output_directory="D:/VE2020_output/",
                                 render_host=self.render_host)


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--render_host", type=str, default="localhost", help="Host to render on.")
    parser.add_argument("--output_path", type=str, help="Folder location to output rendered images.")
    args = parser.parse_args()
    VRayMinimal(render_host=args.render_host, output_path=args.output_path).run()
```

## Launching the V-Ray renderer

`vray_exporter.launch_renderer(output_directory)` has the following optional parameters:

- `render_host` is the IP address of the rendering machine. By default, it's `"localhost"`.
- `port` is the port you will SSH with, assuming that the rendering machine is remote.
- `renderer_path` is the file path on the rendering machine of the Chaos Vantage executable.

## Backend notes

Certain models and scenes in TDW are "V-Ray compatible", meaning that there is a corresponding .vrscene file on TDW's S3 server.

At runtime, the [`VRayExporter`](../../python/add_ons/vray_exporter.md) gets the scene name via the `scene_name` constructor parameter, and a list of names of all models in the scene by querying the build. It then downloads the scene and model .vrscene files if they haven't already been downloaded. The download location is `VRayExporter.VRAY_EXPORT_RESOURCES_PATH`, which, like any other class variable, can be changed by the user.

The `VRayExporter` combines "static" data in the form of the pre-existing models and scene files described above, with "dynamic" simulation scene data output at runtime.  The initial scene .vrscene file, forms the base file for the scene to be rendered. The materials and lighting in these scene files have been optimized for V-Ray rendering from any camera position in the scene. In addition to the geometry, material and lighting data for the scene environment, all required render settings are contained in this file.  The model .vrscene files contain the geometry, material and transform data required to render that model in its canonical position and orientation.

V-Ray scenes store object transforms as matrices, rather than Unity's mix of vectors and quaternions. Accordingly, the `VRayExporter` add-on uses specialized matrix commands and output data. The add-on sends [`send_transform_matrices`](../../api/command_api.md#send_transform_matrices), [`send_avatar_transform_matrices`](../../api/command_api.md#send_avatar_transform_matrices), and [`send_field_of_view`](../../api/command_api.md#send_field_of_view). The add-on receives [`TransformMatrices`](../../api/output_data.md#TransformMatrices), [`AvatarTransformMatrices`](../../api/output_data.md#AvatarTransformMatrices), and [`FieldOfView`](../../api/output_data.md#FieldOfView).

On every communicate() call, the `VRayExporter` reads TDW output data, converts it into V-Ray scene data. The scene that will actually be rendered is a copy of the initial scene .vrscene file that includes camera and model transform data.

When the controller calls `vray_exporter.launch_renderer()`, this "final copy" of the scene file is fed into the renderer to create either a single frame or a sequence of frames.

***

**This is the last document in the "Photorealism" tutorial.**

[Return to the README](../../../README.md)

***

Example Controllers:

- [vray_minimal.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/photorealism/vray_minimal.py) A minimal `VRayExporter` example.
- [vray_dynamic_objects.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/photorealism/vray_dynamic_objects.py)  Create a typical TDW scene. Apply a force to the chair, then export using V-Ray add-on for maximum photorealism.
- [vray_dynamic_camera.py](https://github.com/threedworld-mit/tdw/blob/master/Python/example_controllers/photorealism/vray_dynamic_camera.py)  Create a typical TDW scene, randomize a sequence of camera positions and aimpoints, then export using V-Ray add-on for maximum photorealism.

Python API:

- [`VRayExporter`](../../python/add_ons/vray_exporter.md)

Command API:

- [`send_transform_matrices`](../../api/command_api.md#send_transform_matrices)
- [`send_avatar_transform_matrices`](../../api/command_api.md#send_avatar_transform_matrices)
-  [`send_field_of_view`](../../api/command_api.md#send_field_of_view)

Output Data:

- [`TransformMatrices`](../../api/output_data.md#TransformMatrices)
- [`AvatarTransformMatrices`](../../api/output_data.md#AvatarTransformMatrices)
- [`FieldOfView`](../../api/output_data.md#FieldOfView)