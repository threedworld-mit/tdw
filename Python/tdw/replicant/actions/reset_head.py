from typing import List
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.actions.head_motion import HeadMotion
from tdw.replicant.image_frequency import ImageFrequency


class ResetHead(HeadMotion):
    """
    Reset the head to its neutral rotation.

    The head will continuously move over multiple `communicate()` calls until it is at its neutral rotation.
    """

    def __init__(self, duration: float, scale_duration: bool):
        """
        :param duration: The duration of the motion in seconds.
        :param scale_duration: If True, `duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        """

        super().__init__(duration=duration, scale_duration=scale_duration)

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        commands.append({"$type": "replicant_reset_head",
                         "id": static.replicant_id,
                         "duration": self.duration})
        return commands
