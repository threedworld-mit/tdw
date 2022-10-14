from typing import List, Dict, Union
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.actions.arm_motion import ArmMotion
from tdw.replicant.collision_detection import CollisionDetection
from tdw.agents.arm import Arm


class ReachFor(ArmMotion):
    """
    Reach for a target object or position.
    """

    def __init__(self, target: Union[int, np.ndarray, Dict[str,  float]], arms: List[Arm], dynamic: ReplicantDynamic,
                 collision_detection: CollisionDetection, previous=None, num_frames: int = 15):
        """
        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        :param arms: The [`Arm`](../../agents/arm.md) values that will reach for the `target`. Example: `[Arm.left, Arm.right]`.
        :param dynamic: [`ReplicantDynamic`](../replicant_dynamic.md) data.
        :param collision_detection: [The collision detection rules.](../collision_detection.md)
        :param previous: The previous action. Can be None.
        :param num_frames: The number of frames for the action. This controls the speed of the action.
        """

        super().__init__(arms=arms, dynamic=dynamic, collision_detection=collision_detection, previous=previous,
                         num_frames=num_frames)
        self._target: Union[int, np.ndarray, Dict[str,  float]] = target
        self._initialized: bool = False

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        if not self._initialized:
            self._initialized = True
            # Reach for a target position.
            if isinstance(self._target, np.ndarray):
                target = TDWUtils.array_to_vector3(self._target)
                return [{"$type": "replicant_reach_for_position",
                         "id": static.replicant_id,
                         "position": target,
                         "num_frames": self._num_frames,
                         "arm": arm.name} for arm in self._arms]
            # Reach for a target position.
            elif isinstance(self._target, dict):
                return [{"$type": "replicant_reach_for_position",
                         "id": static.replicant_id,
                         "position": self._target,
                         "num_frames": self._num_frames,
                         "arm": arm.name} for arm in self._arms]
            # Reach for a target object.
            elif isinstance(self._target, int):
                return [{"$type": "replicant_reach_for_object",
                         "id": static.replicant_id,
                         "object_id": int(self._target),
                         "num_frames": self._num_frames,
                         "arm": arm.name} for arm in self._arms]
            else:
                raise Exception(f"Invalid target: {self._target}")
        # Continue the action, checking for collisions.
        return super().get_ongoing_commands(resp=resp, static=static, dynamic=dynamic)
