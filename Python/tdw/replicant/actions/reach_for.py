from typing import List, Dict, Union
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.actions.arm_motion import ArmMotion
from tdw.replicant.collision_detection import CollisionDetection
from tdw.replicant.replicant_simulation_state import EMPTY_OBJECT_MANAGER, OBJECT_MANAGER
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
            targets: Dict[Arm, Dict[str, float]] = dict()
            # Reach for a target position.
            if isinstance(self._target, np.ndarray):
                targets = {arm: TDWUtils.array_to_vector3(self._target) for arm in self._arms}
            elif isinstance(self._target, dict):
                targets = {arm: self._target for arm in self._arms}
            # Reach for a target object.
            elif isinstance(self._target, int):
                centroid: np.ndarray = OBJECT_MANAGER.bounds[self._target].center
                nearest_empty_object_distances: Dict[Arm, float] = dict()
                nearest_empty_object_positions: Dict[Arm, np.ndarray] = dict()
                hand_positions = {arm: dynamic.body_parts[static.hands[arm]].position for arm in self._arms}
                if self._target in EMPTY_OBJECT_MANAGER.empty_object_ids:
                    for empty_object_id in EMPTY_OBJECT_MANAGER.empty_object_ids[self._target]:
                        # Update the nearest affordance point per arm.
                        for arm in self._arms:
                            p = EMPTY_OBJECT_MANAGER.empty_object_positions[empty_object_id]
                            d = np.linalg.norm(p - hand_positions[arm])
                            # Too far away.
                            if d > 0.99:
                                continue
                            if arm not in nearest_empty_object_distances or d < nearest_empty_object_distances[arm]:
                                nearest_empty_object_distances[arm] = d
                                nearest_empty_object_positions[arm] = p
                # Reach for an affordance point.
                for arm in self._arms:
                    if arm in nearest_empty_object_positions:
                        targets[arm] = TDWUtils.array_to_vector3(nearest_empty_object_positions[arm])
                    else:
                        d = np.linalg.norm(centroid - hand_positions[arm])
                        # The centroid is close enough.
                        if d < 0.99:
                            targets[arm] = TDWUtils.array_to_vector3(centroid)
            else:
                raise Exception(f"Invalid target: {self._target}")
            # Immediately fail because one or both arms can't reach a target.
            for arm in self._arms:
                if arm not in targets:
                    self.status = ActionStatus.cannot_reach
                    return []
            # Reach for the target.
            return [{"$type": "replicant_reach_for_position",
                     "position": targets[arm],
                     "id": static.replicant_id,
                     "num_frames": self._num_frames,
                     "arm": arm.name} for arm in self._arms]
        # Continue the action, checking for collisions.
        return super().get_ongoing_commands(resp=resp, static=static, dynamic=dynamic)
