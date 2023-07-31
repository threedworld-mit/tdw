from typing import Optional, List, Tuple, Dict
import numpy as np
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.collision_detection import CollisionDetection
from tdw.replicant.image_frequency import ImageFrequency
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.actions.action import Action
from tdw.wheelchair_replicant.wheel_values import WheelValues
from tdw.wheelchair_replicant.actions.wheelchair_motion import WheelchairMotion


class MoveBy(WheelchairMotion):
    """
    Move by a given distance by applying torques to the rear wheel motors.

    Stop moving by setting the motor torques to 0 and applying the brakes.

    The action can end for several reasons depending on the collision detection rules (see [`self.collision_detection`](../collision_detection.md).

    - If the Replicant moves the target distance, the action succeeds.
    - If `self.collision_detection.previous_was_same == True`, and the previous action was `MoveBy` or `MoveTo`, and it was in the same direction (forwards/backwards), and the previous action ended in failure, this action ends immediately.
    - If `self.collision_detection.avoid_obstacles == True` and the Replicant encounters a wall or object in its path:
      - If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
      - Otherwise, the action ends in failure.
    - If the Replicant collides with an object or a wall and `self.collision_detection.objects == True` and/or `self.collision_detection.walls == True` respectively:
      - If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
      - Otherwise, the action ends in failure.
    """

    def __init__(self, distance: float, wheel_values: WheelValues, dynamic: ReplicantDynamic,
                 collision_detection: CollisionDetection, previous: Optional[Action], reset_arms: bool,
                 reset_arms_duration: float, scale_reset_arms_duration: bool, arrived_at: float,
                 collision_avoidance_distance: float, collision_avoidance_half_extents: Dict[str, float]):
        """
        :param distance: The target distance. If less than 0, the Replicant will walk backwards.
        :param wheel_values: The [`WheelValues`](../wheel_values.md) that will be applied to the wheelchair's wheels.
        :param dynamic: The [`ReplicantDynamic`](../../replicant/replicant_dynamic.md) data that changes per `communicate()` call.
        :param collision_detection: The [`CollisionDetection`](../../replicant/collision_detection.md) rules.
        :param previous: The previous action, if any.
        :param reset_arms: If True, reset the arms to their neutral positions while beginning to move.
        :param reset_arms_duration: The speed at which the arms are reset in seconds.
        :param scale_reset_arms_duration: If True, `reset_arms_duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        :param arrived_at: If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful.
        :param collision_avoidance_distance: If `collision_detection.avoid == True`, an overlap will be cast at this distance from the Wheelchair Replicant to detect obstacles.
        :param collision_avoidance_half_extents: If `collision_detection.avoid == True`, an overlap will be cast with these half extents to detect obstacles.
        """

        """:field
        The target distance. If less than 0, the Replicant will move backwards.
        """
        self.distance: float = distance
        super().__init__(wheel_values=wheel_values, dynamic=dynamic, collision_detection=collision_detection, previous=previous,
                         reset_arms=reset_arms, reset_arms_duration=reset_arms_duration,
                         scale_reset_arms_duration=scale_reset_arms_duration, arrived_at=arrived_at,
                         collision_avoidance_distance=collision_avoidance_distance,
                         collision_avoidance_half_extents=collision_avoidance_half_extents)
        self._destination: np.ndarray = dynamic.transform.position + (dynamic.transform.forward * distance)
        # The initial position. This is used to determine the distance traversed. This is set in `get_initialization_commands()`.
        self._initial_position: np.ndarray = np.zeros(shape=3)
        # This will be updated per-frame.
        self._position: np.ndarray = np.zeros(shape=3)

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        self._initial_position = dynamic.transform.position
        self._position = dynamic.transform.position
        return super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                   image_frequency=image_frequency)

    def _get_distance(self, dynamic: ReplicantDynamic) -> Tuple[np.ndarray, np.ndarray]:
        """
        :param dynamic: The `ReplicantDynamic` data that changes per `communicate()` call.

        :return: Tuple: The distance to target, the distance traversed.
        """

        distance_to_target = np.linalg.norm(dynamic.transform.position - self._destination)
        distance_traversed = np.linalg.norm(dynamic.transform.position - self._initial_position)
        return distance_to_target, distance_traversed

    def _get_fail_status(self) -> ActionStatus:
        return ActionStatus.failed_to_move

    def _previous_was_collision(self, previous: Optional[Action]) -> bool:
        return self.collision_detection.previous_was_same and previous is not None and isinstance(previous, MoveBy) and \
               previous.status == ActionStatus.collision and np.sign(previous.distance) == np.sign(self.distance)

    def _is_success(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> bool:
        distance_to_target, distance_traversed = self._get_distance(dynamic=dynamic)
        return abs(distance_to_target) <= self.arrived_at

    def _is_time_to_brake(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> bool:
        distance_to_target, distance_traversed = self._get_distance(dynamic=dynamic)
        return distance_traversed >= self.wheel_values.brake_at or abs(distance_to_target) <= self.arrived_at

    def _get_overlap_direction(self, dynamic: ReplicantDynamic) -> np.ndarray:
        if self.distance > 0:
            overlap_z = self.collision_avoidance_distance
        else:
            overlap_z = -(self.collision_avoidance_distance * 0.75)
        return dynamic.transform.forward * overlap_z

    def _is_failure(self, dynamic: ReplicantDynamic) -> bool:
        return np.linalg.norm(dynamic.transform.position - self._position) < 0.0001

    def _continue_action(self, dynamic: ReplicantDynamic):
        self._position = dynamic.transform.position
