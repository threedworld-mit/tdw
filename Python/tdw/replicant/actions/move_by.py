from typing import Dict, List
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.replicant.actions.animate import Animate
from tdw.replicant.actions.action import Action
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.collision_detection import CollisionDetection
from tdw.agents.image_frequency import ImageFrequency
from tdw.agents.arm import Arm
from tdw.output_data import OutputData, Raycast
from tdw.controller import Controller


class MoveBy(Animate):
    """
    Walk a given distance.
    """

    _BOXCAST_Y: float = 0.25
    _BOXCAST_Z: float = 0.1

    def __init__(self, distance: float, dynamic: ReplicantDynamic, collision_detection: CollisionDetection,
                 previous: Action = None, reset_arms_num_frames: int = 15, arrived_at: float = 0.1,
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
        self._reset_arms_num_frames: int = reset_arms_num_frames
        super().__init__(animation="walking_2",
                         collision_detection=collision_detection,
                         library="humanoid_animations.json",
                         previous=previous,
                         forward=self._distance > 0)
        self._initial_position_v3: Dict[str, float] = TDWUtils.array_to_vector3(dynamic.transform.position)
        self._destination_arr: np.ndarray = dynamic.transform.position + (dynamic.transform.forward * distance)
        self._max_walk_cycles: int = max_walk_cycles
        self._walk_cycle: int = 0
        # Get the ID for the boxcast.
        self._boxcast_id: int = Controller.get_unique_id()
        # Don't try to walk in the same direction twice.
        if self._collision_detection.previous_was_same and previous is not None and isinstance(previous, MoveBy) and \
                previous.status == ActionStatus.collision and np.sign(previous._distance) == np.sign(self._distance):
            self.status = ActionStatus.collision

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        # Reset the arms.
        commands.extend([{"$type": "replicant_reset_arm",
                          "id": static.replicant_id,
                          "num_frames": self._reset_arms_num_frames,
                          "arm": arm.name} for arm in Arm])
        return commands

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        commands = super().get_ongoing_commands(resp=resp, static=static, dynamic=dynamic)
        # Reset the action status because we want to loop the animation.
        if self.status == ActionStatus.success:
            self.status = ActionStatus.ongoing
        if self.status != ActionStatus.ongoing:
            return commands
        else:
            d = np.linalg.norm(dynamic.transform.position - self._destination_arr)
            if d < self._arrived_at:
                self.status = ActionStatus.success
            else:
                # Try to avoid obstacles by boxcasting.
                if self._collision_detection.avoid:
                    # Check the raycast data.
                    for i in range(len(resp) - 1):
                        r_id = OutputData.get_data_type_id(resp[i])
                        if r_id == "rayc":
                            raycast = Raycast(resp[i])
                            if raycast.get_raycast_id() == self._boxcast_id and raycast.get_hit() and raycast.get_hit_object():
                                if raycast.get_object_id() not in self._collision_detection.exclude_objects:
                                    self.status = ActionStatus.detected_obstacle
                                    return commands
                    # Boxcast.
                    position = dynamic.transform.position.copy()
                    position[1] += MoveBy._BOXCAST_Y
                    position[2] += MoveBy._BOXCAST_Z
                    forward = dynamic.transform.forward.copy()
                    forward[1] += MoveBy._BOXCAST_Y
                    forward[2] += MoveBy._BOXCAST_Z
                    commands.append({"$type": "send_boxcast",
                                     "half_extents": {"x": 0.1, "y": 0.1, "z": 0.75},
                                     "origin": TDWUtils.array_to_vector3(position),
                                     "destination": TDWUtils.array_to_vector3(position + forward * 1.75),
                                     "id": self._boxcast_id})
                # We're at the end of the walk cycle. Continue the animation.
                if self._frame_count % self._animation_length == 0:
                    commands.append({"$type": "play_humanoid_animation",
                                     "name": self._record.name,
                                     "id": static.replicant_id,
                                     "framerate": self._record.framerate})
                    # Too many walk cycles. End the action.
                    self._walk_cycle += 1
                    if self._walk_cycle >= self._max_walk_cycles:
                        self.status = ActionStatus.failed_to_move
            return commands
