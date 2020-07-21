from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.output_data import Images


"""
Capture a _depth image and calculate the depth values of each pixel.
"""


class DepthShader(Controller):
    def run(self):
        self.start()
        # Create an empty room.
        self.communicate(TDWUtils.create_empty_room(12, 12))

        # Create the avatar.
        self.communicate(TDWUtils.create_avatar(position={"x": 0, "y": 3, "z": -4},
                                                look_at=TDWUtils.VECTOR3_ZERO))

        # Set the pass mask to _depth only.
        # Get an image.
        resp = self.communicate([self.get_add_object("rh10", object_id=0),
                                 {"$type": "set_pass_masks",
                                  "avatar_id": "a",
                                  "pass_masks": ["_depth"]},
                                 {"$type": "send_images",
                                  "frequency": "once"}])
        images = Images(resp[0])
        # Get the depth values of each pixel.
        depth = TDWUtils.get_depth_values(images.get_image(0))
        print(depth)


if __name__ == "__main__":
    DepthShader().run()
