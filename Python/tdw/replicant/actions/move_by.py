from typing import Dict, List
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Transforms, Raycast
from tdw.replicant.replicant_utils import ReplicantUtils
from tdw.replicant.actions.walk_motion import WalkMotion
from tdw.replicant.actions.action import Action
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.collision_detection import CollisionDetection
from tdw.replicant.arm import Arm
from tdw.replicant.image_frequency import ImageFrequency



class MoveBy(WalkMotion):
    """
    Walk the Replicant by a given distance.
    """

    def __init__(self, distance: float, dynamic: ReplicantDynamic, collision_detection: CollisionDetection,
                 held_objects: Dict[Arm, List[int]], avoid_objects: bool = False, arrived_at: float = 0.1, 
                 previous: Action = None):
        """
        :param distance: The target distance.
        :param arrived_at: If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful.
        :param dynamic: [The dynamic Replicant data.](../magnebot_dynamic.md)
        :param collision_detection: [The collision detection rules.](../collision_detection.md)
        :param previous: The previous action, if any.
        """
        """:field
        The target distance.
        """
        self.distance: float = distance
        self._arrived_at: float = arrived_at
        super().__init__(dynamic=dynamic, collision_detection=collision_detection, held_objects=held_objects, 
                         avoid_objects=avoid_objects, previous=previous)
        # Get the initial state.
        self._initial_position_v3: Dict[str, float] = TDWUtils.array_to_vector3(dynamic.position)
        self._target_position_arr: np.array = dynamic.position + (dynamic.forward * distance)
        self._target_position_v3: Dict[str, float] = TDWUtils.array_to_vector3(self._target_position_arr)
        # Total number of frames needed to cover distance.
        self.num_frames = int(distance / self.meters_per_frame)
        # Running frame count.
        self.total_frame_count: int = 0
        # Per-loop frame count.
        self.frame_count: int = 0
        # Determine number of walk loops needed to cover distance.
        if self.num_frames <= self.walk_cycle_num_frames:
            self.num_loops = 0
            self.remainder = 0
        else:
            self.num_loops = int(self.num_frames / self.walk_cycle_num_frames)
            self.remainder = self.num_frames - (self.walk_cycle_num_frames * self.num_loops)
        # Running loop count.
        self.loop_count: int = 0
        # Flag for remainder handling.
        self.processing_remainder: bool = False

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        p1 = dynamic.position
        d = np.linalg.norm(p1 - self._target_position_arr)
        # We've arrived at the target.
        if d < self._arrived_at:
            self.status = ActionStatus.success
            commands = []
            commands.extend(self.get_end_commands(resp=resp, static=static, dynamic=dynamic, image_frequency=None))
            return commands
        elif not self._is_valid_ongoing(dynamic=dynamic):
            return []
        elif self.status == ActionStatus.ongoing:
            # We are still walking.
            if self.processing_remainder:
                if self.frame_count < self.remainder:
                    self.frame_count += 1 
                    self.total_frame_count += 1
                    return []
                else:
                    self.processing_remainder = False
                    return []
            else:
                if self.loop_count <= self.num_loops:
                    if self.frame_count < self.walk_cycle_num_frames:
                        self.frame_count += 1 
                        self.total_frame_count += 1
                        if self.avoid_objects:
                            commands = []
                            for i in range(len(resp) - 1):
                                r_id = OutputData.get_data_type_id(resp[i])
                                if r_id == "rayc":
                                    raycast = Raycast(resp[i])
                                    #if raycast.get_raycast_id() == raycast_id:
                                    if raycast.get_hit() and raycast.get_hit_object():
                                        commands = []
                                        print("Boxcast hit; object ID = " + str(raycast.get_object_id()))
                                        self.status = ActionStatus.detected_obstacle
                                        break
                            return commands
                        else:
                            return []
                    elif (self.num_frames - self.total_frame_count) > self.remainder:
                        # Start a new loop.
                        commands = []
                        self.loop_count += 1
                        self.frame_count = 0
                        commands.extend(self._get_walk_commands(dynamic=dynamic))
                        return commands
                    else:
                        # We have performed the required number of loop cycles. 
                        # Now set up to process any remainder frames.
                        if self.remainder > 0:
                            self.processing_remainder = True
                            commands = []
                            self.frame_count = 0
                            commands.extend(self._get_walk_commands(dynamic=dynamic))
                            return commands
                

    def _previous_was_same(self, previous: Action) -> bool:
        if isinstance(previous, MoveBy):
            return (previous.distance > 0 and self.distance > 0) or (previous.distance < 0 and self.distance < 0)
        else:
            return False

