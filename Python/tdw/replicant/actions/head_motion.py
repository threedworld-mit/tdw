from abc import ABC
from typing import List
from overrides import final
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.actions.ik_motion import IkMotion
from tdw.replicant.action_status import ActionStatus


class HeadMotion(IkMotion, ABC):
    """
    Abstract base class for actions that rotate the Replicant's head.

    During a head motion, the Replicant's head will continuously move over multiple `communicate()` calls until either the motion is complete.
    """

    @final
    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        # Check if the motion is done.
        if dynamic.output_data_status != ActionStatus.ongoing:
            self.status = dynamic.output_data_status
        return super().get_ongoing_commands(resp=resp, static=static, dynamic=dynamic)
