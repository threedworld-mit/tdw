from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from tdw.add_ons.image_capture import ImageCapture


class ProcGenRoomFromImage(Controller):
    """
    Generate a proc-gen room from this image: ![](../../Python/example_controllers/room.png)
    Each pixel corresponds to a grid point.
    For more information, see TDWUtils documentation.
    """

    def run(self) -> None:
        commands = TDWUtils.create_room_from_image("room.png")
        commands.append({"$type": "set_post_process",
                         "value": False})
        commands.extend(TDWUtils.create_avatar(position={"x": 0, "y": 40, "z": 0},
                                               look_at=TDWUtils.VECTOR3_ZERO,
                                               avatar_id="a"))
        path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("proc_gen_room_from_image")
        print(f"Images will be saved to: {path}")
        capture = ImageCapture(avatar_ids=["a"], path=path)
        self.add_ons.append(capture)
        self.communicate(commands)
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    ProcGenRoomFromImage().run()
