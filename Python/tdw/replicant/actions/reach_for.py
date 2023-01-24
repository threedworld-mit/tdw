from __future__ import annotations
from typing import List, Dict, Union, Optional
import numpy as np
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
    Reach for a target object or position. One or both hands can reach for the target at the same time.

    If target is an object, the target position is a point on the object.
    If the object has affordance points, the target position is the affordance point closest to the hand.
    Otherwise, the target position is the bounds position closest to the hand.

    The Replicant's arm(s) will continuously over multiple `communicate()` calls move until either the motion is complete or the arm collides with something (see `self.collision_detection`).

    - If the hand is near the target at the end of the action, the action succeeds.
    - If the target is too far away at the start of the action, the action fails.
    - The collision detection will respond normally to walls, objects, obstacle avoidance, etc.
    - If `self.collision_detection.previous_was_same == True`, and if the previous action was a subclass of `ArmMotion`, and it ended in a collision, this action ends immediately.
    """

    def __init__(self, target: Union[int, np.ndarray, Dict[str,  float]], offhand_follows: bool,
                 arrived_at: float, max_distance: float, arms: List[Arm], dynamic: ReplicantDynamic,
                 collision_detection: CollisionDetection, previous: Optional[Action], duration: float,
                 scale_duration: bool):
        """
        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        :param offhand_follows: If True, the offhand will follow the primary hand, meaning that it will maintain the same relative position. Ignored if `len(arms) > 1` or if `target` is an object ID.
        :param arrived_at: If the motion ends and the hand is this distance or less from the target, the action succeeds.
        :param max_distance: If the target is further away from this distance at the start of the action, the action fails.
        :param arms: A list of [`Arm`](../arm.md) values that will reach for the `target`. Example: `[Arm.left, Arm.right]`.
        :param dynamic: The [`ReplicantDynamic`](../replicant_dynamic.md) data that changes per `communicate()` call.
        :param collision_detection: The [`CollisionDetection`](../collision_detection.md) rules.
        :param previous: The previous action. Can be None.
        :param duration: The duration of the motion in seconds.
        :param scale_duration: If True, `duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        """

        super().__init__(arms=arms, dynamic=dynamic, collision_detection=collision_detection, previous=previous,
                         duration=duration, scale_duration=scale_duration)
        """:field
        The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        """
        self.target: Union[int, np.ndarray, Dict[str,  float]] = target
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
        self.offhand_follows: bool = offhand_follows

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        # Reach for a target position.
        if isinstance(self.target, np.ndarray):
            commands.extend(self._get_reach_for_position(target=TDWUtils.array_to_vector3(self.target),
                                                         static=static,
                                                         dynamic=dynamic))
        # Reach for a target position.
        elif isinstance(self.target, dict):
            commands.extend(self._get_reach_for_position(target=self.target,
                                                         static=static,
                                                         dynamic=dynamic))
        # Reach for a target object.
        elif isinstance(self.target, int):
            commands.extend([{"$type": "replicant_reach_for_object",
                              "id": static.replicant_id,
                              "object_id": int(self.target),
                              "duration": self.duration,
                              "arm": arm.name,
                              "max_distance": self.max_distance,
                              "arrived_at": self.arrived_at} for arm in self.arms])
        else:
            raise Exception(f"Invalid target: {self.target}")
        return commands

    def _get_reach_for_position(self, target: Dict[str, float], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        commands = [{"$type": "replicant_reach_for_position",
                     "id": static.replicant_id,
                     "position": target,
                     "duration": self.duration,
                     "arm": arm.name,
                     "max_distance": self.max_distance,
                     "arrived_at": self.arrived_at} for arm in self.arms]
        # Tell the offhand to follow.
        if self.offhand_follows and len(self.arms) == 1:
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
                             "arrived_at": self.arrived_at})
        return commands
