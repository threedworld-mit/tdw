from typing import Optional, List
import numpy as np
from tdw.type_aliases import TARGET
from tdw.tdw_utils import TDWUtils
from tdw.replicant.actions.action import Action
from tdw.replicant.collision_detection import CollisionDetection
from tdw.replicant.image_frequency import ImageFrequency
from tdw.wheelchair_replicant.wheel_parameters import get_turn_values
from tdw.wheelchair_replicant.actions.turn_by import TurnBy
from tdw.wheelchair_replicant.wheelchair_replicant_dynamic import WheelchairReplicantDynamic
from tdw.wheelchair_replicant.wheelchair_replicant_static import WheelchairReplicantStatic


class TurnTo(TurnBy):
    """
    Turn to a target object or position.

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

    def __init__(self, target: TARGET, dynamic: WheelchairReplicantDynamic, collision_detection: CollisionDetection,
                 previous: Optional[Action], reset_arms: bool, reset_arms_duration: float,
                 scale_reset_arms_duration: bool, arrived_at: float, brake_at: Optional[float],
                 brake_torque: Optional[float], left_motor_torque: Optional[float], right_motor_torque: Optional[float],
                 steer_angle: Optional[float]):
        """
        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        :param dynamic: The [`WheelchairReplicantDynamic`](../wheelchair_replicant_dynamic.md) data that changes per `communicate()` call.
        :param collision_detection: The [`CollisionDetection`](../../replicant/collision_detection.md) rules.
        :param previous: The previous action, if any.
        :param reset_arms: If True, reset the arms to their neutral positions while beginning to move.
        :param reset_arms_duration: The speed at which the arms are reset in seconds.
        :param scale_reset_arms_duration: If True, `reset_arms_duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        :param arrived_at: If the angle between the traversed angle and the target angle is less than this threshold in degrees, the action succeeds.
        :param brake_at: Start to brake at this angle.
        :param brake_torque: The torque that will be applied to the rear wheels at the end of the action.  If None, a default value derived from `angle` will be used.
        :param left_motor_torque: The torque that will be applied to the left rear wheel at the start of the action. If None, a default value derived from `angle` will be used.
        :param right_motor_torque: The torque that will be applied to the right rear wheel at the start of the action. If None, a default value derived from `angle` will be used.
        :param steer_angle: The steer angle in degrees that will applied to the front wheels at the start of the action. If None, a default value derived from `angle` will be used.
        """

        self._target: TARGET = target
        if brake_at is None or brake_torque is None or left_motor_torque is None or right_motor_torque is None or steer_angle is None:
            brake_at = 0
            brake_torque = 0
            left_motor_torque = 0
            right_motor_torque = 0
            steer_angle = 0
            self._need_to_set_wheel_parameters: bool = True
        else:
            self._need_to_set_wheel_parameters = False
        # We'll set the angle in `get_initialization_commands()`.
        super().__init__(angle=0, dynamic=dynamic, collision_detection=collision_detection, previous=previous,
                         reset_arms=reset_arms, reset_arms_duration=reset_arms_duration,
                         scale_reset_arms_duration=scale_reset_arms_duration, arrived_at=arrived_at, brake_at=brake_at,
                         brake_torque=brake_torque, left_motor_torque=left_motor_torque,
                         right_motor_torque=right_motor_torque, steer_angle=steer_angle)

    def get_initialization_commands(self, resp: List[bytes],
                                    static: WheelchairReplicantStatic,
                                    dynamic: WheelchairReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        # Get the target position.
        if isinstance(self._target, int):
            target_position = self._get_object_position(object_id=self._target, resp=resp)
        elif isinstance(self._target, dict):
            target_position = TDWUtils.vector3_to_array(self._target)
        elif isinstance(self._target, np.ndarray):
            target_position = self._target
        else:
            raise Exception(f"Invalid TurnTo target: {self._target}")
        # Set the target angle.
        v2 = target_position - dynamic.transform.position
        v2 = v2 / np.linalg.norm(v2)
        self.angle = TDWUtils.get_angle_between(v1=dynamic.transform.forward, v2=v2)
        # Set wheel parameters.
        if self._need_to_set_wheel_parameters:
            self.brake_at, self.brake_torque, self.left_motor_torque, self.right_motor_torque, self.steer_angle = get_turn_values(angle=self.angle)
        return super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                   image_frequency=image_frequency)
