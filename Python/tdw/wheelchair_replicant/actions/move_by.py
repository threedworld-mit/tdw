from typing import Optional, List, Tuple
import numpy as np
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.collision_detection import CollisionDetection
from tdw.replicant.image_frequency import ImageFrequency
from tdw.replicant.actions.action import Action
from tdw.wheelchair_replicant.actions.wheelchair_motion import WheelchairMotion
from tdw.wheelchair_replicant.wheelchair_replicant_dynamic import WheelchairReplicantDynamic
from tdw.wheelchair_replicant.wheelchair_replicant_static import WheelchairReplicantStatic


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

    def __init__(self, distance: float, dynamic: WheelchairReplicantDynamic, collision_detection: CollisionDetection,
                 previous: Optional[Action], reset_arms: bool, reset_arms_duration: float,
                 scale_reset_arms_duration: bool, arrived_at: float, brake_at: float, brake_torque: float,
                 motor_torque: float):
        """
        :param dynamic: The [`WheelchairReplicantDynamic`](../wheelchair_replicant_dynamic.md) data that changes per `communicate()` call.
        :param collision_detection: The [`CollisionDetection`](../collision_detection.md) rules.
        :param previous: The previous action, if any.
        :param reset_arms: If True, reset the arms to their neutral positions while beginning to move.
        :param reset_arms_duration: The speed at which the arms are reset in seconds.
        :param scale_reset_arms_duration: If True, `reset_arms_duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        :param arrived_at: If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful.
        :param brake_at: Start to brake at this distance or angle.
        :param brake_torque: The torque that will be applied to the rear wheels at the end of the action.
        :param motor_torque: The torque that will be applied to the rear wheels at the start of the action.
        """

        """:field
        The target distance. If less than 0, the Replicant will move backwards.
        """
        self.distance: float = distance
        super().__init__(dynamic=dynamic, collision_detection=collision_detection, previous=previous,
                         reset_arms=reset_arms, reset_arms_duration=reset_arms_duration,
                         scale_reset_arms_duration=scale_reset_arms_duration, arrived_at=arrived_at, brake_at=brake_at,
                         brake_torque=brake_torque, left_motor_torque=motor_torque, right_motor_torque=motor_torque,
                         steer_angle=0)
        self._destination: np.ndarray = dynamic.transform.position + (dynamic.transform.forward * distance)
        # The initial position. This is used to determine the distance traversed. This is set in `get_initialization_commands()`.
        self._initial_position: np.ndarray = np.zeros(shape=3)

    def get_initialization_commands(self, resp: List[bytes],
                                    static: WheelchairReplicantStatic,
                                    dynamic: WheelchairReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        self._initial_position = dynamic.transform.position
        return super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                   image_frequency=image_frequency)

    def _get_distance(self, dynamic: WheelchairReplicantDynamic) -> Tuple[np.ndarray, np.ndarray]:
        """
        :param dynamic: The `WheelchairReplicantStatic` data that changes per `communicate()` call.

        :return: Tuple: The distance to target, the distance traversed.
        """

        distance_to_target = np.linalg.norm(dynamic.transform.position - self._destination)
        distance_traversed = np.linalg.norm(dynamic.transform.position - self._initial_position)
        return distance_to_target, distance_traversed

    def _previous_was_collision(self, previous: Optional[Action]) -> bool:
        return self.collision_detection.previous_was_same and previous is not None and isinstance(previous, MoveBy) and \
               previous.status == ActionStatus.collision and np.sign(previous.distance) == np.sign(self.distance)

    def _is_success(self, resp: List[bytes],
                    static: WheelchairReplicantStatic,
                    dynamic: WheelchairReplicantDynamic) -> bool:
        distance_to_target, distance_traversed = self._get_distance(dynamic=dynamic)
        return distance_to_target < self.arrived_at or distance_traversed > abs(self.distance) - self.arrived_at

    def _is_time_to_brake(self, resp: List[bytes],
                          static: WheelchairReplicantStatic,
                          dynamic: WheelchairReplicantDynamic) -> bool:
        distance_to_target, distance_traversed = self._get_distance(dynamic=dynamic)
        return distance_to_target < self.brake_torque or distance_traversed > abs(self.distance) - self.arrived_at

    def _get_overlap_direction(self, dynamic: WheelchairReplicantDynamic) -> np.ndarray:
        overlap_z = 0.5
        if self.distance < 0:
            overlap_z *= -1
        return dynamic.transform.forward * overlap_z
