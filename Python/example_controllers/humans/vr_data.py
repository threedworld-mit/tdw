from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.keyboard import Keyboard
from tdw.output_data import OutputData, VRRig


class VRData(Controller):
    """
    Add several objects to the scene and parse VR output data.
    """

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.done = False

        keyboard = Keyboard()
        self.add_ons.append(keyboard)
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
        self.communicate([{"$type": "set_graspable",
                           "id": box_id}])
        # Add the ball object and make it graspable.
        sphere_id = self.get_unique_id()
        commands.extend(self.get_add_physics_object(model_name="prim_sphere",
                                                    object_id=sphere_id,
                                                    position={"x": 0.2, "y": 3.0, "z": 0.5},
                                                    library="models_special.json",
                                                    scale_factor={"x": 0.2, "y": 0.2, "z": 0.2}))
        commands.append({"$type": "set_graspable",
                         "id": sphere_id})
        # Receive VR data per frame.
        commands.append({"$type": "send_vr_rig",
                         "frequency": "always"})
        # Send the commands.
        resp = self.communicate(commands)
        # Loop until the Escape key is pressed.
        while not self.done:
            for i in range(len(resp) - 1):
                r_id = OutputData.get_data_type_id(resp[i])
                # Parse VR data.
                if r_id == "vrri":
                    vr_rig = VRRig(resp[i])
                    print("Position", vr_rig.get_position())
                    print("Rotation", vr_rig.get_rotation())
                    print("Forward", vr_rig.get_forward())

                    print("Head position", vr_rig.get_head_position())
                    print("Head rotation", vr_rig.get_head_rotation())
                    print("Head forward", vr_rig.get_head_forward())

                    print("Left hand position", vr_rig.get_left_hand_position())
                    print("Left hand rotation", vr_rig.get_left_hand_rotation())
                    print("Left hand forward", vr_rig.get_left_hand_forward())

                    print("Right hand position", vr_rig.get_right_hand_position())
                    print("Right hand rotation", vr_rig.get_right_hand_rotation())
                    print("Right hand forward", vr_rig.get_right_hand_forward())

                    print("")
            resp = self.communicate([])
        self.communicate({"$type": "terminate"})

    def quit(self):
        self.done = True


if __name__ == "__main__":
    c = VRData()
    c.run()
