from tdw.controller import Controller
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH


class Photoreal(Controller):
    """
    Create a photorealistic scene, focusing on post-processing and other effects.
    The "archviz_house" environment is used due to its maximal photorealistic lighting.
    """

    def run(self):
        # Add a camera and enable image capture.
        camera = ThirdPersonCamera(avatar_id="a",
                                   position={"x": -10.48, "y": 1.81, "z": -6.583},
                                   look_at={"x": -12.873, "y": 1.85, "z": -5.75},
                                   field_of_view=68)
        path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("photoreal")
        print(f"Image will be saved to: {path}")
        capture = ImageCapture(avatar_ids=["a"], path=path)
        self.add_ons.extend([camera, capture])

        # Set the resolution to 1080p.
        # Set render quality to maximum.
        # Load the scene.
        # Add the objects.
        # Adjust post-processing parameters to achieve a suitable depth of field and exposure.
        # Also adjust the ambient occlusion parameters for realistic shadowing in corners and under furniture objects.
        # Set shadow strength to full.
        # Immediately end the simulation.
        self.communicate([{"$type": "set_screen_size",
                           "width": 1920,
                           "height": 1080},
                          {"$type": "set_render_quality",
                           "render_quality": 5},
                          self.get_add_scene(scene_name="archviz_house"),
                          self.get_add_object(model_name="live_edge_coffee_table",
                                              object_id=self.get_unique_id(),
                                              position={"x": -12.8, "y": 0.96, "z": -5.47},
                                              rotation={"x": 0, "y": -90, "z": 0}),
                          self.get_add_object(model_name="chista_slice_of_teak_table",
                                              object_id=self.get_unique_id(),
                                              position={"x": -14.394, "y": 0.96, "z": -7.06},
                                              rotation={"x": 0, "y": 21.35, "z": 0}),
                          self.get_add_object(model_name="chair_billiani_doll",
                                              object_id=self.get_unique_id(),
                                              position={"x": -15.15, "y": 0.96, "z": -6.8},
                                              rotation={"x": 0, "y": 63.25, "z": 0}),
                          self.get_add_object(model_name="zenblocks",
                                              object_id=self.get_unique_id(),
                                              position={"x": -12.7, "y": 1.288, "z": -5.55},
                                              rotation={"x": 0, "y": 90, "z": 0}),
                          {"$type": "set_aperture",
                           "aperture": 1.6},
                          {"$type": "set_focus_distance",
                           "focus_distance": 2.25},
                          {"$type": "set_post_exposure",
                           "post_exposure": 0.4},
                          {"$type": "set_ambient_occlusion_intensity",
                           "intensity": 0.175},
                          {"$type": "set_ambient_occlusion_thickness_modifier",
                           "thickness": 3.5},
                          {"$type": "set_shadow_strength",
                           "strength": 1.0},
                          {"$type": "terminate"}])


if __name__ == "__main__":
    Photoreal().run()
