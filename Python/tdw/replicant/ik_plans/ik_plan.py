from abc import ABC, abstractmethod
from typing import List, Optional
from overrides import final
from tdw.type_aliases import TARGET
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.actions.arm_motion import ArmMotion
from tdw.replicant.actions.action import Action
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.actions.reach_for import ReachFor
from tdw.replicant.collision_detection import CollisionDetection
from tdw.replicant.arm import Arm


class IkPlan(ABC):
    """
    An `IkPlan` takes the reach-for parameters and converts them into a list of actions.

    The parameters of `IkPlan` are similar to that of a `ReachFor` action, but an `IkPlan` is *not* an action.

    This is an abstract class. Subclasses of `IkPlan` define how the list of `ReachFor` actions is set.

    An `IkPlan` is used by the [`ReachForWithPlan`](../actions/reach_for_with_plan.md) action. (From the Replicant API, this is combined with the `reach_for(target, arm)` function).
    """

    def __init__(self, targets: List[TARGET], absolute: bool, arrived_at: float, max_distance: float, arms: List[Arm],
                 dynamic: ReplicantDynamic, collision_detection: CollisionDetection, previous: Optional[Action],
                 duration: float, scale_duration: bool, from_held: bool, held_point: str):
        """
        :param targets: The targets per arm. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        :param absolute: If True, the target position is in world space coordinates. If False, the target position is relative to the Replicant. Ignored if `target` is an int.
        :param arrived_at: If the final [`ReachFor`](../actions/reach_for.md) action ends and the hand is this distance or less from the target, the motion succeeds.
        :param max_distance: If at the start of the first [`ReachFor`](../actions/reach_for.md) action the target is further away than this distance from the hand, the action fails.
        :param arms: The [`Arm`](../arm.md)(s) that will reach for each target.
        :param dynamic: The [`ReplicantDynamic`](../replicant_dynamic.md) data that changes per `communicate()` call.
        :param collision_detection: The [`CollisionDetection`](../collision_detection.md) rules.
        :param previous: The previous action. Can be None.
        :param duration: The total duration of the motion in seconds. Each [`ReachFor`](../actions/reach_for.md) action is a fraction of this. For example, if there are 2 [`ReachFor`](../actions/reach_for.md) actions, then the duration of each of them is `duration / 2`.
        :param scale_duration: If True, `duration` will be multiplied by `framerate / 60`, ensuring smoother motions at faster-than-life simulation speeds.
        :param from_held: If False, the Replicant will try to move its hand to the `target`. If True, the Replicant will try to move its held object to the `target`. This is ignored if the hand isn't holding an object.
        :param held_point: The bounds point of the held object from which the offset will be calculated. Can be `"bottom"`, `"top"`, etc. For example, if this is `"bottom"`, the Replicant will move the bottom point of its held object to the `target`. This is ignored if `from_held == False` or ths hand isn't holding an object.
        """

        """:field
        The total duration of the motion in seconds. Each [`ReachFor`](../actions/reach_for.md) action is a fraction of this. For example, if there are 2 [`ReachFor`](../actions/reach_for.md) actions, then the duration of each of them is `duration / 2`.
        """
        self.duration: float = duration
        """:field
        If True, `duration` will be multiplied by `framerate / 60`, ensuring smoother motions at faster-than-life simulation speeds.
        """
        self.scale_duration: bool = scale_duration
        """:field
        The [`Arm`](../arm.md)(s) that will reach for each target.
        """
        self.arms: List[Arm] = arms
        """:field
        The [`CollisionDetection`](../collision_detection.md) rules.
        """
        self.collision_detection: CollisionDetection = collision_detection
        # Ignore collision detection for held items.
        self.__held_objects: List[int] = [v for v in dynamic.held_objects.values() if v not in self.collision_detection.exclude_objects]
        self.collision_detection.exclude_objects.extend(self.__held_objects)
        """:field
        The previous action. Can be None.
        """
        self.previous: Optional[Action] = previous
        # Immediately end the action if the previous action was the same motion and it ended with a collision.
        if self.collision_detection.previous_was_same and previous is not None and isinstance(previous, ArmMotion):
            for arm in arms:
                if arm in previous.collisions:
                    self.status = ActionStatus.collision
        """:field
         The targets per arm. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        """
        self.targets: List[TARGET] = targets
        """:field
        If True, the target position is in world space coordinates. If False, the target position is relative to the Replicant. Ignored if `target` is an int.
        """
        self.absolute: bool = absolute
        """:field
        If the final [`ReachFor`](../actions/reach_for.md) action ends and the hand is this distance or less from the target, the motion succeeds.
        """
        self.arrived_at: float = arrived_at
        """:field
        If at the start of the first [`ReachFor`](../actions/reach_for.md) action the target is further away than this distance from the hand, the action fails.
        """
        self.max_distance: float = max_distance
        """:field
        If False, the Replicant will try to move its hand to the `target`. If True, the Replicant will try to move its held object to the `target`.
        """
        self.from_held: bool = from_held
        """:field
        The bounds point of the held object from which the offset will be calculated. Can be `"bottom"`, `"top"`, etc. For example, if this is `"bottom"`, the Replicant will move the bottom point of its held object to the `target`. This is ignored if `from_held == False` or ths hand isn't holding an object.
        """
        self.held_point: str = held_point

    @abstractmethod
    def get_actions(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[Action]:
        """
        :param resp: The response from the build.
        :param static: The [`ReplicantStatic`](../replicant_static.md) data that doesn't change after the Replicant is initialized.
        :param dynamic: The [`ReplicantDynamic`](../replicant_dynamic.md) data that changes per `communicate()` call.

        :return: A list of [`Action`](../actions/action.md).
        """

        raise Exception()

    @final
    def _get_reach_for(self, targets: List[TARGET], arms: List[Arm], absolute: bool, duration: float,
                       dynamic: ReplicantDynamic, from_held: bool) -> ReachFor:
        """
        :param targets: The target per arm. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        :param arms: The arms.
        :param absolute: If True, the target position is in world space coordinates. If False, the target position is relative to the Replicant. Ignored if `target` is an int.
        :param duration: The duration in seconds of this `ReachFor` action (not the total duration of all sub-actions).
        :param dynamic: The `ReplicantDynamic` data that changes per `communicate()` call.
        :param from_held: If False, the Replicant will try to move its hand to the `target`. If True, the Replicant will try to move its held object to the `target`. This is ignored if the hand isn't holding an object.

        :return: A `ReachFor` action.
        """

        return ReachFor(targets=targets, absolute=absolute, offhand_follows=False, arrived_at=self.arrived_at,
                        max_distance=self.max_distance, arms=arms, dynamic=dynamic,
                        collision_detection=self.collision_detection, previous=self.previous, duration=duration,
                        from_held=from_held, held_point=self.held_point, scale_duration=self.scale_duration)
