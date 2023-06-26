from typing import List, Optional, Dict, Union
from copy import deepcopy
import numpy as np
from tdw.type_aliases import TARGET, POSITION, ROTATION
from tdw.add_ons.replicant_base import ReplicantBase
from tdw.wheelchair_replicant.wheelchair_replicant_static import WheelchairReplicantStatic
from tdw.wheelchair_replicant.wheelchair_replicant_dynamic import WheelchairReplicantDynamic
from tdw.replicant.collision_detection import CollisionDetection
from tdw.replicant.actions.action import Action
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.image_frequency import ImageFrequency
from tdw.replicant.arm import Arm
from tdw.librarian import HumanoidRecord, HumanoidLibrarian
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.wheelchair_replicant.actions.move_by import MoveBy
from tdw.wheelchair_replicant.actions.reset_arm import ResetArm
from tdw.wheelchair_replicant.actions.reach_for import ReachFor


"""
TODO:

turn_by
turn_to
move_to
"""


class WheelchairReplicant(ReplicantBase, WheelchairReplicantDynamic, WheelchairReplicantStatic):
    """
    A WheelchairReplicant is an wheelchairbound human-like agent that can interact with the scene with pseudo-physics behavior.
    """

    """:class_var
    The WheelchairReplicants library file. You can override this to use a custom library (e.g. a local library).
    """
    LIBRARY_NAME: str = "wheelchair_replicants.json"

    def get_initialization_commands(self) -> List[dict]:
        """
        This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

        :return: A list of commands that will initialize this add-on.
        """

        commands = super().get_initialization_commands()
        commands.append({"$type": "send_wheelchairs",
                         "frequency": "always"})
        return commands

    def move_by(self, distance: float, reset_arms: bool = True, reset_arms_duration: float = 0.25,
                scale_reset_arms_duration: bool = True, arrived_at: float = 0.1, brake_at: float = None,
                motor_torque: float = None, brake_torque: float = None):
        """
        Apply torque to the rear wheels to move by a given distance.

        The action can end for several reasons depending on the collision detection rules (see [`self.collision_detection`](../replicant/collision_detection.md).

        :param distance: The target distance. If less than 0, the Replicant will move backwards.
        :param reset_arms: If True, reset the arms to their neutral positions while beginning to move.
        :param reset_arms_duration: The speed at which the arms are reset in seconds.
        :param scale_reset_arms_duration: If True, `reset_arms_duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        :param arrived_at: If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful.
        :param brake_at: Start to brake at this distance in meters from the target. If None, a default value derived from `distance` will be used.
        :param motor_torque: The torque that will be applied to the rear wheels at the start of the action. If None, a default value derived from `distance` will be used.
        :param brake_torque: The torque that will be applied to the rear wheels at the end of the action. If None, a default value derived from `distance` will be used.
        """

        if brake_at is None or motor_torque is None or brake_torque is None:
            brake_at, motor_torque, brake_torque = WheelchairReplicant._get_wheel_move_parameters(distance)
        self.action = MoveBy(distance=distance, dynamic=self.dynamic, collision_detection=self.collision_detection,
                             previous=self._previous_action, reset_arms=reset_arms,
                             reset_arms_duration=reset_arms_duration,
                             scale_reset_arms_duration=scale_reset_arms_duration, arrived_at=arrived_at,
                             brake_at=brake_at, motor_torque=motor_torque, brake_torque=brake_torque)

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

    def reset_arm(self, arm: Union[Arm, List[Arm]], duration: float = 0.25, scale_duration: bool = True) -> None:
        """
        Move arm(s) back to rest position(s). One or both arms can be reset at the same time.

        The Replicant's arm(s) will continuously over multiple `communicate()` calls move until either the motion is complete or the arm collides with something (see `self.collision_detection`).

        - The collision detection will respond normally to walls, objects, obstacle avoidance, etc.
        - If `self.collision_detection.previous_was_same == True`, and if the previous action was an arm motion, and it ended in a collision, this action ends immediately.

        :param arm: The [`Arm`](../replicant/arm.md) value(s) that will reach for the `target` as a single value or a list. Example: `Arm.left` or `[Arm.left, Arm.right]`.
        :param duration: The duration of the motion in seconds.
        :param scale_duration: If True, `duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        """

        self.action = ResetArm(arms=WheelchairReplicant._arms_to_list(arm),
                               dynamic=self.dynamic,
                               collision_detection=self.collision_detection,
                               previous=self._previous_action,
                               duration=duration,
                               scale_duration=scale_duration)

    def _set_dynamic_data(self, resp: List[bytes]) -> None:
        """
        Set dynamic data.

        :param resp: The response from the build.
        """

        self.dynamic = WheelchairReplicantDynamic(resp=resp, replicant_id=self.replicant_id, frame_count=self._frame_count)
        if self.dynamic.got_images:
            self._frame_count += 1

    def _get_library_name(self) -> str:
        return WheelchairReplicant.LIBRARY_NAME

    def _get_add_replicant_command(self) -> str:
        return "add_wheelchair_replicant"

    def _get_send_replicants_command(self) -> str:
        return "send_wheelchair_replicants"

    @staticmethod
    def _get_wheel_move_parameters(distance: float) -> (float, float, float):
        """
        :param distance: The target distance.

        :return: Wheel parameters derived from the distance.
        """

        d = abs(distance)
        brake_at = distance * 0.9
        if d < 1:
            brake_torque = 2.5
            motor_torque = 2.5
        else:
            brake_torque = 5
            motor_torque = 5
        if distance < 0:
            brake_at *= -1
            brake_torque *= -1
            motor_torque *= -1
        return brake_at, motor_torque, brake_torque
