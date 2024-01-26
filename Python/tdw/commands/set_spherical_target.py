# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.robot_joint_target_command import RobotJointTargetCommand
from typing import Dict


class SetSphericalTarget(RobotJointTargetCommand):
    """
    Set the target angles (x, y, z) of a spherical robot joint. Per frame, the joint will revolve towards the targets until it is either no longer possible to do so (i.e. due to physics) or because it has reached the target angles.
    """

    def __init__(self, joint_id: int, target: Dict[str, float], id: int = 0):
        """
        :param joint_id: The ID of the joint.
        :param target: The target angles in degrees for the (x, y, z) drives.
        :param id: The ID of the robot in the scene.
        """

        super().__init__(joint_id=joint_id, id=id)
        """:field
        The target angles in degrees for the (x, y, z) drives.
        """
        self.target: Dict[str, float] = target