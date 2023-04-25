from typing import List
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.actions.action import Action
from tdw.replicant.actions.reach_for import ReachFor
from tdw.replicant.ik_plans.ik_plan import IkPlan


class VerticalHorizontal(IkPlan):
    """
    Split a [`ReachFor`](../actions/reach_for.md) action into two actions:

    1. Reach directly above the current position of the hand to match the y coordinate of the target.
    2. Reach laterally towards the (x, z) coordinates of the target.
    """

    def get_actions(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[ReachFor]:
        # Get the target as a numpy array.
        if isinstance(self.target, np.ndarray):
            target_arr: np.ndarray = self.target
        elif isinstance(self.target, dict):
            target_arr = TDWUtils.vector3_to_array(self.target)
        elif isinstance(self.target, int):
            target_arr = Action._get_object_bounds(object_id=self.target, resp=resp)["center"]
        else:
            raise Exception(f"Invalid target: {self.target}")
        # Divide `self.duration` by the number of sub-actions.
        duration = self.duration / 2
        # The initial position of the hand.
        p0: np.ndarray = dynamic.body_parts[static.hands[self.arm]].position
        # Raise the hand up.
        p1 = np.copy(p0)
        p1[1] = target_arr[1]
        return [self._get_reach_for(target=p1, absolute=False, duration=duration, dynamic=dynamic),
                self._get_reach_for(target=self.target, absolute=self.absolute, duration=duration, dynamic=dynamic)]
