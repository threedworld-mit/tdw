from tdw.controller import Controller
from tdw.add_ons.keyboard import Keyboard


class KeyboardExample(Controller):
    """
    Minimal keyboard example. Press Escape to quit.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.done = False
        keyboard = Keyboard()
        self.add_ons.append(keyboard)
        keyboard.listen(key="Escape", function=self.quit)

    def quit(self):
        self.done = True


if __name__ == "__main__":
    c = KeyboardExample()
    while not c.done:
        c.communicate([])
    c.communicate({"$type": "terminate"})
