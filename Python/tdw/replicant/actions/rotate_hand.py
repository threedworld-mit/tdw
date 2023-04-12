from typing import List, Union, Dict, Optional
import numpy as np
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.image_frequency import ImageFrequency
from tdw.replicant.arm import Arm
from tdw.replicant.collision_detection import CollisionDetection
from tdw.replicant.actions.arm_motion import ArmMotion
from tdw.replicant.actions.action import Action


class RotateHand(ArmMotion):
    """
    Rotate one or both hands to target rotations.

    The Replicant's arm(s) will move continuously rotate over multiple `communicate()` calls move until either the motion is complete or the arm collides with something (see `self.collision_detection`).

    - If either hand's rotation is near its target at the end of the action, the action succeeds.
    - The collision detection will respond normally to walls, objects, obstacle avoidance, etc.
    - If `self.collision_detection.previous_was_same == True`, and if the previous action was a subclass of `ArmMotion`, and it ended in a collision, this action ends immediately.
    """

    def __init__(self, targets: Dict[Arm, Union[int, np.ndarray, Dict[str, float]]], arrived_at: float,
                 dynamic: ReplicantDynamic, collision_detection: CollisionDetection, previous: Optional[Action],
                 duration: float, scale_duration: bool):
        """
        :param targets: The target rotation per hand. Key = An [`Arm`](../replicant/arm.md). Value = A rotation. If int: The rotation of the object with this ID. If dict or numpy array: An x, y, z, w quaternion.
        :param arrived_at: If the motion ends and the hand is this angle or less from the target rotation, the action succeeds.
        :param dynamic: The [`ReplicantDynamic`](../replicant_dynamic.md) data that changes per `communicate()` call.
        :param collision_detection: The [`CollisionDetection`](../collision_detection.md) rules.
        :param previous: The previous action. Can be None.
        :param duration: The duration of the motion in seconds.
        :param scale_duration: If True, `duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        """

        super().__init__(arms=list(targets.keys()), dynamic=dynamic, collision_detection=collision_detection, previous=previous,
                         duration=duration, scale_duration=scale_duration)
        """:field
        The target rotation per hand. Key = An [`Arm`](../replicant/arm.md). Value = A rotation. If int: The rotation of the object with this ID. If dict or numpy array: An x, y, z, w quaternion.
        """
        self.targets: Dict[Arm, Union[int, np.ndarray, Dict[str, float]]] = targets
        """:field
        If the motion ends and the hand is this angle or less from the target rotation, the action succeeds.
        """
        self.arrived_at: float = arrived_at

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        for arm in self.targets:
            commands.append({"$type": "replicant_rotate_hand",
                             "id": static.replicant_id,
                             "duration": self.duration,
                             "arm": arm.name,
                             "arrived_at": self.arrived_at,
                             "rotation": self._get_rotation(rotation=self.targets[arm], resp=resp)})
        return commands
