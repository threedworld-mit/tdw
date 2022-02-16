from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.keyboard import Keyboard
from tdw.add_ons.embodied_avatar import EmbodiedAvatar


class KeyboardControls(Controller):
    """
    Use arrow keys to move an avatar.
    """

    FORCE: float = 80
    TORQUE: float = 160

    def __init__(self, port: int = 1071):
        super().__init__(port=port)
        self.done = False

        # Add a `Keyboard` add-on to the controller to listen for keyboard input.
        keyboard: Keyboard = Keyboard()
        keyboard.listen(key="UpArrow", function=self.move_forward, events=["press", "hold"])
        keyboard.listen(key="DownArrow", function=self.move_backward, events=["press", "hold"])
        keyboard.listen(key="RightArrow", function=self.turn_right, events=["press", "hold"])
        keyboard.listen(key="LeftArrow", function=self.turn_left, events=["press", "hold"])
        keyboard.listen(key="Escape", function=self.quit, events=["press"])
        self.add_ons.append(keyboard)
        # Add an embodied avatar.
        self.embodied_avatar: EmbodiedAvatar = EmbodiedAvatar()
        self.embodied_avatar.set_drag(drag=10, angular_drag=20)
        self.add_ons.append(self.embodied_avatar)

    def move_forward(self) -> None:
        """
        Move forward.
        """

        self.embodied_avatar.apply_force(KeyboardControls.FORCE)

    def move_backward(self) -> None:
        """
        Move backward.
        """

        self.embodied_avatar.apply_force(-KeyboardControls.FORCE)

    def turn_right(self) -> None:
        """
        Turn clockwise.
        """

        self.embodied_avatar.apply_torque(KeyboardControls.TORQUE)

    def turn_left(self) -> None:
        """
        Turn counterclockwise.
        """

        self.embodied_avatar.apply_torque(-KeyboardControls.TORQUE)

    def quit(self) -> None:
        """
        End the simulation.
        """

        self.done = True

    def run(self):
        print("W, up-arrow = Move forward")
        print("S, down-arrow = Move backward")
        print("A, left-arrow = Turn counterclockwise")
        print("D, right-arrow = Turn clockwise")
        print("Esc = Quit")

        # Create the room. Set the room's floor material.
        self.communicate([TDWUtils.create_empty_room(12, 12),
                          self.get_add_material("parquet_alternating_orange", library="materials_high.json"),
                         {"$type": "set_proc_gen_floor_material",
                          "name": "parquet_alternating_orange"},
                         {"$type": "set_proc_gen_floor_texture_scale",
                          "scale": {"x": 8, "y": 8}}])
        while not self.done:
            self.communicate([])
        self.communicate({"$type": "terminate"})


if __name__ == "__main__":
    KeyboardControls().run()
