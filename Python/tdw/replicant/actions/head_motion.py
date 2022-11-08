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

    Duration an head motion, the Replicant's head will continuously move over multiple `communicate()` calls until either the motion is complete.
    """

    def __init__(self, duration: float):
        """
        :param duration: The duration of the motion in seconds.
        """

        super().__init__()
        """:field
        The duration of the motion in seconds.
        """
        self.duration: float = duration

    @final
    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        # Check if the motion is done.
        if dynamic.output_data_status != ActionStatus.ongoing:
            self.status = dynamic.output_data_status
        return []
