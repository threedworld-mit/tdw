import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.robot_arm import RobotArm
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Control a UR5 robot arm with inverse kinematics (IK).
"""

c = Controller()
ur5 = RobotArm(name="ur5", robot_id=0)
camera = ThirdPersonCamera(avatar_id="a",
                           position={"x": -0.881, "y": 0.836, "z": -1.396},
                           look_at={"x": 0, "y": 0.2, "z": 0})
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("ur5_ik")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=["a"], path=path)
c.add_ons.extend([ur5, camera, capture])
c.communicate(TDWUtils.create_empty_room(12, 12))

# Reach for a target position.
target_position = np.array([0.3, 0.7, 0.3])
ur5.reach_for(target=target_position)
while ur5.joints_are_moving():
    c.communicate([])

# Calculate the distance from the end effector to the target position.
end_effector_position = ur5.dynamic.joints[ur5.static.joint_ids_by_name["wrist_3_link"]].position
print(np.linalg.norm(target_position - end_effector_position))
c.communicate({"$type": "terminate"})
