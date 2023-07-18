from typing import List, Union
from tdw.controller import Controller
from tdw.librarian import HumanoidAnimationLibrarian
from tdw.type_aliases import TARGET
from tdw.add_ons.replicant_base import ReplicantBase
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.actions.turn_by import TurnBy
from tdw.replicant.actions.turn_to import TurnTo
from tdw.replicant.actions.move_by import MoveBy
from tdw.replicant.actions.move_to import MoveTo
from tdw.replicant.actions.reach_for import ReachFor
from tdw.replicant.actions.reach_for_with_plan import ReachForWithPlan
from tdw.replicant.actions.animate import Animate
from tdw.replicant.arm import Arm
from tdw.replicant.ik_plans.ik_plan_type import IkPlanType


class Replicant(ReplicantBase, ReplicantStatic, ReplicantDynamic):
    """
    A Replicant is an able-bodied human-like agent that can interact with the scene with pseudo-physics behavior.

    When a Replicant collides with objects, it initiates a physics-driven collision. The Replicant's own movements are driven by non-physics animation.

    A Replicant can walk, turn, reach for positions or objects, grasp and drop objects, and turn its head to look around.
    """

    """:class_var
    The Replicants library file. You can override this to use a custom library (e.g. a local library).
    """
    LIBRARY_NAME: str = "replicants.json"

    def get_initialization_commands(self) -> List[dict]:
        commands = super().get_initialization_commands()
        commands.insert(1, {"$type": "add_replicant_rigidbody",
                            "id": self.replicant_id})
        commands.insert(2, {"$type": "set_rigidbody_constraints",
                            "id": self.replicant_id,
                            "freeze_position_axes": {"x": 0, "y": 1, "z": 0}})
        # Add empty objects to the Replicant for relative IK motion targets.
        commands.extend([{"$type": "attach_empty_object",
                          "id": self.replicant_id,
                          "empty_object_id": arm.value,
                          "position": {"x": 0, "y": 0, "z": 0}} for arm in [Arm.left, Arm.right]])
        return commands

    def turn_by(self, angle: float) -> None:
        """
        Turn the Replicant by an angle.

        This is a non-animated action, meaning that the Replicant will immediately snap to the angle.

        :param angle: The target angle in degrees. Positive value = clockwise turn.
        """

        self.action = TurnBy(angle=angle)

    def turn_to(self, target: TARGET) -> None:
        """
        Turn the Replicant to face a target object or position.

        This is a non-animated action, meaning that the Replicant will immediately snap to the angle.

        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        """

        self.action = TurnTo(target=target)

    def move_by(self, distance: float, reset_arms: bool = True, reset_arms_duration: float = 0.25,
                scale_reset_arms_duration: bool = True, arrived_at: float = 0.1, animation: str = "walking_2",
                library: str = "humanoid_animations.json") -> None:
        """
        Walk a given distance.

        The Replicant will continuously play a walk cycle animation until the action ends.

        The action can end for several reasons depending on the collision detection rules (see [`self.collision_detection`](../replicant/collision_detection.md).

        - If the Replicant walks the target distance, the action succeeds.
        - If `collision_detection.previous_was_same == True`, and the previous action was `move_by()` or `move_to()`, and it was in the same direction (forwards/backwards), and the previous action ended in failure, this action ends immediately.
        - If `self.collision_detection.avoid_obstacles == True` and the Replicant encounters a wall or object in its path:
          - If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
          - Otherwise, the action ends in failure.
        - If the Replicant collides with an object or a wall and `self.collision_detection.objects == True` and/or `self.collision_detection.walls == True` respectively:
          - If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
          - Otherwise, the action ends in failure.

        :param distance: The target distance. If less than 0, the Replicant will walk backwards.
        :param reset_arms: If True, reset the arms to their neutral positions while beginning the walk cycle.
        :param reset_arms_duration: The speed at which the arms are reset in seconds.
        :param scale_reset_arms_duration: If True, `reset_arms_duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        :param arrived_at: If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful.
        :param animation: The name of the walk animation.
        :param library: The name of the walk animation's library.
        """

        self.action = MoveBy(distance=distance,
                             dynamic=self.dynamic,
                             collision_detection=self.collision_detection,
                             previous=self._previous_action,
                             reset_arms=reset_arms,
                             reset_arms_duration=reset_arms_duration,
                             scale_reset_arms_duration=scale_reset_arms_duration,
                             arrived_at=arrived_at,
                             animation=animation,
                             library=library,
                             collision_avoidance_distance=self._record.collision_avoidance_distance,
                             collision_avoidance_half_extents=self._record.collision_avoidance_half_extents)

    def move_to(self, target: TARGET, reset_arms: bool = True, reset_arms_duration: float = 0.25,
                scale_reset_arms_duration: bool = True, arrived_at: float = 0.1, bounds_position: str = "center",
                animation: str = "walking_2", library: str = "humanoid_animations.json") -> None:
        """
        Turn the Replicant to a target position or object and then walk to it.

        While walking, the Replicant will continuously play a walk cycle animation until the action ends.

        The action can end for several reasons depending on the collision detection rules (see [`self.collision_detection`](../replicant/collision_detection.md).

        - If the Replicant walks the target distance, the action succeeds.
        - If `collision_detection.previous_was_same == True`, and the previous action was `move_by()` or `move_to()`, and it was in the same direction (forwards/backwards), and the previous action ended in failure, this action ends immediately.
        - If `self.collision_detection.avoid_obstacles == True` and the Replicant encounters a wall or object in its path:
          - If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
          - Otherwise, the action ends in failure.
        - If the Replicant collides with an object or a wall and `self.collision_detection.objects == True` and/or `self.collision_detection.walls == True` respectively:
          - If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
          - Otherwise, the action ends in failure.

        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        :param reset_arms: If True, reset the arms to their neutral positions while beginning the walk cycle.
        :param reset_arms_duration: The speed at which the arms are reset in seconds.
        :param scale_reset_arms_duration: If True, `reset_arms_duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        :param arrived_at: If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful.
        :param bounds_position: If `target` is an integer object ID, move towards this bounds point of the object. Options: `"center"`, `"top`", `"bottom"`, `"left"`, `"right"`, `"front"`, `"back"`.
        :param animation: The name of the walk animation.
        :param library: The name of the walk animation's library.
        """

        self.action = MoveTo(target=target,
                             collision_detection=self.collision_detection,
                             previous=self._previous_action,
                             reset_arms=reset_arms,
                             reset_arms_duration=reset_arms_duration,
                             scale_reset_arms_duration=scale_reset_arms_duration,
                             arrived_at=arrived_at,
                             bounds_position=bounds_position,
                             animation=animation,
                             library=library,
                             collision_avoidance_distance=self._record.collision_avoidance_distance,
                             collision_avoidance_half_extents=self._record.collision_avoidance_half_extents)

    def reach_for(self, target: Union[TARGET, List[TARGET]], arm: Union[Arm, List[Arm]], absolute: bool = True,
                  offhand_follows: bool = False, arrived_at: float = 0.09, max_distance: float = 1.5,
                  duration: float = 0.25, scale_duration: bool = True, from_held: bool = False,
                  held_point: str = "bottom", plan: IkPlanType = None) -> None:
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
        :param plan: An optional [`IkPlanType`](../replicant/ik_plans/ik_plan_type.md) that splits this action into multiple sub-actions. If None, there is a single `ReachFor` action. If `arm` is a list, only the first element is used. `offhand_follows` is ignored. `duration` is divided by the number of sub-actions.
        """

        if isinstance(target, list):
            targets = target
        else:
            targets = [target]
        if plan is None:
            self.action = ReachFor(targets=targets,
                                   arms=Replicant._arms_to_list(arm),
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
        else:
            self.action = ReachForWithPlan(targets=targets,
                                           arms=Replicant._arms_to_list(arm),
                                           absolute=absolute,
                                           dynamic=self.dynamic,
                                           collision_detection=self.collision_detection,
                                           arrived_at=arrived_at,
                                           previous=self._previous_action,
                                           duration=duration,
                                           scale_duration=scale_duration,
                                           max_distance=max_distance,
                                           from_held=from_held,
                                           held_point=held_point,
                                           plan=plan)

    def animate(self, animation: str, library: str = "humanoid_animations.json", loop: bool = None) -> None:
        """
        Play an animation.

        The animation will end either when the animation clip is finished or if the Replicant collides with something (see [`self.collision_detection`](../replicant/collision_detection.md)).

        - The collision detection will respond normally to walls, objects, obstacle avoidance, etc.
        - If `self.collision_detection.previous_was_same == True`, and it was the same animation, and it ended in a collision, this action ends immediately.

        :param animation: The name of the animation.
        :param library: The animation library.
        :param loop: If None, the animation will loop if this is a looping animation (see `HumanoidAnimationRecord.loop`); this is almost always what you want the animation to do. If True, the animation will continuously loop and the action will continue until interrupted. If False, the action ends when the animation ends.
        """

        if loop is None:
            # Add the library.
            if library not in Controller.HUMANOID_ANIMATION_LIBRARIANS:
                Controller.HUMANOID_ANIMATION_LIBRARIANS[library] = HumanoidAnimationLibrarian(library)
            # Get the record.
            record = Controller.HUMANOID_ANIMATION_LIBRARIANS[library].get_record(animation)
            # Get the loop value.
            loop = record.loop

        self.action = Animate(animation=animation,
                              collision_detection=self.collision_detection,
                              forward=True,
                              library=library,
                              previous=self._previous_action,
                              ik_body_parts=[],
                              loop=loop)

    def _get_library_name(self) -> str:
        return Replicant.LIBRARY_NAME

    def _get_add_replicant_command(self) -> str:
        return "add_replicant"

    def _get_send_replicants_command(self) -> str:
        return "send_replicants"

    def _can_walk(self) -> bool:
        return True
