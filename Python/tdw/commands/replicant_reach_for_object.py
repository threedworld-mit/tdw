# AUTOGENERATED FROM C#. DO NOT MODIFY.

from tdw.commands.replicant_reach_for_command import ReplicantReachForCommand
from tdw.replicant.arm import Arm
from typing import Dict


class ReplicantReachForObject(ReplicantReachForCommand):
    """
    Tell the Replicant to start to reach for a target object. The Replicant will try to reach for the nearest empty object attached to the target. If there aren't any empty objects, the Replicant will reach for the nearest bounds position.
    """

    def __init__(self, id: int, arm: Arm, duration: float, object_id: int, max_distance: float = 1.5, arrived_at: float = 0.02, set_status: bool = True, offset: Dict[str, float] = None):
        """
        :param id: The unique object ID.
        :param arm: The arm doing the action.
        :param duration: The duration of the motion in seconds.
        :param object_id: The target object ID.
        :param max_distance: The maximum distance that the Replicant can reach.
        :param arrived_at: If the hand is this distance from the target position or less, the action succeeded.
        :param set_status: If True, when this command ends, it will set the Replicant output data's status.
        :param offset: This offset will be applied to the target position.
        """

        super().__init__(max_distance=max_distance, arrived_at=arrived_at, set_status=set_status, offset=offset, duration=duration, arm=arm, id=id)
        """:field
        The target object ID.
        """
        self.object_id: int = object_id
