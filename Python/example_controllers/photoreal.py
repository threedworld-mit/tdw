from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import Images
from pathlib import Path


"""
Create a photorealistic scene_data, focusing on post-processing and other effects.
The "archviz_house" environment is used due to its maximal photorealistic lighting.
"""


class Photoreal(Controller):
    def run(self):
        # Create the output directory.
        output_directory = Path("photoreal")
        if not output_directory.exists():
            output_directory.mkdir()

        # Load the streamed scene_data.
        self.load_streamed_scene(scene="archviz_house")

        # Add the objects.
        self.add_object("live_edge_coffee_table",
                        position={"x": -12.8, "y": 0.96, "z": -5.47},
                        rotation={"x": 0, "y": -90, "z": 0})
        self.add_object("chista_slice_of_teak_table",
                        position={"x": -14.394, "y": 0.96, "z": -7.06},
                        rotation={"x": 0, "y": 21.35, "z": 0})
        self.add_object("chair_billiani_doll",
                        position={"x": -15.15, "y": 0.96, "z": -6.8},
                        rotation={"x": 0, "y": 63.25, "z": 0})
        self.add_object("zenblocks",
                        position={"x": -12.7, "y": 1.288, "z": -5.55},
                        rotation={"x": 0, "y": 90, "z": 0})

        # Organize all setup commands into a single list. 
        # We want a high-quality result, so set 1080P screen resolution / aspect ratio
        # and maximum render quality.
        init_setup_commands = [{"$type": "set_screen_size", 
                                "width": 1920, 
                                "height": 1080},
                               {"$type": "set_render_quality",
                                "render_quality": 5}]

        # Create the avatar and adjust its field of view for a wider camera angle.
        init_setup_commands.extend([{"$type": "create_avatar", 
                                     "type": "A_Img_Caps_Kinematic", 
                                     "id": "a"},
                                    {"$type": "set_field_of_view", 
                                     "field_of_view": 68.0, 
                                     "avatar_id": "a"}])

        # Adjust post-processing parameters to achieve a suitable depth of field and exposure, and disable vignette.
        # Also adjust the ambient occlusion parameters for realistic shadowing in corners and under furniture objects.
        init_setup_commands.extend([{"$type": "set_aperture",
                                     "aperture": 1.6},
                                    {"$type": "set_focus_distance",
                                     "focus_distance": 2.25},
                                    {"$type": "set_post_exposure",
                                     "post_exposure": 0.4},
                                    {"$type": "set_vignette",
                                     "enabled": False},
                                    {"$type": "set_ambient_occlusion_intensity",
                                     "intensity": 0.175},
                                    {"$type": "set_ambient_occlusion_thickness_modifier",
                                     "thickness": 3.5}])

        # Set shadow strength to full.
        init_setup_commands.append({"$type": 
                                    "set_shadow_strength", 
                                    "strength": 1.0})

        # Execute the setup commands.
        self.communicate(init_setup_commands)

        # Teleport the avatar to the desired position.
        # Set the pass masks to _img.
        # Enable image capture.
        resp = self.communicate([{"$type": "teleport_avatar_to",
                                  "avatar_id": "a",
                                  "position": {"x": -10.48, "y": 1.81, "z": -6.583}},
                                 {"$type": "set_pass_masks",
                                  "avatar_id": "a",
                                  "pass_masks": ["_img"]},
                                 {"$type": "send_images",
                                  "frequency": "always"},
                                 {"$type": "look_at_position",
                                  "position": {"x": -12.873, "y": 1.85, "z": -5.75},
                                  "avatar_id": "a"}])

        # Parse the output image data.
        images = Images(resp[0])
        # Save the image.
        TDWUtils.save_images(images, TDWUtils.zero_padding(0), output_directory=str(output_directory.resolve()))
        print(f"Image saved to: {output_directory.resolve()}")


if __name__ == "__main__":
    Photoreal().run()
