from typing import Optional, List, Dict
import numpy as np
from tdw.quaternion_utils import QuaternionUtils
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.actions.action import Action
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.collision_detection import CollisionDetection
from tdw.replicant.image_frequency import ImageFrequency
from tdw.wheelchair_replicant.wheel_values import WheelValues
from tdw.wheelchair_replicant.actions.wheelchair_motion import WheelchairMotion


class TurnBy(WheelchairMotion):
    """
    Turn by an angle.

    The wheelchair turns by applying motor torques to the rear wheels and a steer angle to the front wheels.

    Therefore, the wheelchair is not guaranteed to turn in place.

    The action can end for several reasons depending on the collision detection rules (see [`self.collision_detection`](../collision_detection.md).

    - If the Replicant turns by the target angle, the action succeeds.
    - If `self.collision_detection.previous_was_same == True`, and the previous action was `MoveBy` or `MoveTo`, and it was in the same direction (forwards/backwards), and the previous action ended in failure, this action ends immediately.
    - If `self.collision_detection.avoid_obstacles == True` and the Replicant encounters a wall or object in its path:
      - If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
      - Otherwise, the action ends in failure.
    - If the Replicant collides with an object or a wall and `self.collision_detection.objects == True` and/or `self.collision_detection.walls == True` respectively:
      - If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
      - Otherwise, the action ends in failure.
    """

    def __init__(self, angle: float, wheel_values: WheelValues, dynamic: ReplicantDynamic,
                 collision_detection: CollisionDetection, previous: Optional[Action], reset_arms: bool,
                 reset_arms_duration: float, scale_reset_arms_duration: bool, arrived_at: float,
                 collision_avoidance_distance: float, collision_avoidance_half_extents: Dict[str, float]):
        """
        :param angle: The angle in degrees.
        :param wheel_values: The [`WheelValues`](../wheel_values.md) that will be applied to the wheelchair's wheels.
        :param dynamic: The [`ReplicantDynamic`](../../replicant/replicant_dynamic.md) data that changes per `communicate()` call.
        :param collision_detection: The [`CollisionDetection`](../collision_detection.md) rules.
        :param previous: The previous action, if any.
        :param reset_arms: If True, reset the arms to their neutral positions while beginning to move.
        :param reset_arms_duration: The speed at which the arms are reset in seconds.
        :param scale_reset_arms_duration: If True, `reset_arms_duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        :param arrived_at: If the angle between the traversed angle and the target angle is less than this threshold in degrees, the action succeeds.
        :param collision_avoidance_distance: If `collision_detection.avoid == True`, an overlap will be cast at this distance from the Wheelchair Replicant to detect obstacles.
        :param collision_avoidance_half_extents: If `collision_detection.avoid == True`, an overlap will be cast with these half extents to detect obstacles.
        """

        """:field
        The target angle in degrees.
        """
        self.angle: float = TurnBy._clamp_angle(angle)
        # The initial forward directional vector of the Magnebot.
        self._initial_forward_vector: np.ndarray = np.zeros(3)
        # The initial yaw rotation.
        self._initial_rotation: float = 0
        # The current yaw rotation.
        self._rotation: float = 0
        super().__init__(wheel_values=wheel_values, dynamic=dynamic, collision_detection=collision_detection,
                         previous=previous, reset_arms=reset_arms, reset_arms_duration=reset_arms_duration,
                         scale_reset_arms_duration=scale_reset_arms_duration, arrived_at=arrived_at,
                         collision_avoidance_distance=collision_avoidance_distance,
                         collision_avoidance_half_extents=collision_avoidance_half_extents)

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        self._initial_forward_vector = dynamic.transform.forward.copy()
        self._initial_rotation = QuaternionUtils.quaternion_to_euler_angles(dynamic.transform.rotation)[1]
        self._initial_rotation = TurnBy._clamp_angle(self._initial_rotation)
        self._rotation = self._initial_rotation
        return super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                   image_frequency=image_frequency)

    def _get_delta_rotation(self, dynamic: ReplicantDynamic) -> float:
        """
        :param dynamic: The `WheelchairReplicantStatic` data that changes per `communicate()` call.

        :return: The change in rotation from the initial rotation to the current rotation.
        """

        rotation: float = QuaternionUtils.quaternion_to_euler_angles(dynamic.transform.rotation)[1]
        rotation = TurnBy._clamp_angle(rotation)
        return np.linalg.norm(self._initial_rotation - rotation) * np.sign(self.angle)

    def _get_fail_status(self) -> ActionStatus:
        return ActionStatus.failed_to_turn

    def _previous_was_collision(self, previous: Optional[Action]) -> bool:
        return self.collision_detection.previous_was_same and previous is not None and isinstance(previous, TurnBy) and \
               previous.status == ActionStatus.collision and np.sign(previous.angle) == np.sign(self.angle)

    def _is_success(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> bool:
        delta_rotation: float = self._get_delta_rotation(dynamic=dynamic)
        return (0 < self.angle < delta_rotation) or (0 > self.angle > -delta_rotation) or np.linalg.norm(self.angle - delta_rotation) < self.arrived_at

    def _is_time_to_brake(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> bool:
        delta_rotation: float = self._get_delta_rotation(dynamic=dynamic)
        return abs(delta_rotation) >= self.wheel_values.brake_at

    def _get_overlap_direction(self, dynamic: ReplicantDynamic) -> np.ndarray:
        overlap_d = self.collision_avoidance_distance * 0.625
        if self.angle < 0:
            overlap_d *= -1
        right = QuaternionUtils.multiply_by_vector(dynamic.transform.rotation, QuaternionUtils.RIGHT)
        return right * overlap_d

    def _is_failure(self, dynamic: ReplicantDynamic) -> bool:
        angle = TurnBy._clamp_angle(QuaternionUtils.quaternion_to_euler_angles(dynamic.transform.rotation)[1])
        return np.linalg.norm(angle - self._rotation) < 0.0001

    def _continue_action(self, dynamic: ReplicantDynamic):
        self._rotation = TurnBy._clamp_angle(QuaternionUtils.quaternion_to_euler_angles(dynamic.transform.rotation)[1])

    @staticmethod
    def _clamp_angle(angle: float) -> float:
        """
        :param angle: an angle.

        :return: The angle between -180 and 180 degrees.
        """

        if angle > 180:
            return -360 + angle
        elif angle < -180:
            return 360 - angle
        else:
            return angle

