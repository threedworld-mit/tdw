from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.oculus_leap_motion import OculusLeapMotion
from tdw.add_ons.leap_motion_pose_recorder import LeapMotionPoseRecorder
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH
from tdw.replicant.arm import Arm

"""
Record a hand pose.
"""

c = Controller()
vr = OculusLeapMotion()
pose_recorder = LeapMotionPoseRecorder()
c.add_ons.extend([vr, pose_recorder])
c.communicate(TDWUtils.create_empty_room(12, 12))
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("leap_motion_pose/pose.npy").resolve()
print(f"Pose will be saved to: {path}")
pose_recorder.record(path=path, time_to_capture=10, hands=[Arm.right])
while pose_recorder.is_recording():
    c.communicate([])
c.communicate({"$type": "terminate"})
