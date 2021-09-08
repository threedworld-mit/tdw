from base64 import b64encode
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils


"""
Add a painting to the scene_data.
"""


class Paintings(Controller):
    def run(self):
        # Open the image file.
        with open("DT4897.jpg", "rb") as f:
            image = b64encode(f.read()).decode("utf-8")

        # The expected dimensions of the painting.
        dimensions = {"x": 479, "y": 332}

        self.start()
        # Create an empty room.
        self.communicate(TDWUtils.create_empty_room(8, 8))

        # Create a painting.
        # Apply the texture.
        painting_id = self.get_unique_id()
        painting_position = {"x": 1, "y": 2, "z": 3}
        self.communicate([{"$type": "create_painting",
                           "position": painting_position,
                           "size": {"x": 5, "y": 3},
                           "euler_angles": {"x": 0, "y": 30, "z": 0},
                           "id": painting_id},
                          {"$type": "set_painting_texture",
                           "id": painting_id,
                           "dimensions": dimensions,
                           "image": image}
                          ])

        # Create the avatar.
        self.communicate(TDWUtils.create_avatar(position={"x": 0, "y": 5, "z": 0},
                                                look_at=painting_position))


if __name__ == "__main__":
    Paintings().run()
