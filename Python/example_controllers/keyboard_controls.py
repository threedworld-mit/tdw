from tdw.keyboard_controller import KeyboardController
from tdw.tdw_utils import TDWUtils


"""
Use WASD or arrow keys to move an avatar.
"""


class KeyboardControls(KeyboardController):
    def __init__(self, port: int = 1071):
        super().__init__(port=port)
        self.done = False

    def run(self, force=80, torque=100):
        """
        :param force: The force magnitude used to move the avatar.
        :param torque: The torque magnitude to turn the avatar by.
        """

        print("W, up-arrow = Move forward")
        print("S, down-arrow = Move backward")
        print("A, left-arrow = Turn counterclockwise")
        print("D, right-arrow = Turn clockwise")
        print("Esc = Quit")

        # Listen for keyboard input for movement.
        self.listen("w", commands={"$type": "move_avatar_forward_by",
                                   "magnitude": force,
                                   "avatar_id": "a"})
        self.listen("up", commands={"$type": "move_avatar_forward_by",
                                    "magnitude": force,
                                    "avatar_id": "a"})
        self.listen("s", commands={"$type": "move_avatar_forward_by",
                                   "magnitude": -force,
                                   "avatar_id": "a"})
        self.listen("down", commands={"$type": "move_avatar_forward_by",
                                      "magnitude": -force,
                                      "avatar_id": "a"})
        self.listen("d", commands={"$type": "turn_avatar_by",
                                   "torque": torque,
                                   "avatar_id": "a"})
        self.listen("right", commands={"$type": "turn_avatar_by",
                                       "torque": torque,
                                       "avatar_id": "a"})
        self.listen("a", commands={"$type": "turn_avatar_by",
                                   "torque": -torque,
                                   "avatar_id": "a"})
        self.listen("left", commands={"$type": "turn_avatar_by",
                                      "torque": -torque,
                                      "avatar_id": "a"})
        # Listen for keyboard input to quit.
        self.listen("esc", function=self.stop)

        self.start()
        # Create the room.
        commands = [TDWUtils.create_empty_room(12, 12)]
        # Create the avatar.
        commands.extend(TDWUtils.create_avatar(avatar_type="A_Img_Caps", avatar_id="a"))
        # 1. Set high drag values so it doesn't feel like the avatar is sliding on ice.
        # 2. Set the room's floor material.
        commands.extend([{"$type": "set_avatar_drag",
                          "drag": 10,
                          "angular_drag": 20,
                          "avatar_id": "a"},
                         self.get_add_material("parquet_alternating_orange", library="materials_high.json"),
                         {"$type": "set_proc_gen_floor_material",
                          "name": "parquet_alternating_orange"},
                         {"$type": "set_proc_gen_floor_texture_scale",
                          "scale": {"x": 8, "y": 8}}])
        self.communicate(commands)
        while not self.done:
            # Listen for keyboard input to add other commands.
            self.communicate([])
        self.communicate({"$type": "terminate"})

    def stop(self):
        """
        Stop the controller and the build.
        """

        self.done = True


if __name__ == "__main__":
    KeyboardControls().run()
