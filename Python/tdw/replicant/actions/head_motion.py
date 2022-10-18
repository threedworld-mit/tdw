from abc import ABC
from typing import List
from overrides import final
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.actions.action import Action
from tdw.replicant.action_status import ActionStatus


class HeadMotion(Action, ABC):
    """
    Abstract base class for actions that rotate the Replicant's head.
    """

    def __init__(self, duration: float = 0.1):
        """
        :param duration: The duration of the motion in seconds.
        """

        super().__init__()
        self._duration: float = duration

    @final
    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        if self._get_motion_complete(replicant_id=static.replicant_id, resp=resp):
            self.status = ActionStatus.success
        return []
