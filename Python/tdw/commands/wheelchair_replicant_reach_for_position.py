# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.wheelchair_replicant_reach_for_command import WheelchairReplicantReachForCommand
from tdw.replicant.arm import Arm
from typing import Dict


class WheelchairReplicantReachForPosition(WheelchairReplicantReachForCommand):
    """
    Tell a WheelchairReplicant to start to reach for a target position.
    """

    def __init__(self, id: int, arm: Arm, duration: float, absolute: bool, position: Dict[str, float], max_distance: float = 1.5, arrived_at: float = 0.02, set_status: bool = True, offset: Dict[str, float] = None):
        """
        :param id: The unique object ID.
        :param arm: The arm doing the action.
        :param duration: The duration of the motion in seconds.
        :param absolute: If True, the target position is in absolute world space coordinates. If False, it's in local space coordinates.
        :param position: The target position.
        :param max_distance: The maximum distance that the Replicant can reach.
        :param arrived_at: If the hand is this distance from the target position or less, the action succeeded.
        :param set_status: If True, when this command ends, it will set the Replicant output data's status.
        :param offset: This offset will be applied to the target position.
        """

        super().__init__(max_distance=max_distance, arrived_at=arrived_at, set_status=set_status, offset=offset, duration=duration, arm=arm, id=id)
        """:field
        The target position.
        """
        self.position: Dict[str, float] = position
        """:field
        If True, the target position is in absolute world space coordinates. If False, it's in local space coordinates.
        """
        self.absolute: bool = absolute
