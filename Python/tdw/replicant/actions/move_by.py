from typing import Dict, List
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.output_data import Transforms
from tdw.replicant.replicant_utils import ReplicantUtils
from tdw.replicant.actions.walk_motion import WalkMotion
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic


class MoveBy(WalkMotion):
    """
    Walk the Replicant by a given distance.
    """

    def __init__(self, distance: float, dynamic: ReplicantDynamic, collision_detection: CollisionDetection,
                 arrived_at: float = 0.1, previous: Action = None):
        """
        :param distance: The target distance.
        :param arrived_at: If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful.
        :param dynamic: [The dynamic Magnebot data.](../magnebot_dynamic.md)
        :param collision_detection: [The collision detection rules.](../collision_detection.md)
        :param previous: The previous action, if any.
        """
        """:field
        The target distance.
        """
        self.distance: float = distance
        self._arrived_at: float = arrived_at
        super().__init__(dynamic=dynamic, collision_detection=collision_detection, previous=previous)
        # Get the initial state.
        self._initial_position_v3: Dict[str, float] = ReplicantUtils.get_replicant_position(replicant_id)
        self._target_position_arr: np.array = dynamic.transform.position + (dynamic.transform.forward * distance)
        self._target_position_v3: Dict[str, float] = TDWUtils.array_to_vector3(self._target_position_arr)
        # Total number of frames needed to cover distance.
        self.num_frames = int(distance / self.meters_per_frame)
        # Running frame count.
        self.total_frame_count: int = 0
        # Per-loop frame count.
        self.frame_count: int = 0
        # Determine number of walk loops needed to cover distance.
        if self.num_frames <= self.walk_cycle_num_frames:
            self.num_loops = 1
            self.remainder = 0
        else:
            self.num_loops = int(self.num_frames / self.walk_cycle_num_frames)
            self.remainder = self.num_frames - (self.walk_cycle_num_frames * self.num_loops)
        # Running loop count.
        self.loop_count: int = 0

    def _get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        # We've arrived at the target.
        if self.total_frame_count >= self.num_frames:
            self.status = ActionStatus.success
            return []
        elif not self._is_valid_ongoing(dynamic=dynamic):
            return []
        else:
            # We are still walking.
            if self.loop_count < self.num_loops:
                if self.frame_count < self.walk_cycle_num_frames:
                    self.frame_count += 1 
                    self.total_frame_count += 1
                    return []
                else:
                # Start a new loop.
                self.loop_count += 1
                self.frame_count = 0
                commands.extend(self._get_walk_commands(dynamic=dynamic))

    def _previous_was_same(self, previous: Action) -> bool:
        if isinstance(previous, MoveBy):
            return (previous.distance > 0 and self.distance > 0) or (previous.distance < 0 and self.distance < 0)
        else:
            return False




        commands = []
        
            commands.append({"$type": "play_humanoid_animation",
                             "name": "walking_2",
                             "id": h_id})

            for i in range(num_loops):
                self.communicate({"$type": "play_humanoid_animation",
                                  "name": "walking_2",
                                  "id": h_id})
                frame = 0
                while frame < walk_record.get_num_frames():
                    self.communicate([])
                    frame += 1
            remainder = num_frames - (walk_record.get_num_frames() * num_loops)
            self.communicate({"$type": "play_humanoid_animation",
                              "name": "walking_2",
                              "id": h_id})
            frame = 0
            while frame < remainder:
                self.communicate([])
                frame += 1
