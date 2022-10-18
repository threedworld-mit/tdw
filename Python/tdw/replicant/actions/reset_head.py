from typing import List
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.actions.head_motion import HeadMotion
from tdw.agents.image_frequency import ImageFrequency


class ResetHead(HeadMotion):
    """
    Reset the head to its neutral rotation.
    """

    def __init__(self, duration: float = 0.1):
        """
        :param duration: The duration of the motion in seconds.
        """

        super().__init__(duration=duration)

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        commands.append({"$type": "replicant_reset_head",
                         "id": static.replicant_id,
                         "duration": self._duration})
        return commands
