# AUTOGENERATED FROM C#. DO NOT MODIFY.

from abc import ABC
from tdw.commands.replicant_base_arm_command import ReplicantBaseArmCommand
from tdw.replicant.arm import Arm


class WheelchairReplicantArmCommand(ReplicantBaseArmCommand, ABC):
    """
    These commands involve a WheelchairReplicant's arm.
    """

    def __init__(self, id: int, arm: Arm):
        """
        :param id: The unique object ID.
        :param arm: The arm doing the action.
        """

        super().__init__(arm=arm, id=id)

