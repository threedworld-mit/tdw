import numpy as np
from tdw.controller import Controller
from tdw.add_ons.oculus_touch import OculusTouch
from tdw.add_ons.robot import Robot
from tdw.tdw_utils import TDWUtils
from tdw.vr_data.oculus_touch_button import OculusTouchButton


class OculusTouchAxisListener(Controller):
    """
    Control a robot arm with the Oculus Touch control sticks.
    """

    # This controls how fast the joints will rotate.
    SPEED: float = 0.5

    def __init__(self, port: int = 1071, check_version: bool = True, launch_build: bool = True):
        super().__init__(port=port, check_version=check_version, launch_build=launch_build)
        self.robot: Robot = Robot(name="ur5", position={"x": 0, "y": 0, "z": 2})
        self.vr: OculusTouch = OculusTouch()
        # Move the robot joints with the control sticks.
        self.vr.listen_to_axis(is_left=True, function=self.left_axis)
        self.vr.listen_to_axis(is_left=False, function=self.right_axis)
        # Quit when the left trigger button is pressed.
        self.vr.listen_to_button(button=OculusTouchButton.trigger_button, is_left=True, function=self.quit)
        self.add_ons.extend([self.robot, self.vr])
        self.done: bool = False

    def run(self) -> None:
        self.communicate(TDWUtils.create_empty_room(12, 12))
        while not self.done:
            self.communicate([])
        self.communicate({"$type": "terminate"})

    def left_axis(self, delta: np.array) -> None:
        # Get the IDs and current angles of the joints.
        shoulder_link_id = self.robot.static.joint_ids_by_name["shoulder_link"]
        shoulder_link_angle = self.robot.dynamic.joints[shoulder_link_id].angles[0]
        upper_arm_link_id = self.robot.static.joint_ids_by_name["upper_arm_link"]
        upper_arm_link_angle = self.robot.dynamic.joints[upper_arm_link_id].angles[0]
        # Set the joint targets by adding or subtracting from the axis delta.
        self.robot.set_joint_targets({shoulder_link_id: shoulder_link_angle + delta[0] * OculusTouchAxisListener.SPEED,
                                      upper_arm_link_id: upper_arm_link_angle + delta[1] * OculusTouchAxisListener.SPEED})

    def right_axis(self, delta: np.array) -> None:
        # Get the IDs and current angles of the joints.
        forearm_link_id = self.robot.static.joint_ids_by_name["forearm_link"]
        forearm_link_angle = self.robot.dynamic.joints[forearm_link_id].angles[0]
        wrist_1_link_id = self.robot.static.joint_ids_by_name["wrist_1_link"]
        wrist_1_link_angle = self.robot.dynamic.joints[wrist_1_link_id].angles[0]
        # Set the joint targets by adding or subtracting from the axis delta.
        self.robot.set_joint_targets({forearm_link_id: forearm_link_angle + delta[0] * OculusTouchAxisListener.SPEED,
                                      wrist_1_link_id: wrist_1_link_angle + delta[1] * OculusTouchAxisListener.SPEED})

    def quit(self):
        self.done = True


if __name__ == "__main__":
    c = OculusTouchAxisListener()
    c.run()
