from tdw.keyboard_controller import KeyboardController
from tdw.tdw_utils import TDWUtils


"""
Use WASD or arrow keys to move an avatar.
"""


class KeyboardControls(KeyboardController):
    def __init__(self, port: int = 1071):
        super().__init__(port=port)
        self.done = False
        self.avatar_id = "a"

    def move(self, direction: int, force: float = 80) -> dict:
        """
        :param direction: The direction of movement.
        :param force: The force of the movement.

        :return: A `move_avatar_forward_by` command.
        """

        return {"$type": "move_avatar_forward_by",
                "magnitude": force * direction,
                "avatar_id": self.avatar_id}

    def turn(self, direction: int, torque: float = 100):
        """
        :param direction: The direction of the turn.
        :param torque: The torque force of the turn.

        :return: A `turn_avatar_by` command.
        """

        return {"$type": "turn_avatar_by",
                "torque": torque * direction,
                "avatar_id": self.avatar_id}

    def stop(self) -> None:
        """
        End the simulation.
        """

        self.communicate({"$type": "terminate"})
        self.done = True

    def run(self):
        print("W, up-arrow = Move forward")
        print("S, down-arrow = Move backward")
        print("A, left-arrow = Turn counterclockwise")
        print("D, right-arrow = Turn clockwise")
        print("Esc = Quit")

        self.start()
        # Create the room.
        commands = [TDWUtils.create_empty_room(12, 12)]
        # Create the avatar.
        commands.extend(TDWUtils.create_avatar(avatar_type="A_Img_Caps", avatar_id=self.avatar_id))
        # 1. Set high drag values so it doesn't feel like the avatar is sliding on ice.
        # 2. Set the room's floor material.
        # 3. Request keyboard input.
        commands.extend([{"$type": "set_avatar_drag",
                          "drag": 10,
                          "angular_drag": 20,
                          "avatar_id": self.avatar_id},
                         self.get_add_material("parquet_alternating_orange", library="materials_high.json"),
                         {"$type": "set_proc_gen_floor_material",
                          "name": "parquet_alternating_orange"},
                         {"$type": "set_proc_gen_floor_texture_scale",
                          "scale": {"x": 8, "y": 8}}])
        self.communicate(commands)

        self.listen(key="W", commands=self.move(direction=1), events=["press", "hold"])
        self.listen(key="UpArrow", commands=self.move(direction=1), events=["press", "hold"])
        self.listen(key="S", commands=self.move(direction=-1), events=["press", "hold"])
        self.listen(key="DownArrow", commands=self.move(direction=-1), events=["press", "hold"])
        self.listen(key="A", commands=self.turn(direction=-1), events=["press", "hold"])
        self.listen(key="LeftArrow", commands=self.turn(direction=-1), events=["press", "hold"])
        self.listen(key="D", commands=self.turn(direction=1), events=["press", "hold"])
        self.listen(key="RightArrow", commands=self.turn(direction=1), events=["press", "hold"])
        self.listen(key="Escape", function=self.stop, events=["press"])

        while not self.done:
            self.communicate([])


if __name__ == "__main__":
    KeyboardControls().run()
