from typing import List
from abc import ABC
from tdw.replicant.actions.action import Action
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.image_frequency import ImageFrequency


class IkMotion(Action, ABC):
    """
    Abstract base class for actions driving by inverse kinematics (IK).
    """

    def __init__(self, duration: float, scale_duration: bool):
        """
        :param duration: The duration of the motion in seconds.
        :param scale_duration: If True, `duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        """

        super().__init__()
        """:field
        The duration of the motion in seconds.
        """
        self.duration: float = duration
        """:field
        If True, `duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        """
        self.scale_duration: bool = scale_duration

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        # Scale the duration by the framerate.
        if self.scale_duration:
            self.duration = Action._get_scaled_duration(duration=self.duration, resp=resp)
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        return commands
