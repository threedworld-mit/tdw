import numpy as np
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.replicant import Replicant
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.quaternion_utils import QuaternionUtils
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.arm import Arm
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Rotate the Replicant's hand without moving the arm.
"""

c = Controller()
replicant = Replicant()
camera = ThirdPersonCamera(position={"x": -0.9, "y": 1.175, "z": 3},
                           look_at={"x": 0, "y": 1, "z": 0},
                           avatar_id="a")
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("replicant_rotate_hand")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=["a"], path=path)
c.add_ons.extend([replicant, camera, capture])
c.communicate([TDWUtils.create_empty_room(12, 12)])
# Reach for a target position so that it's easier to see the hand rotation.
replicant.reach_for(target={"x": 0.6, "y": 0.8, "z": 0.9},
                    arm=Arm.right)
while replicant.action.status == ActionStatus.ongoing:
    c.communicate([])
c.communicate([])
# Get some rotations.
q0 = QuaternionUtils.euler_angles_to_quaternion(np.array([30, 0, 0]))
q1 = QuaternionUtils.euler_angles_to_quaternion(np.array([0, 70, 0]))
q2 = QuaternionUtils.euler_angles_to_quaternion(QuaternionUtils.UP)
# Rotate the hand.
for rotation in [q0, q1, q2]:
    replicant.rotate_hand(targets={Arm.right: rotation})
    while replicant.action.status == ActionStatus.ongoing:
        c.communicate([])
c.communicate({"$type": "terminate"})
