from typing import List, Dict, Optional
import numpy as np
from tdw.type_aliases import TARGET
from tdw.tdw_utils import TDWUtils
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.actions.arm_motion import ArmMotion
from tdw.replicant.actions.action import Action
from tdw.replicant.collision_detection import CollisionDetection
from tdw.replicant.arm import Arm
from tdw.replicant.image_frequency import ImageFrequency


class ReachFor(ArmMotion):
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

    See also: [`ReachForWithPlan`](reach_for_with_plan.md).
    """

    def __init__(self, targets: List[TARGET], absolute: bool, offhand_follows: bool,
                 arrived_at: float, max_distance: float, arms: List[Arm], dynamic: ReplicantDynamic,
                 collision_detection: CollisionDetection, previous: Optional[Action], duration: float,
                 scale_duration: bool, from_held: bool, held_point: str):
        """
        :param targets: The target per arm. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        :param absolute: If True, the target position is in world space coordinates. If False, the target position is relative to the Replicant. Ignored if `target` is an int.
        :param offhand_follows: If True, the offhand will follow the primary hand, meaning that it will maintain the same relative position. Ignored if `len(arms) > 1` or if `target` is an object ID.
        :param arrived_at: If the motion ends and the hand is this distance or less from the target, the action succeeds.
        :param max_distance: If the target is further away from this distance at the start of the action, the action fails.
        :param arms: A list of [`Arm`](../arm.md) values that will reach for the `target`. Example: `[Arm.left, Arm.right]`.
        :param dynamic: The [`ReplicantDynamic`](../replicant_dynamic.md) data that changes per `communicate()` call.
        :param collision_detection: The [`CollisionDetection`](../collision_detection.md) rules.
        :param previous: The previous action. Can be None.
        :param duration: The duration of the motion in seconds.
        :param scale_duration: If True, `duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        :param from_held: If False, the Replicant will try to move its hand to the `target`. If True, the Replicant will try to move its held object to the `target`. This is ignored if the hand isn't holding an object.
        :param held_point: The bounds point of the held object from which the offset will be calculated. Can be `"bottom"`, `"top"`, etc. For example, if this is `"bottom"`, the Replicant will move the bottom point of its held object to the `target`. This is ignored if `from_held == False` or ths hand isn't holding an object.
        """

        super().__init__(arms=arms, dynamic=dynamic, collision_detection=collision_detection, previous=previous,
                         duration=duration, scale_duration=scale_duration)
        """:field
        The target per arm. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        """
        self.targets: List[TARGET] = targets
        """:field
        If True, the target position is in world space coordinates. If False, the target position is relative to the Replicant. Ignored if `target` is an int.
        """
        self.absolute: bool = absolute
        """:field
        If the motion ends and the hand is this distance or less from the target, the action succeeds.
        """
        self.arrived_at: float = arrived_at
        """:field
        If the target is further away from this distance at the start of the action, the action fails.
        """
        self.max_distance: float = max_distance
        """:field
        If True, the offhand will follow the primary hand, meaning that it will maintain the same relative position. Ignored if `len(arms) > 1` or if `target` is an object ID.
        """
        self.offhand_follows: bool = offhand_follows and len(arms) == 1
        """:field
        If False, the Replicant will try to move its hand to the `target`. If True, the Replicant will try to move its held object to the `target`.
        """
        self.from_held: bool = from_held
        """:field
        The bounds point of the held object from which the offset will be calculated. Can be `"bottom"`, `"top"`, etc. For example, if this is `"bottom"`, the Replicant will move the bottom point of its held object to the `target`. This is ignored if `from_held == False` or ths hand isn't holding an object.
        """
        self.held_point: str = held_point

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        for target, arm in zip(self.targets, self.arms):
            # Reach for a target position.
            if isinstance(target, np.ndarray):
                commands.extend(self._get_reach_for_position(target=TDWUtils.array_to_vector3(target),
                                                             arm=arm,
                                                             resp=resp,
                                                             static=static,
                                                             dynamic=dynamic))
            # Reach for a target position.
            elif isinstance(target, dict):
                commands.extend(self._get_reach_for_position(target=target,
                                                             arm=arm,
                                                             resp=resp,
                                                             static=static,
                                                             dynamic=dynamic))
            # Reach for a target object.
            elif isinstance(target, int):
                commands.append({"$type": "replicant_reach_for_object",
                                 "id": static.replicant_id,
                                 "object_id": int(target),
                                 "duration": self.duration,
                                 "arm": arm.name,
                                 "max_distance": self.max_distance,
                                 "arrived_at": self.arrived_at,
                                 "from_held": self.from_held,
                                 "held_point": self.held_point,
                                 "offset": self._get_offset(arm=arm, resp=resp, static=static, dynamic=dynamic)})
            else:
                raise Exception(f"Invalid target: {target} for arm {arm.name}")
        return commands

    def _get_reach_for_position(self, target: Dict[str, float], arm: Arm, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        commands = [{"$type": "replicant_reach_for_position" if self.absolute else "replicant_reach_for_relative_position",
                     "id": static.replicant_id,
                     "position": target,
                     "duration": self.duration,
                     "arm": arm.name,
                     "max_distance": self.max_distance,
                     "arrived_at": self.arrived_at,
                     "offset": self._get_offset(arm=arm, resp=resp, static=static, dynamic=dynamic)}]
        # Tell the offhand to follow.
        if self.offhand_follows:
            # Get the offset to the target.
            offset = TDWUtils.vector3_to_array(target) - dynamic.body_parts[static.hands[self.arms[0]]].position
            # Get the offhand.
            offhand = Arm.right if self.arms[0] == Arm.left else Arm.left
            # Get the position.
            position = dynamic.body_parts[static.hands[offhand]].position + offset
            # Set the target of the offhand.
            commands.append({"$type": "replicant_reach_for_position",
                             "id": static.replicant_id,
                             "position": TDWUtils.array_to_vector3(position),
                             "duration": self.duration,
                             "arm": offhand.name,
                             "max_distance": self.max_distance,
                             "arrived_at": self.arrived_at,
                             "offset": self._get_offset(arm=offhand, resp=resp, static=static, dynamic=dynamic)})
        return commands

    def _get_offset(self, arm: Arm, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> Dict[str, float]:
        if self.from_held and arm in dynamic.held_objects:
            bounds = self._get_object_bounds(object_id=dynamic.held_objects[arm], resp=resp)
            object_position = bounds[self.held_point]
            hand_position = dynamic.body_parts[static.hands[arm]].position
            return TDWUtils.array_to_vector3(hand_position - object_position)
        else:
            return {"x": 0, "y": 0, "z": 0}
