# AUTOGENERATED FROM C#. DO NOT MODIFY.

from abc import ABC
from tdw.commands.robot_joint_command import RobotJointCommand


class RobotJointTargetCommand(RobotJointCommand, ABC):
    """
    These commands set target angles for each of the joint's drives. To get the type of joint and its drives, see the send_static_robots command and the StaticRobot output data.
    """

    def __init__(self, joint_id: int, id: int = 0):
        """
        :param joint_id: The ID of the joint.
        :param id: The ID of the robot in the scene.
        """

        super().__init__(joint_id=joint_id, id=id)

