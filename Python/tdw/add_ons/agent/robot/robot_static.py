from typing import List, Dict
from tdw.output_data import OutputData, StaticRobot
from tdw.add_ons.agent.robot.joint_static import JointStatic
from tdw.add_ons.agent.robot.non_moving import NonMoving
from tdw.add_ons.agent.agent_state import AgentState


class RobotStatic(AgentState[int]):
    """
    Static data for a robot that won't change due to physics (such as the joint IDs, segmentation colors, etc.)
    """

    def _set_state(self, resp: List[bytes]) -> None:
        got_data: bool = False
        """:field
        A dictionary of [Static robot joint data](joint_static.md) for each joint. Key = The ID of the joint.
        """
        self.joints: Dict[int, JointStatic] = dict()
        """:field
        A dictionary of [Static data for non-moving parts](non_moving.md) for each non-moving part. Key = The ID of the part.
        """
        self.non_moving: Dict[int, NonMoving] = dict()
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "srob":
                static_robot: StaticRobot = StaticRobot(resp[i])
                if static_robot.get_id() == self.id:
                    got_data = True
                    for j in range(static_robot.get_num_joints()):
                        joint = JointStatic(static_robot=static_robot, joint_index=j)
                        self.joints[joint.joint_id] = joint
                    for j in range(static_robot.get_num_non_moving()):
                        non_moving = NonMoving(static_robot=static_robot, index=j)
                        self.non_moving[non_moving.object_id] = non_moving
        assert got_data, "No static robot data in response from build!"
        """:field
        A list of joint IDs and non-moving body part IDs.
        """
        self.body_parts: List[int] = list(self.joints.keys())
        self.body_parts.extend(self.non_moving.keys())
