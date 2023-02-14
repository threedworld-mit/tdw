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
                                output_directory=self.output_path,
                                animate=False,
                                render_host=self.render_host)
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
        exporter.launch_renderer()


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--render_host", type=str, default="localhost", help="Host to render on.")
    parser.add_argument("--output_path", type=str, help="Folder location to output rendered images.")
    args = parser.parse_args()
    VRayMinimal(render_host=args.render_host, output_path=args.output_path).run()
