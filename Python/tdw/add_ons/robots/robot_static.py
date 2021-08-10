from typing import List, Dict
from tdw.output_data import OutputData, StaticRobot
from tdw.add_ons.robots.joint_static import JointStatic
from tdw.add_ons.robots.non_moving import NonMoving


class RobotStatic:
    """
    Static data for a robot that won't change due to physics (such as the joint IDs, segmentation colors, etc.)
    """

    def __init__(self, resp: List[bytes], robot_id: int):
        """
        :param resp: The response from the build, which we assume contains `StaticRobot` output data.
        :param robot_id: The ID of this robot.
        """

        got_data: bool = False
        """:field
        A dictionary of [Static robot joint data](joint_static.md) for each joint. Key = The ID of the joint.
        """
        self.joints: Dict[int, JointStatic] = dict()
        """:field
        A dictionary of [Static data for non-moving parts](non_moving.md) for each non-moving part. Key = The ID of the part.
        """
        self.non_moving: Dict[int, NonMoving] = dict()
        """:field
        The ID of this robot.
        """
        self.robot_id: int = robot_id
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "srob":
                static_robot: StaticRobot = StaticRobot(resp[i])
                if static_robot.get_id() == self.robot_id:
                    got_data = True
                    for j in range(static_robot.get_num_joints()):
                        joint = JointStatic(static_robot=static_robot, joint_index=j)
                        self.joints[joint.joint_id] = joint
                    for j in range(static_robot.get_num_non_moving()):
                        non_moving = NonMoving(static_robot=static_robot, index=j)
                        self.non_moving[non_moving.object_id] = non_moving
        assert got_data, "No static robot data in response from build!"
