from typing import List
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.actions.action import Action
from tdw.replicant.actions.reset_arm import ResetArm
from tdw.replicant.ik_plans.ik_plan import IkPlan


class Reset(IkPlan):
    """
    Reset the Replicant to its neutral position and then reach for the target.
    """

    def get_actions(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[Action]:
        return [ResetArm(arms=self.arms, dynamic=dynamic, collision_detection=self.collision_detection,
                         previous=self.previous, duration=self.duration, scale_duration=self.scale_duration),
                self._get_reach_for(targets=self.targets, arms=self.arms, absolute=self.absolute, duration=self.duration,
                                    dynamic=dynamic, from_held=self.from_held)]
