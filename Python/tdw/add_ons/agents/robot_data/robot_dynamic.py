from typing import List, Dict, Optional
import numpy as np
from tdw.output_data import OutputData, Robot
from tdw.object_data.transform import Transform
from tdw.add_ons.agents.agent_state import AgentState
from tdw.add_ons.agents.robot_data.joint_dynamic import JointDynamic


class RobotDynamic(AgentState):
    """
    Dynamic data for a robot that can change per frame (such as the position of the robot, the angle of a joint, etc.)
    """

    """:class_var
    If the joint moved by less than this angle or distance since the previous frame, it's considered to be non-moving.
    """
    NON_MOVING: float = 0.001

    def __init__(self, robot_id: int, resp: List[bytes], previous=None):
        """
        :param resp: The response from the build, which we assume contains `Robot` output data.
        :param robot_id: The ID of this robot.
        :param previous: If not None, the previous RobotDynamic data. Use this to determine if the joints are moving.
        """

        """:field
        The Transform data for this robot.
        """
        self.transform: Optional[Transform] = None
        """:field
        A dictionary of [dynamic joint data](joint_dynamic.md). Key = The ID of the joint.
        """
        self.joints: Dict[int, JointDynamic] = dict()
        self.__previous = previous
        self._robot_id: int = robot_id
        super().__init__(resp=resp)

    def _set_state(self, resp: List[bytes]) -> None:
        got_data: bool = False
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "robo":
                robot: Robot = Robot(resp[i])
                if robot.get_id() == self._robot_id:
                    got_data = True
                    self.transform = Transform(position=np.array(robot.get_position()),
                                               rotation=np.array(robot.get_rotation()),
                                               forward=np.array(robot.get_forward()))
                    # Get dynamic data for each joint.
                    for j in range(robot.get_num_joints()):
                        joint = JointDynamic(robot=robot, joint_index=j)
                        # Determine if the joint is currently moving.
                        if self.__previous is not None:
                            self.__previous: RobotDynamic
                            previous_joint: JointDynamic = self.__previous.joints[joint.joint_id]
                            for k in range(len(previous_joint.angles)):
                                if np.linalg.norm(previous_joint.angles[k] - joint.angles[k]) > RobotDynamic.NON_MOVING:
                                    joint.moving = True
                                    break
                        self.joints[joint.joint_id] = joint
        assert got_data, "No dynamic robot data in response from build!"
