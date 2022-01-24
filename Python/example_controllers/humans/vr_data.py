from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.keyboard import Keyboard
from tdw.add_ons.vr import VR
from tdw.vr_data.rig_type import RigType


class VRData(Controller):
    """
    Add several objects to the scene and parse VR output data.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.done = False

        keyboard = Keyboard()
        self.vr = VR(rig_type=RigType.oculus_touch, vr_rig_output_data=True, image_passes=None)
        self.add_ons.extend([keyboard, self.vr])
        keyboard.listen(key="Escape", function=self.quit)

    def run(self) -> None:
        commands = [TDWUtils.create_empty_room(12, 12)]
        # Add the table object and make it kinematic.
        commands.extend(self.get_add_physics_object(model_name="small_table_green_marble",
                                                    object_id=self.get_unique_id(),
                                                    position={"x": 0, "y": 0, "z": 0.5},
                                                    kinematic=True,
                                                    library="models_core.json"))
        # Add a box object and make it graspable.
        box_id = self.get_unique_id()
        commands.extend(self.get_add_physics_object(model_name="woven_box",
                                                    object_id=box_id,
                                                    position={"x": 0.2, "y": 1.0, "z": 0.5},
                                                    library="models_core.json"))
        # Add the ball object and make it graspable.
        sphere_id = self.get_unique_id()
        commands.extend(self.get_add_physics_object(model_name="prim_sphere",
                                                    object_id=sphere_id,
                                                    position={"x": 0.2, "y": 3.0, "z": 0.5},
                                                    library="models_special.json",
                                                    scale_factor={"x": 0.2, "y": 0.2, "z": 0.2}))
        # Send the commands.
        self.communicate(commands)
        # Loop until the Escape key is pressed.
        while not self.done:
            print("Position", self.vr.rig.position)
            print("Rotation", self.vr.rig.rotation)
            print("Forward", self.vr.rig.forward)
            print("Head position", self.vr.head.position)
            print("Head rotation", self.vr.head.rotation)
            print("Head forward", self.vr.head.forward)
            print("Left hand position", self.vr.left_hand.position)
            print("Left hand rotation", self.vr.left_hand.rotation)
            print("Left hand forward", self.vr.left_hand.forward)
            print("Right hand position", self.vr.right_hand.position)
            print("Right hand rotation", self.vr.right_hand.rotation)
            print("Right hand forward", self.vr.right_hand.forward)
            print("")
            self.communicate([])
        self.communicate({"$type": "terminate"})

    def quit(self):
        self.done = True


if __name__ == "__main__":
    c = VRData()
    c.run()
