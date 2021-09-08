from pathlib import Path
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Images


"""
Create one image per pass of a scene.
"""


class PassMasks(Controller):
    def run(self):
        # Create the scene.
        # Set image encoding globals.
        self.start()
        commands = [TDWUtils.create_empty_room(12, 12),
                    {"$type": "set_screen_size",
                     "width": 128,
                     "height": 128},
                    {"$type": "set_img_pass_encoding",
                     "value": False}]
        # Create the avatar.
        commands.extend(TDWUtils.create_avatar(position={"x": 2.478, "y": 1.602, "z": 1.412},
                                               look_at=TDWUtils.VECTOR3_ZERO,
                                               avatar_id="a"))
        # Enable all pass masks. Request an image for this frame only.
        commands.extend([{"$type": "set_pass_masks",
                          "pass_masks": ["_img", "_id", "_category", "_mask", "_depth", "_normals", "_flow",
                                         "_depth_simple", "_albedo"],
                          "avatar_id": "a"},
                         {"$type": "send_images",
                          "ids": ["a"],
                          "frequency": "once"}])
        # Add objects.
        commands.append(self.get_add_object("small_table_green_marble",
                                            position=TDWUtils.VECTOR3_ZERO,
                                            rotation=TDWUtils.VECTOR3_ZERO,
                                            object_id=0))
        commands.append(self.get_add_object("rh10",
                                            position={"x": 0.7, "y": 0, "z": 0.4},
                                            rotation={"x": 0, "y": 30, "z": 0},
                                            object_id=1))
        commands.append(self.get_add_object("jug01",
                                            position={"x": -0.3, "y": 0.9, "z": 0.2},
                                            rotation=TDWUtils.VECTOR3_ZERO,
                                            object_id=3))
        commands.append(self.get_add_object("jug05",
                                            position={"x": 0.3, "y": 0.9, "z": -0.2},
                                            rotation=TDWUtils.VECTOR3_ZERO,
                                            object_id=4))
        # Send the commands.
        resp = self.communicate(commands)
        # Save the images.
        for r in resp[:-1]:
            r_id = OutputData.get_data_type_id(r)
            if r_id == "imag":
                # Save the images.
                TDWUtils.save_images(output_directory="dist", images=Images(r), filename="0")
                print(f"Images saved to: {Path('dist').resolve()}")
        # Stop the build.
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    PassMasks(launch_build=False).run()
