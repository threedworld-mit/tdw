from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.add_ons.robot import Robot
from tdw.add_ons.image_capture import ImageCapture
from tdw.backend.paths import EXAMPLE_CONTROLLER_OUTPUT_PATH

"""
Add a camera to a UR5 robot.
"""

c = Controller()
robot_id = c.get_unique_id()
robot = Robot(name="ur5", robot_id=robot_id)
path = EXAMPLE_CONTROLLER_OUTPUT_PATH.joinpath("parent_robot_to_avatar")
print(f"Images will be saved to: {path}")
capture = ImageCapture(avatar_ids=["avatar"], path=path)
c.add_ons.extend([robot, capture])
commands = [TDWUtils.create_empty_room(12, 12)]
commands.extend(TDWUtils.create_avatar(avatar_id="avatar"))
c.communicate(commands)

joint_id = robot.static.joint_ids_by_name["wrist_3_link"]
joint_position = robot.dynamic.joints[joint_id].position
robot.set_joint_targets(targets={robot.static.joint_ids_by_name["shoulder_link"]: -70,
                                 robot.static.joint_ids_by_name["forearm_link"]: -55,
                                 robot.static.joint_ids_by_name["wrist_3_link"]: 60})
c.communicate({"$type": "parent_avatar_to_robot",
               "position": {"x": 0, "y": 0, "z": 0},
               "body_part_id": joint_id,
               "avatar_id": "avatar",
               "id": robot_id})
while robot.joints_are_moving():
    c.communicate([])
c.communicate({"$type": "terminate"})
