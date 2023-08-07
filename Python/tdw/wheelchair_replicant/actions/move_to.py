from typing import Optional, List, Dict
import numpy as np
from tdw.type_aliases import TARGET
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.collision_detection import CollisionDetection
from tdw.replicant.image_frequency import ImageFrequency
from tdw.replicant.actions.action import Action
from tdw.wheelchair_replicant.wheel_values import WheelValues, get_move_values
from tdw.wheelchair_replicant.actions.turn_to import TurnTo
from tdw.wheelchair_replicant.actions.move_by import MoveBy


class MoveTo(Action):
    """
    Turn the wheelchair to a target position or object and then move to it.

    The action can end for several reasons depending on the collision detection rules (see [`self.collision_detection`](../collision_detection.md).

    - If the Replicant moves the target distance (i.e. it reaches its target), the action succeeds.
    - If `self.collision_detection.previous_was_same == True`, and the previous action was `MoveBy` or `MoveTo`, and it was in the same direction (forwards/backwards), and the previous action ended in failure, this action ends immediately.
    - If `self.collision_detection.avoid_obstacles == True` and the Replicant encounters a wall or object in its path:
      - If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
      - Otherwise, the action ends in failure.
    - If the Replicant collides with an object or a wall and `self.collision_detection.objects == True` and/or `self.collision_detection.walls == True` respectively:
      - If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
      - Otherwise, the action ends in failure.
    """

    def __init__(self, target: TARGET, turn_wheel_values: Optional[WheelValues],
                 move_wheel_values: Optional[WheelValues], dynamic: ReplicantDynamic,
                 collision_detection: CollisionDetection, previous: Optional[Action], reset_arms: bool,
                 reset_arms_duration: float, scale_reset_arms_duration: bool, aligned_at: float, arrived_at: float,
                 collision_avoidance_distance: float, collision_avoidance_half_extents: Dict[str, float]):
        """
        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        :param turn_wheel_values: The [`WheelValues`](../wheel_values.md) that will be applied to the wheelchair's wheels while it's turning. If None, values will be derived from the angle.
        :param move_wheel_values: The [`WheelValues`](../wheel_values.md) that will be applied to the wheelchair's wheels while it's moving. If None, values will be derived from the distance.
        :param dynamic: The [`ReplicantDynamic`](../../replicant/replicant_dynamic.md) data that changes per `communicate()` call.
        :param collision_detection: The [`CollisionDetection`](../../replicant/collision_detection.md) rules.
        :param previous: The previous action, if any.
        :param reset_arms: If True, reset the arms to their neutral positions while beginning to move.
        :param reset_arms_duration: The speed at which the arms are reset in seconds.
        :param scale_reset_arms_duration: If True, `reset_arms_duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        :param aligned_at: If the angle between the traversed angle and the target angle is less than this threshold in degrees, the action succeeds.
        :param arrived_at: If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful.
        :param collision_avoidance_distance: If `collision_detection.avoid == True`, an overlap will be cast at this distance from the Wheelchair Replicant to detect obstacles.
        :param collision_avoidance_half_extents: If `collision_detection.avoid == True`, an overlap will be cast with these half extents to detect obstacles.
        """

        super().__init__()
        """:field
        If True, the wheelchair is turning. If False, the wheelchair is moving.
        """
        self.turning: bool = True
        """:field
        The current sub-action. This is first a `TurnTo`, then a `MoveBy`.
        """
        self.action = TurnTo(target=target, wheel_values=turn_wheel_values, dynamic=dynamic,
                             collision_detection=collision_detection, previous=previous, reset_arms=reset_arms,
                             reset_arms_duration=reset_arms_duration,
                             scale_reset_arms_duration=scale_reset_arms_duration, arrived_at=aligned_at,
                             collision_avoidance_distance=collision_avoidance_distance,
                             collision_avoidance_half_extents=collision_avoidance_half_extents)
        self._target: TARGET = target
        self._image_frequency: ImageFrequency = ImageFrequency.once
        self._collision_detection: CollisionDetection = collision_detection
        """:field
        If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful.
        """
        self.arrived_at: float = arrived_at
        self._move_wheel_values: Optional[WheelValues] = move_wheel_values
        self._collision_avoidance_distance: float = collision_avoidance_distance
        self._collision_avoidance_half_extents: Dict[str, float] = collision_avoidance_half_extents

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        self._image_frequency = image_frequency
        return self.action.get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        commands = self.action.get_ongoing_commands(resp=resp, static=static, dynamic=dynamic)
        # The sub-action is ongoing.
        if self.action.status == ActionStatus.ongoing:
            return commands
        # The sub-action ended.
        else:
            # The sub-action succeeded.
            if self.action.status == ActionStatus.success:
                # We're done turning. Start moving.
                if self.turning:
                    self.turning = False
                    # Get the distance.
                    target_position = MoveBy._get_target_array(target=self._target, resp=resp)
                    distance = np.linalg.norm(dynamic.transform.position - target_position)
                    d0 = dynamic.transform.position + dynamic.transform.forward
                    d1 = dynamic.transform.position - dynamic.transform.forward
                    # Reverse the direction.
                    if np.linalg.norm(target_position - d1) < np.linalg.norm(target_position - d0):
                        distance *= -1
                    # Get wheel values.
                    if self._move_wheel_values is None:
                        self._move_wheel_values = get_move_values(distance)
                    self.action = MoveBy(distance=distance, wheel_values=self._move_wheel_values, dynamic=dynamic,
                                         collision_detection=self._collision_detection, previous=None,
                                         reset_arms=False, reset_arms_duration=0, scale_reset_arms_duration=False,
                                         arrived_at=self.arrived_at,
                                         collision_avoidance_distance=self._collision_avoidance_distance,
                                         collision_avoidance_half_extents=self._collision_avoidance_half_extents)
                    return self.action.get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                                   image_frequency=self._image_frequency)
                # We're done!
                else:
                    self.status = ActionStatus.success
            # The action failed.
            else:
                self.status = self.action.status
                return commands

    def get_end_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                         image_frequency: ImageFrequency) -> List[dict]:
        return self.action.get_end_commands(resp=resp, static=static, dynamic=dynamic, image_frequency=image_frequency)
