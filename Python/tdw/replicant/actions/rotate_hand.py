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

    The Replicant's arm(s) will move continuously over multiple `communicate()` calls move until either the motion is complete or the arm collides with something (see `self.collision_detection`).

    - If either hand's rotation is near its target at the end of the action, the action succeeds.
    - The collision detection will respond normally to walls, objects, obstacle avoidance, etc.
    - If `self.collision_detection.previous_was_same == True`, and if the previous action was a subclass of `ArmMotion`, and it ended in a collision, this action ends immediately.
    """

    def __init__(self, target: List[Union[int, np.ndarray, Dict[str, float]]], arrived_at: float, arms: List[Arm],
                 dynamic: ReplicantDynamic, collision_detection: CollisionDetection, previous: Optional[Action],
                 duration: float, scale_duration: bool):
        """
        :param target: Target rotations for each hand. If int: An object ID. If dict or numpy array: An x, y, z, w quaternion.
        :param arrived_at: If the motion ends and the hand is this angle or less from the target rotation, the action succeeds.
        :param arms: A list of [`Arm`](../arm.md) values that will rotate to the `target`. Example: `[Arm.left, Arm.right]`.
        :param dynamic: The [`ReplicantDynamic`](../replicant_dynamic.md) data that changes per `communicate()` call.
        :param collision_detection: The [`CollisionDetection`](../collision_detection.md) rules.
        :param previous: The previous action. Can be None.
        :param duration: The duration of the motion in seconds.
        :param scale_duration: If True, `duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        """

        super().__init__(arms=arms, dynamic=dynamic, collision_detection=collision_detection, previous=previous,
                         duration=duration, scale_duration=scale_duration)
        """:field
        The target. If int: An object ID. If dict or numpy array: An x, y, z, w quaternion.
        """
        self.target: List[Union[int, np.ndarray, Dict[str, float]]] = target
        """:field
        If the motion ends and the hand is this angle or less from the target rotation, the action succeeds.
        """
        self.arrived_at: float = arrived_at

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        for target, arm in zip(self.target, self.arms):
            commands.append({"$type": "replicant_rotate_hand",
                             "id": static.replicant_id,
                             "duration": self.duration,
                             "arm": arm.name,
                             "arrived_at": self.arrived_at,
                             "rotation": self._get_rotation(rotation=target, resp=resp)})
        return commands
