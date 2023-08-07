from typing import Optional, List, Dict
import numpy as np
from tdw.type_aliases import TARGET
from tdw.tdw_utils import TDWUtils
from tdw.replicant.actions.action import Action
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.collision_detection import CollisionDetection
from tdw.replicant.image_frequency import ImageFrequency
from tdw.wheelchair_replicant.wheel_values import WheelValues, get_turn_values, get_default_values
from tdw.wheelchair_replicant.actions.turn_by import TurnBy


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

    def __init__(self, target: TARGET, wheel_values: Optional[WheelValues], dynamic: ReplicantDynamic,
                 collision_detection: CollisionDetection, previous: Optional[Action], reset_arms: bool,
                 reset_arms_duration: float, scale_reset_arms_duration: bool, arrived_at: float,
                 collision_avoidance_distance: float, collision_avoidance_half_extents: Dict[str, float]):
        """
        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        :param wheel_values: The [`WheelValues`](../wheel_values.md) that will be applied to the wheelchair's wheels. If None, values will be derived from `angle`.
        :param dynamic: The [`ReplicantDynamic`](../../replicant/replicant_dynamic.md) data that changes per `communicate()` call.
        :param collision_detection: The [`CollisionDetection`](../../replicant/collision_detection.md) rules.
        :param previous: The previous action, if any.
        :param reset_arms: If True, reset the arms to their neutral positions while beginning to move.
        :param reset_arms_duration: The speed at which the arms are reset in seconds.
        :param scale_reset_arms_duration: If True, `reset_arms_duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        :param arrived_at: If the angle between the traversed angle and the target angle is less than this threshold in degrees, the action succeeds.
        :param collision_avoidance_distance: If `collision_detection.avoid == True`, an overlap will be cast at this distance from the Wheelchair Replicant to detect obstacles.
        :param collision_avoidance_half_extents: If `collision_detection.avoid == True`, an overlap will be cast with these half extents to detect obstacles.
        """

        self._target: TARGET = target
        if wheel_values is None:
            wheel_values = get_default_values()
            self._need_to_set_wheel_parameters: bool = True
        else:
            self._need_to_set_wheel_parameters = False
        # We'll set the angle in `get_initialization_commands()`.
        super().__init__(angle=0, wheel_values=wheel_values, dynamic=dynamic, collision_detection=collision_detection,
                         previous=previous, reset_arms=reset_arms, reset_arms_duration=reset_arms_duration,
                         scale_reset_arms_duration=scale_reset_arms_duration, arrived_at=arrived_at,
                         collision_avoidance_distance=collision_avoidance_distance,
                         collision_avoidance_half_extents=collision_avoidance_half_extents)

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        target_position = self._get_target_array(target=self._target, resp=resp)
        # Set the target angle.
        v2 = target_position - dynamic.transform.position
        v2 = v2 / np.linalg.norm(v2)
        self.angle = TDWUtils.get_angle_between(v1=dynamic.transform.forward, v2=v2)
        if self.angle > 180:
            self.angle = -(360 - self.angle)
        # Set wheel parameters.
        if self._need_to_set_wheel_parameters:
            self.wheel_values = get_turn_values(angle=self.angle, arrived_at=self.arrived_at)
        return super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                   image_frequency=image_frequency)
