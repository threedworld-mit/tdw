# AUTOGENERATED FROM C#. DO NOT MODIFY.

from abc import ABC
from tdw.commands.robot_joint_command import RobotJointCommand


class SetRobotJointPositionCommand(RobotJointCommand, ABC):
    """
    These commands instantaneously set the robot joint angles and positions. These commands SHOULD NOT be used in place of physics-based motion. Unity will interpret these commands as a VERY fast motion. These commands should only be used when a robot is first created in order to set an initial pose.
    """

    def __init__(self, joint_id: int, id: int = 0):
        """
        :param joint_id: The ID of the joint.
        :param id: The ID of the robot in the scene.
        """

        super().__init__(joint_id=joint_id, id=id)

