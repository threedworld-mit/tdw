from typing import List
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.actions.action import Action
from tdw.replicant.ik_plans.ik_plan import IkPlan


class VerticalHorizontal(IkPlan):
    """
    Split a [`ReachFor`](../actions/reach_for.md) action into two actions:

    1. Reach directly above the current position of the hand to match the y coordinate of the target.
    2. Reach laterally towards the (x, z) coordinates of the target.
    """

    def get_actions(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[Action]:
        targets_1 = []
        for target in self.targets:
            # Get the target as a numpy array.
            if isinstance(target, np.ndarray):
                targets_1.append(target)
            elif isinstance(target, dict):
                targets_1.append(TDWUtils.vector3_to_array(target))
            elif isinstance(target, int):
                targets_1.append(Action._get_object_bounds(object_id=target, resp=resp)["center"])
            else:
                raise Exception(f"Invalid target: {target}")
        # Divide `self.duration` by the number of sub-actions.
        duration = self.duration / 2
        targets_0 = []
        for target, arm in zip(targets_1, self.arms):
            # The initial position of the hand.
            p0: np.ndarray = dynamic.body_parts[static.hands[arm]].position
            # Raise the hand up.
            p1 = np.copy(p0)
            p1[1] = target[1]
            targets_0.append(p1)
        return [self._get_reach_for(targets=targets_0, arms=self.arms, absolute=True, duration=duration,
                                    dynamic=dynamic, from_held=False),
                self._get_reach_for(targets=targets_1, arms=self.arms, absolute=self.absolute, duration=duration,
                                    dynamic=dynamic, from_held=self.from_held)]
