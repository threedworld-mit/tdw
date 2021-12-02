from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.robot import Robot
from tdw.add_ons.embodied_avatar import EmbodiedAvatar
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Minimal example of a multi-agent simulation with different types of agents.
"""

c = Controller()
# Add a robot, an embodied avatar, a camera, and image capture.
robot = Robot(name="ur10",
              robot_id=c.get_unique_id(),
              position={"x": -1, "y": 0, "z": 0.8})
embodied_avatar = EmbodiedAvatar(avatar_id="e",
                                 position={"x": 0.1, "y": 0, "z": -0.5})
camera = ThirdPersonCamera(avatar_id="a",
                           position={"x": 0, "y": 4.05, "z": 3.1},
                           look_at={"x": 0, "y": 0, "z": 0})
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("robot_and_avatar")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=["a"], path=path)
c.add_ons.extend([robot, embodied_avatar, camera, capture])
c.communicate(TDWUtils.create_empty_room(12, 12))
# Set the robot's joint targets .
robot.set_joint_targets(targets={robot.static.joint_ids_by_name["shoulder_link"]: -70})
# Move the avatar forward.
embodied_avatar.apply_force(500)
# Wait until the robot joints stop moving.
while robot.joints_are_moving():
    c.communicate([])
c.communicate({"$type": "terminate"})
