from typing import Dict, List
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.replicant.actions.walk import Walk
from tdw.replicant.actions.action import Action
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.collision_detection import CollisionDetection


class MoveBy(Walk):
    """
    Walk a given distance.
    """

    def __init__(self, distance: float, dynamic: ReplicantDynamic, collision_detection: CollisionDetection,
                 previous: Action = None, reset_arms_num_frames: int = None, arrived_at: float = 0.1,
                 max_walk_cycles: int = 100):
        """
        :param distance: The target distance. If less than 0, the Replicant will walk backwards.
        :param dynamic: [The dynamic Replicant data.](../magnebot_dynamic.md)
        :param collision_detection: The [`CollisionDetection`](collision_detection.md) rules.
        :param previous: The previous action, if any.
        :param reset_arms_num_frames: The number of frames for resetting the arms while walking. This controls the speed of the arm motion.
        :param arrived_at: If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful.
        :param max_walk_cycles: The walk animation will loop this many times maximum. If by that point the Replicant hasn't reached its destination, the action fails.
        """

        self._distance: float = distance
        self._arrived_at: float = arrived_at
        super().__init__(collision_detection=collision_detection, previous=previous, reset_arms_num_frames=reset_arms_num_frames)
        # Get the initial state and the destination.
        self._initial_position_v3: Dict[str, float] = TDWUtils.array_to_vector3(dynamic.transform.position)
        self._destination_arr: np.ndarray = dynamic.transform.position + (dynamic.transform.forward * distance)
        self._max_walk_cycles: int = max_walk_cycles
        self._walk_cycle: int = 0
        # Don't try to walk in the same direction twice.
        if self._collision_detection.previous_was_same and previous is not None and isinstance(previous, MoveBy) and \
                previous.status == ActionStatus.collision and np.sign(previous._distance) == np.sign(self._distance):
            self.status = ActionStatus.collision

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        commands = super().get_ongoing_commands(resp=resp, static=static, dynamic=dynamic)
        if self.status != ActionStatus.ongoing:
            return commands
        else:
            d = np.linalg.norm(dynamic.transform.position - self._destination_arr)
            if d < self._arrived_at:
                self.status = ActionStatus.success
            # We're at the end of the walk cycle. Continue the animation.
            elif self._frame_count % self._animation_length == 0:
                commands.append({"$type": "play_humanoid_animation",
                                 "name": self._record.name,
                                 "id": static.replicant_id,
                                 "framerate": self._record.framerate})
                # Too many walk cycles. End the action.
                self._walk_cycle += 1
                if self._walk_cycle >= self._max_walk_cycles:
                    self.status = ActionStatus.failed_to_move
            return commands
