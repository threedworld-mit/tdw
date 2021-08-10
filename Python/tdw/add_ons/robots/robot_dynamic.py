from typing import List, Dict
import numpy as np
from tdw.output_data import OutputData, Robot
from tdw.add_ons.robots.joint_dynamic import JointDynamic


class RobotDynamic:
    """
    Dynamic data for a robot that can change per frame (such as the position of the robot, the angle of a joint, etc.)
    """

    def __init__(self, resp: List[bytes], robot_id: int, previous=None, non_moving: float = 0.001):
        """
        :param resp: The response from the build, which we assume contains `StaticRobot` output data.
        :param robot_id: The ID of this robot.
        :param previous: If not None, the previous RobotDynamic data. Use this to determine if the joints are moving.
        :param non_moving: If the joint has moved by less than this angle or distance since the previous frame, it's considered to be non-moving.
        """

        got_data: bool = False
        """:field
        The ID of this robot.
        """
        self.robot_id: int = robot_id
        """:field
        The current position of the robot as an `[x, y, z]` numpy array.
        """
        self.position: np.array = np.array([0, 0, 0])
        """:field
        The current rotation of the robot as an `[x, y, z, w]` quaternion numpy array.
        """
        self.rotation: np.array = np.array([0, 0, 0, 0])
        """:field
        The forward directional vector of the robot as an `[x, y, z]` numpy array.
        """
        self.forward: np.array = np.array([0, 0, 0])
        """:field
        A dictionary of [dynamic joint data](joint_dynamic.md). Key = The ID of the joint.
        """
        self.joints: Dict[int, JointDynamic] = dict()
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "robo":
                robot: Robot = Robot(resp[i])
                if robot.get_id() == self.robot_id:
                    got_data = True

                    # Get the dynamic data for the robot.
                    self.position = np.array(robot.get_position())
                    self.rotation = np.array(robot.get_rotation())
                    self.forward = np.array(robot.get_forward())

                    # Get dynamic data for each joint.
                    for j in range(robot.get_num_joints()):
                        joint = JointDynamic(robot=robot, joint_index=j)
                        # Determine if the joint is currently moving.
                        if previous is not None:
                            previous: RobotDynamic
                            previous_joint: JointDynamic = previous.joints[joint.joint_id]
                            for k in range(len(previous_joint.angles)):
                                if np.linalg.norm(previous_joint.angles[k] - joint.angles[k]) > non_moving:
                                    joint.moving = True
                                    break
                        self.joints[joint.joint_id] = joint
        assert got_data, "No dynamic robot data in response from build!"
