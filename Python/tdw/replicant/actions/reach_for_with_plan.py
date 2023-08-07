from typing import List, Optional
from tdw.type_aliases import TARGET
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.image_frequency import ImageFrequency
from tdw.replicant.actions.action import Action
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.actions.reach_for import ReachFor
from tdw.replicant.collision_detection import CollisionDetection
from tdw.replicant.arm import Arm
from tdw.replicant.ik_plans.ik_plan import IkPlan
from tdw.replicant.ik_plans.ik_plan_type import IkPlanType
from tdw.replicant.ik_plans.vertical_horizontal import VerticalHorizontal
from tdw.replicant.ik_plans.reset import Reset


class ReachForWithPlan(Action):
    """
    Reach for a target object or position.

    This is similar to [`ReachFor`](reach_for.md) but has the following differences:

    - There are multiple `ReachFor` sub-actions defined by an [`IkPlanType`](../ik_plans/ik_plan_type.md) value.
    - There is no option for an offhand to follow the hand to the target.

    `ReachForWithPlan` can be useful when the agent needs to maneuver its arm in a specific way, such as reaching above a surface and then forward.

    Within the [`Replicant`](../../add_ons/replicant.md), this action gets used by `reach_for(target, arm)` if the user sets the optional `plan` parameter.

    If target is an object, the target position is a point on the object.
    If the object has affordance points, the target position is the affordance point closest to the hand.
    Otherwise, the target position is the bounds position closest to the hand.

    The Replicant's arm(s) will continuously over multiple `communicate()` calls move until either the motion is complete or the arm collides with something (see `self.collision_detection`).

    - If the hand is near the target at the end of the action, the action succeeds.
    - If the target is too far away at the start of the action, the action fails.
    - The collision detection will respond normally to walls, objects, obstacle avoidance, etc.
    - If `self.collision_detection.previous_was_same == True`, and if the previous action was a subclass of `ArmMotion`, and it ended in a collision, this action ends immediately.

    See also: [`ReachFor`](reach_for.md).
    """

    def __init__(self, plan: IkPlanType, targets: List[TARGET], absolute: bool, arrived_at: float, max_distance: float,
                 arms: List[Arm], dynamic: ReplicantDynamic, collision_detection: CollisionDetection,
                 previous: Optional[Action], duration: float, scale_duration: bool, from_held: bool, held_point: str):
        """
        :param plan: An [`IkPlanType`](../ik_plans/ik_plan_type.md) that will define the [`IkPlan`](../ik_plans/ik_plan.md) this action will use.
        :param targets: The targets per arm. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        :param absolute: If True, the target position is in world space coordinates. If False, the target position is relative to the Replicant. Ignored if `target` is an int.
        :param arrived_at: If the final [`ReachFor`](../actions/reach_for.md) action ends and the hand is this distance or less from the target, the motion succeeds.
        :param max_distance: If at the start of the first [`ReachFor`](../actions/reach_for.md) action the target is further away than this distance from the hand, the action fails.
        :param arms: The [`Arm`](../arm.md)(s) that will reach for each target.
        :param dynamic: The [`ReplicantDynamic`](../replicant_dynamic.md) data that changes per `communicate()` call.
        :param collision_detection: The [`CollisionDetection`](../collision_detection.md) rules.
        :param previous: The previous action. Can be None.
        :param duration: The total duration of the motion in seconds. Each [`ReachFor`](../actions/reach_for.md) action is a fraction of this. For example, if there are 2 [`ReachFor`](../actions/reach_for.md) actions, then the duration of each of them is `duration / 2`.
        :param scale_duration: If True, `duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        :param from_held: If False, the Replicant will try to move its hand to the `target`. If True, the Replicant will try to move its held object to the `target`. This is ignored if the hand isn't holding an object.
        :param held_point: The bounds point of the held object from which the offset will be calculated. Can be `"bottom"`, `"top"`, etc. For example, if this is `"bottom"`, the Replicant will move the bottom point of its held object to the `target`. This is ignored if `from_held == False` or ths hand isn't holding an object.
        """

        super().__init__()
        if plan == IkPlanType.vertical_horizontal:
            ctor = VerticalHorizontal
        elif plan == IkPlanType.reset:
            ctor = Reset
        else:
            raise Exception(f"Undefined IK plan: {plan}")
        """:field
        The [`IkPlan`](../ik_plans/ik_plan.md) this action will use.
        """
        self.ik_plan: IkPlan = ctor(targets=targets, absolute=absolute, arrived_at=arrived_at, max_distance=max_distance,
                                    arms=arms, dynamic=dynamic, collision_detection=collision_detection,
                                    previous=previous, duration=duration, scale_duration=scale_duration,
                                    from_held=from_held, held_point=held_point)
        """:field
        A list of actions that will be filled in `get_initialization_commands()`.
        """
        self.actions: List[ReachFor] = list()
        """:field
        The index of the current action.
        """
        self.action_index: int = 0
        self._image_frequency: ImageFrequency = ImageFrequency.once

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        self._image_frequency = image_frequency
        # Get the actions.
        self.actions = self.ik_plan.get_actions(resp=resp, static=static, dynamic=dynamic)
        # Initialize the first action.
        return self._initialize_action(resp=resp, static=static, dynamic=dynamic)

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        commands = self.actions[self.action_index].get_ongoing_commands(resp=resp, static=static, dynamic=dynamic)
        status = self.actions[self.action_index].status
        if status == ActionStatus.success:
            # We're done!
            if self.action_index >= len(self.actions) - 1:
                self.status = ActionStatus.success
            # Initialize the next action.
            else:
                self.action_index += 1
                return self._initialize_action(resp=resp, static=static, dynamic=dynamic)
        # Something went wrong.
        elif status != ActionStatus.success:
            self.status = status
        return commands

    def get_end_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                         image_frequency: ImageFrequency) -> List[dict]:
        # End the last action.
        return self.actions[self.action_index].get_end_commands(resp=resp, static=static, dynamic=dynamic,
                                                                image_frequency=image_frequency)

    def _initialize_action(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        """
        :param resp: The response from the build.
        :param static: The `ReplicantStatic` data that doesn't change after the Replicant is initialized.
        :param dynamic: The `ReplicantDynamic` data that changes per `communicate()` call.

        :return: A list of commands to initialize the current action action.
        """

        # Initialize the action.
        commands = self.actions[self.action_index].get_initialization_commands(resp=resp,
                                                                               static=static,
                                                                               dynamic=dynamic,
                                                                               image_frequency=self._image_frequency)
        # Set my status.
        self.status = self.actions[self.action_index].status
        # Returns the commands of the action.
        return commands
