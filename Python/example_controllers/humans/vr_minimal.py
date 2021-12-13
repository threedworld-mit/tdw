from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.keyboard import Keyboard


class VirtualReality(Controller):
    """
    Minimal VR example. Press Escape to quit.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.done = False

        keyboard = Keyboard()
        self.add_ons.append(keyboard)
        keyboard.listen(key="Escape", function=self.quit)

    def run(self) -> None:
        object_id = self.get_unique_id()
        self.communicate([TDWUtils.create_empty_room(12, 12),
                          {"$type": "create_vr_rig"},
                          self.get_add_object(model_name="rh10",
                                              object_id=object_id,
                                              position={"x": 0, "y": 0, "z": 1.2}),
                          {"$type": "set_graspable",
                           "id": object_id}])
        while not self.done:
            self.communicate([])
        self.communicate({"$type": "terminate"})

    def quit(self):
        self.done = True


if __name__ == "__main__":
    c = VirtualReality()
    c.run()
