from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.robot import Robot
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Add a UR5 robot and set its joint targets.
"""

c = Controller()
robot_id = c.get_unique_id()
robot = Robot(name="ur5",
              position={"x": 1, "y": 0, "z": -2},
              rotation={"x": 0, "y": 0, "z": 0},
              robot_id=robot_id)
# Add a camera and enable image capture.
camera = ThirdPersonCamera(avatar_id="a",
                           position={"x": -0.1, "y": 1.7, "z": 0.1},
                           look_at=robot_id)
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("set_joint_targets")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=["a"], path=path)
c.add_ons.extend([robot, camera, capture])
c.communicate(TDWUtils.create_empty_room(12, 12))

# Set the initial pose.
while robot.joints_are_moving():
    c.communicate([])

# Strike a cool pose.
robot.set_joint_targets(targets={robot.static.joint_ids_by_name["shoulder_link"]: 50,
                                 robot.static.joint_ids_by_name["forearm_link"]: -60})

# Wait for the joints to stop moving.
while robot.joints_are_moving():
    c.communicate([])

c.communicate({"$type": "terminate"})