from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.vive_pro_eye import ViveProEye
from tdw.vr_data.vive_button import ViveButton


class ViveProEyeCompositeObject(Controller):
    """
    Manipulate a composite object.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.communicate(TDWUtils.create_empty_room(12, 12))
        self.done = False
        self.vr = ViveProEye()
        self.vr.listen_to_button(button=ViveButton.left_menu, function=self.quit)
        self.add_ons.append(self.vr)

    def run(self) -> None:
        self.communicate(Controller.get_add_physics_object(model_name="vm_v5_072_composite",
                                                           object_id=Controller.get_unique_id(),
                                                           position={"x": 0, "y": 0.7, "z": 0.9},
                                                           kinematic=True))
        while not self.done:
            self.communicate([])
        self.communicate({"$type": "terminate"})

    def quit(self):
        self.done = True


if __name__ == "__main__":
    c = ViveProEyeCompositeObject()
    c.run()