from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils


"""
Generate a proc-gen room from this image: ![](../../Python/example_controllers/room.png)
Each pixel corresponds to a grid point.
For more information, see TDWUtils documentation.
"""


class ProcGenRoomFromImage(Controller):
    def run(self):
        self.start()

        # Create the room from an image.
        self.communicate(TDWUtils.create_room_from_image("room.png"))
        self.communicate({"$type": "set_post_process",
                          "value": False})
        self.communicate(TDWUtils.create_avatar(position={"x": 0, "y": 40, "z": 0},
                                                look_at=TDWUtils.VECTOR3_ZERO))


if __name__ == "__main__":
    ProcGenRoomFromImage().run()
