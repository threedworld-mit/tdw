from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.robot import Robot
from tdw.add_ons.third_person_camera import ThirdPersonCamera
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Minimal example of a multi-agent simulation.
"""

c = Controller()
# Add two robots, a camera, and image capture.
robot_0 = Robot(name="ur5",
                robot_id=c.get_unique_id(),
                position={"x": -1, "y": 0, "z": 0.8})
robot_1 = Robot(name="ur10",
                robot_id=c.get_unique_id(),
                position={"x": 0.1, "y": 0, "z": -0.5},
                rotation={"x": 0, "y": 30, "z": 0})
camera = ThirdPersonCamera(avatar_id="a",
                           position={"x": 0, "y": 3.05, "z": 2.1},
                           look_at={"x": 0, "y": 0, "z": 0})
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("multi_agent_minimal")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=["a"], path=path)
c.add_ons.extend([robot_0, robot_1, camera, capture])
c.communicate(TDWUtils.create_empty_room(12, 12))
# Set joint targets.
robot_0.set_joint_targets(targets={robot_0.static.joint_ids_by_name["shoulder_link"]: -70})
robot_1.set_joint_targets(targets={robot_1.static.joint_ids_by_name["shoulder_link"]: 70})
# Wait until the joints stop moving.
while robot_0.joints_are_moving() and robot_1.joints_are_moving():
    c.communicate([])
c.communicate({"$type": "terminate"})
