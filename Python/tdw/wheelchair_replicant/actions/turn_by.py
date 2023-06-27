from typing import Optional, List
import numpy as np
from tdw.quaternion_utils import QuaternionUtils
from tdw.replicant.actions.action import Action
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.collision_detection import CollisionDetection
from tdw.replicant.image_frequency import ImageFrequency
from tdw.wheelchair_replicant.wheel_values import WheelValues
from tdw.wheelchair_replicant.actions.wheelchair_motion import WheelchairMotion
from tdw.wheelchair_replicant.wheelchair_replicant_dynamic import WheelchairReplicantDynamic
from tdw.wheelchair_replicant.wheelchair_replicant_static import WheelchairReplicantStatic


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

    def __init__(self, angle: float, wheel_values: WheelValues, dynamic: WheelchairReplicantDynamic,
                 collision_detection: CollisionDetection, previous: Optional[Action], reset_arms: bool,
                 reset_arms_duration: float, scale_reset_arms_duration: bool, arrived_at: float):
        """
        :param angle: The angle in degrees.
        :param wheel_values: The [`WheelValues`](../wheel_values.md) that will be applied to the wheelchair's wheels.
        :param dynamic: The [`WheelchairReplicantDynamic`](../wheelchair_replicant_dynamic.md) data that changes per `communicate()` call.
        :param collision_detection: The [`CollisionDetection`](../collision_detection.md) rules.
        :param previous: The previous action, if any.
        :param reset_arms: If True, reset the arms to their neutral positions while beginning to move.
        :param reset_arms_duration: The speed at which the arms are reset in seconds.
        :param scale_reset_arms_duration: If True, `reset_arms_duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        :param arrived_at: If the angle between the traversed angle and the target angle is less than this threshold in degrees, the action succeeds.
        """

        """:field
        The target angle in degrees.
        """
        self.angle: float = angle
        # Clamp the angle.
        if np.abs(self.angle) > 180:
            if self.angle > 0:
                self.angle -= 360
            else:
                self.angle += 360
        # The initial forward directional vector of the Magnebot.
        self._initial_forward_vector: np.ndarray = np.zeros(3)
        # The initial yaw rotation.
        self._initial_rotation: float = 0
        super().__init__(wheel_values=wheel_values, dynamic=dynamic, collision_detection=collision_detection,
                         previous=previous, reset_arms=reset_arms, reset_arms_duration=reset_arms_duration,
                         scale_reset_arms_duration=scale_reset_arms_duration, arrived_at=arrived_at)

    def get_initialization_commands(self, resp: List[bytes],
                                    static: WheelchairReplicantStatic,
                                    dynamic: WheelchairReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        self._initial_forward_vector = dynamic.transform.forward.copy()
        self._initial_rotation = QuaternionUtils.quaternion_to_euler_angles(dynamic.transform.rotation)[1]
        return super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                   image_frequency=image_frequency)

    def _get_delta_rotation(self, dynamic: WheelchairReplicantDynamic) -> float:
        """
        :param dynamic: The `WheelchairReplicantStatic` data that changes per `communicate()` call.

        :return: The change in rotation from the initial rotation to the current rotation.
        """

        rotation: float = QuaternionUtils.quaternion_to_euler_angles(dynamic.transform.rotation)[1]
        return np.linalg.norm(self._initial_rotation - rotation)

    def _previous_was_collision(self, previous: Optional[Action]) -> bool:
        return self.collision_detection.previous_was_same and previous is not None and isinstance(previous, TurnBy) and \
               previous.status == ActionStatus.collision and np.sign(previous.angle) == np.sign(self.angle)

    def _is_success(self, resp: List[bytes],
                    static: WheelchairReplicantStatic,
                    dynamic: WheelchairReplicantDynamic) -> bool:
        delta_rotation: float = self._get_delta_rotation(dynamic=dynamic)
        return (0 < self.angle < delta_rotation) or (0 > self.angle > -delta_rotation) or np.linalg.norm(self.angle - delta_rotation) < self.arrived_at

    def _is_time_to_brake(self, resp: List[bytes],
                          static: WheelchairReplicantStatic,
                          dynamic: WheelchairReplicantDynamic) -> bool:
        delta_rotation: float = self._get_delta_rotation(dynamic=dynamic)
        return abs(delta_rotation) < self.wheel_values.brake_at

    def _get_overlap_direction(self, dynamic: WheelchairReplicantDynamic) -> np.ndarray:
        overlap_d = 0.5
        if self.angle < 0:
            overlap_d *= -1
        right = QuaternionUtils.multiply_by_vector(dynamic.transform.rotation, QuaternionUtils.RIGHT)
        return right * overlap_d
