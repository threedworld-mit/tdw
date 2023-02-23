from typing import List
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.actions.head_motion import HeadMotion
from tdw.replicant.image_frequency import ImageFrequency


class RotateHead(HeadMotion):
    """
    Rotate the head by an angle around an axis.

    The head will continuously move over multiple `communicate()` calls until it is looking at the target.
    """

    _VALID_AXES: List[str] = ["pitch", "yaw", "roll"]

    def __init__(self, axis: str, angle: float, duration: float, scale_duration: bool):
        """
        :param axis: The axis of rotation. Options: `"pitch"`, `"yaw"`, `"roll"`.
        :param angle: The target angle in degrees.
        :param duration: The duration of the motion in seconds.
        :param scale_duration: If True, `duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        """

        super().__init__(duration=duration, scale_duration=scale_duration)
        """:field
        The axis of rotation. Options: `"pitch"`, `"yaw"`, `"roll"`.
        """
        self.axis: str = axis.lower()
        if self.axis not in RotateHead._VALID_AXES:
            raise Exception(f"Invalid head rotation axis: {self.axis}")
        """:field
        The target angle in degrees.
        """
        self.angle: float = angle

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        commands.append({"$type": "replicant_rotate_head_by",
                         "id": static.replicant_id,
                         "angle": float(self.angle),
                         "axis": self.axis})
        return commands
