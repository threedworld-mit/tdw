from typing import List, Optional, Union
from tdw.type_aliases import TARGET, POSITION, ROTATION
from tdw.add_ons.replicant_base import ReplicantBase
from tdw.replicant.arm import Arm
from tdw.replicant.image_frequency import ImageFrequency
from tdw.wheelchair_replicant.wheel_values import WheelValues, get_turn_values, get_move_values
from tdw.wheelchair_replicant.actions.turn_by import TurnBy
from tdw.wheelchair_replicant.actions.turn_to import TurnTo
from tdw.wheelchair_replicant.actions.move_by import MoveBy
from tdw.wheelchair_replicant.actions.move_to import MoveTo
from tdw.wheelchair_replicant.actions.reach_for import ReachFor


class WheelchairReplicant(ReplicantBase):
    """
    A WheelchairReplicant is a wheelchair-bound human-like agent that can interact with the scene with pseudo-physics behavior.
    """

    """:class_var
    The WheelchairReplicants library file. You can override this to use a custom library (e.g. a local library).
    """
    LIBRARY_NAME: str = "wheelchair_replicants.json"

    def __init__(self, replicant_id: int = 0, position: POSITION = None, rotation: ROTATION = None,
                 image_frequency: ImageFrequency = ImageFrequency.once, name: str = "man_casual",
                 target_framerate: int = 100):
        """
        :param replicant_id: The ID of the Replicant.
        :param position: The position of the Replicant as an x, y, z dictionary or numpy array. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param rotation: The rotation of the Replicant in Euler angles (degrees) as an x, y, z dictionary or numpy array. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param image_frequency: An [`ImageFrequency`](../replicant/image_frequency.md) value that sets how often images are captured.
        :param name: The name of the Replicant model.
        :param target_framerate: The target framerate. It's possible to set a higher target framerate, but doing so can lead to a loss of precision in agent movement.
        """

        super().__init__(replicant_id=replicant_id, position=position, rotation=rotation,
                         image_frequency=image_frequency, name=name, target_framerate=target_framerate)

    def turn_by(self, angle: float, wheel_values: WheelValues = None, reset_arms: bool = True,
                reset_arms_duration: float = 0.25, scale_reset_arms_duration: bool = True, arrived_at: float = 1):
        """
        Turn by an angle.

        The wheelchair turns by applying motor torques to the rear wheels and a steer angle to the front wheels.

        Therefore, the wheelchair is not guaranteed to turn in place.

        The action can end for several reasons depending on the collision detection rules (see [`self.collision_detection`](../replicant/collision_detection.md).

        - If the Replicant turns by the target angle, the action succeeds.
        - If `self.collision_detection.previous_was_same == True`, and the previous action was `MoveBy` or `MoveTo`, and it was in the same direction (forwards/backwards), and the previous action ended in failure, this action ends immediately.
        - If `self.collision_detection.avoid_obstacles == True` and the Replicant encounters a wall or object in its path:
          - If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
          - Otherwise, the action ends in failure.
        - If the Replicant collides with an object or a wall and `self.collision_detection.objects == True` and/or `self.collision_detection.walls == True` respectively:
          - If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
          - Otherwise, the action ends in failure.

        :param angle: The angle in degrees.
        :param wheel_values: The [`WheelValues`](../wheelchair_replicant/wheel_values.md) that will be applied to the wheelchair's wheels. If None, values will be derived from `angle`.
        :param reset_arms: If True, reset the arms to their neutral positions while beginning to move.
        :param reset_arms_duration: The speed at which the arms are reset in seconds.
        :param scale_reset_arms_duration: If True, `reset_arms_duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        :param arrived_at: If the angle between the traversed angle and the target angle is less than this threshold in degrees, the action succeeds.
        """

        # Derive wheel parameters from the angle.
        if wheel_values is None:
            wheel_values = get_turn_values(angle=angle, arrived_at=arrived_at)
        self.action = TurnBy(angle=angle, wheel_values=wheel_values, dynamic=self.dynamic,
                             collision_detection=self.collision_detection, previous=self._previous_action,
                             reset_arms=reset_arms, reset_arms_duration=reset_arms_duration,
                             scale_reset_arms_duration=scale_reset_arms_duration, arrived_at=arrived_at,
                             collision_avoidance_distance=self._record.collision_avoidance_distance,
                             collision_avoidance_half_extents=self._record.collision_avoidance_half_extents)

    def turn_to(self, target: TARGET, wheel_values: WheelValues = None, reset_arms: bool = True,
                reset_arms_duration: float = 0.25, scale_reset_arms_duration: bool = True, arrived_at: float = 1):
        """
        Turn to a target object or position.

        The wheelchair turns by applying motor torques to the rear wheels and a steer angle to the front wheels.

        Therefore, the wheelchair is not guaranteed to turn in place.

        The action can end for several reasons depending on the collision detection rules (see [`self.collision_detection`](../replicant/collision_detection.md).

        - If the Replicant turns by the target angle, the action succeeds.
        - If `self.collision_detection.previous_was_same == True`, and the previous action was `MoveBy` or `MoveTo`, and it was in the same direction (forwards/backwards), and the previous action ended in failure, this action ends immediately.
        - If `self.collision_detection.avoid_obstacles == True` and the Replicant encounters a wall or object in its path:
          - If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
          - Otherwise, the action ends in failure.
        - If the Replicant collides with an object or a wall and `self.collision_detection.objects == True` and/or `self.collision_detection.walls == True` respectively:
          - If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
          - Otherwise, the action ends in failure.

        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        :param wheel_values: The [`WheelValues`](../wheelchair_replicant/wheel_values.md) that will be applied to the wheelchair's wheels. If None, values will be derived from `angle`.
        :param reset_arms: If True, reset the arms to their neutral positions while beginning to move.
        :param reset_arms_duration: The speed at which the arms are reset in seconds.
        :param scale_reset_arms_duration: If True, `reset_arms_duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        :param arrived_at: If the angle between the traversed angle and the target angle is less than this threshold in degrees, the action succeeds.
        """

        # If `wheel_values` is None, the `TurnTo` will set it.
        # It needs to be this way because we don't know the angle if `target` is an object ID.
        self.action = TurnTo(target=target, wheel_values=wheel_values, dynamic=self.dynamic,
                             collision_detection=self.collision_detection, previous=self._previous_action,
                             reset_arms=reset_arms, reset_arms_duration=reset_arms_duration,
                             scale_reset_arms_duration=scale_reset_arms_duration, arrived_at=arrived_at,
                             collision_avoidance_distance=self._record.collision_avoidance_distance,
                             collision_avoidance_half_extents=self._record.collision_avoidance_half_extents)

    def move_by(self, distance: float, wheel_values: WheelValues = None, reset_arms: bool = True,
                reset_arms_duration: float = 0.25, scale_reset_arms_duration: bool = True, arrived_at: float = 0.1):
        """
        Move by a given distance by applying torques to the rear wheel motors.

        Stop moving by setting the motor torques to 0 and applying the brakes.

        The action can end for several reasons depending on the collision detection rules (see [`self.collision_detection`](../replicant/collision_detection.md).

        - If the Replicant moves the target distance, the action succeeds.
        - If `self.collision_detection.previous_was_same == True`, and the previous action was `MoveBy` or `MoveTo`, and it was in the same direction (forwards/backwards), and the previous action ended in failure, this action ends immediately.
        - If `self.collision_detection.avoid_obstacles == True` and the Replicant encounters a wall or object in its path:
          - If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
          - Otherwise, the action ends in failure.
        - If the Replicant collides with an object or a wall and `self.collision_detection.objects == True` and/or `self.collision_detection.walls == True` respectively:
          - If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
          - Otherwise, the action ends in failure.

        :param distance: The target distance. If less than 0, the Replicant will move backwards.
        :param wheel_values: The [`WheelValues`](../wheelchair_replicant/wheel_values.md) that will be applied to the wheelchair's wheels. If None, values will be derived from `angle`.
        :param reset_arms: If True, reset the arms to their neutral positions while beginning to move.
        :param reset_arms_duration: The speed at which the arms are reset in seconds.
        :param scale_reset_arms_duration: If True, `reset_arms_duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        :param arrived_at: If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful.
        """

        if wheel_values is None:
            wheel_values = get_move_values(distance)
        self.action = MoveBy(distance=distance, wheel_values=wheel_values, dynamic=self.dynamic,
                             collision_detection=self.collision_detection, previous=self._previous_action,
                             reset_arms=reset_arms, reset_arms_duration=reset_arms_duration,
                             scale_reset_arms_duration=scale_reset_arms_duration, arrived_at=arrived_at,
                             collision_avoidance_distance=self._record.collision_avoidance_distance,
                             collision_avoidance_half_extents=self._record.collision_avoidance_half_extents)

    def move_to(self, target: TARGET, turn_wheel_values: Optional[WheelValues] = None,
                move_wheel_values: Optional[WheelValues] = None, reset_arms: bool = True,
                reset_arms_duration: float = 0.25, scale_reset_arms_duration: bool = True, aligned_at: float = 1,
                arrived_at: float = 0.5):
        """
        Turn the wheelchair to a target position or object and then move to it.

        The action can end for several reasons depending on the collision detection rules (see [`self.collision_detection`](../replicant/collision_detection.md).

        - If the Replicant moves the target distance (i.e. it reaches its target), the action succeeds.
        - If `self.collision_detection.previous_was_same == True`, and the previous action was `MoveBy` or `MoveTo`, and it was in the same direction (forwards/backwards), and the previous action ended in failure, this action ends immediately.
        - If `self.collision_detection.avoid_obstacles == True` and the Replicant encounters a wall or object in its path:
          - If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
          - Otherwise, the action ends in failure.
        - If the Replicant collides with an object or a wall and `self.collision_detection.objects == True` and/or `self.collision_detection.walls == True` respectively:
          - If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
          - Otherwise, the action ends in failure.

        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        :param turn_wheel_values: The [`WheelValues`](../wheelchair_replicant/wheel_values.md) that will be applied to the wheelchair's wheels while it's turning. If None, values will be derived from the angle.
        :param move_wheel_values: The [`WheelValues`](../wheelchair_replicant/wheel_values.md) that will be applied to the wheelchair's wheels while it's moving. If None, values will be derived from the distance.
        :param reset_arms: If True, reset the arms to their neutral positions while beginning to move.
        :param reset_arms_duration: The speed at which the arms are reset in seconds.
        :param scale_reset_arms_duration: If True, `reset_arms_duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        :param aligned_at: If the angle between the traversed angle and the target angle is less than this threshold in degrees, the action succeeds.
        :param arrived_at: If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful.
        """

        self.action = MoveTo(target=target, turn_wheel_values=turn_wheel_values, move_wheel_values=move_wheel_values,
                             dynamic=self.dynamic, collision_detection=self.collision_detection,
                             previous=self._previous_action, reset_arms=reset_arms,
                             reset_arms_duration=reset_arms_duration,
                             scale_reset_arms_duration=scale_reset_arms_duration, aligned_at=aligned_at,
                             arrived_at=arrived_at,
                             collision_avoidance_distance=self._record.collision_avoidance_distance,
                             collision_avoidance_half_extents=self._record.collision_avoidance_half_extents)

    def reach_for(self, target: Union[TARGET, List[TARGET]], arm: Union[Arm, List[Arm]], absolute: bool = True,
                  offhand_follows: bool = False, arrived_at: float = 0.09, max_distance: float = 1.5,
                  duration: float = 0.25, scale_duration: bool = True, from_held: bool = False,
                  held_point: str = "bottom") -> None:
        """
        Reach for a target object or position. One or both hands can reach for the same or separate targets.

        If target is an object, the target position is a point on the object.
        If the object has affordance points, the target position is the affordance point closest to the hand.
        Otherwise, the target position is the bounds position closest to the hand.

        The Replicant's arm(s) will continuously over multiple `communicate()` calls move until either the motion is complete or the arm collides with something (see `self.collision_detection`).

        - If the hand is near the target at the end of the action, the action succeeds.
        - If the target is too far away at the start of the action, the action fails.
        - The collision detection will respond normally to walls, objects, obstacle avoidance, etc.
        - If `self.collision_detection.previous_was_same == True`, and if the previous action was a subclass of `ArmMotion`, and it ended in a collision, this action ends immediately.

        Unlike [`Replicant`](replicant.md), this action doesn't support [IK plans](../replicant/ik_plans/ik_plan_type.md).

        :param target: The target(s). This can be a list (one target per hand) or a single value (the hand's target). If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        :param arm: The [`Arm`](../replicant/arm.md) value(s) that will reach for each target as a single value or a list. Example: `Arm.left` or `[Arm.left, Arm.right]`.
        :param absolute: If True, the target position is in world space coordinates. If False, the target position is relative to the Replicant. Ignored if `target` is an int.
        :param offhand_follows: If True, the offhand will follow the primary hand, meaning that it will maintain the same relative position. Ignored if `arm` is a list or `target` is an int.
        :param arrived_at: If at the end of the action the hand(s) is this distance or less from the target position, the action succeeds.
        :param max_distance: The maximum distance from the hand to the target position.
        :param duration: The duration of the motion in seconds.
        :param scale_duration: If True, `duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        :param from_held: If False, the Replicant will try to move its hand to the `target`. If True, the Replicant will try to move its held object to the `target`. This is ignored if the hand isn't holding an object.
        :param held_point: The bounds point of the held object from which the offset will be calculated. Can be `"bottom"`, `"top"`, etc. For example, if this is `"bottom"`, the Replicant will move the bottom point of its held object to the `target`. This is ignored if `from_held == False` or ths hand isn't holding an object.
        """

        if isinstance(target, list):
            targets = target
        else:
            targets = [target]
        self.action = ReachFor(targets=targets,
                               arms=WheelchairReplicant._arms_to_list(arm),
                               absolute=absolute,
                               dynamic=self.dynamic,
                               collision_detection=self.collision_detection,
                               offhand_follows=offhand_follows,
                               arrived_at=arrived_at,
                               previous=self._previous_action,
                               duration=duration,
                               scale_duration=scale_duration,
                               max_distance=max_distance,
                               from_held=from_held,
                               held_point=held_point)

    def _get_library_name(self) -> str:
        return WheelchairReplicant.LIBRARY_NAME

    def _get_add_replicant_command(self) -> str:
        return "add_wheelchair_replicant"

    def _get_send_replicants_command(self) -> str:
        return "send_wheelchair_replicants"

    def _can_walk(self) -> bool:
        return False
