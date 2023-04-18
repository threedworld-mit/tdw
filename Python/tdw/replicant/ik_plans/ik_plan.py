from abc import ABC, abstractmethod
from typing import List, Dict, Union, Optional
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.actions.arm_motion import ArmMotion
from tdw.replicant.actions.action import Action
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.actions.reach_for import ReachFor
from tdw.replicant.collision_detection import CollisionDetection
from tdw.replicant.arm import Arm
from tdw.replicant.image_frequency import ImageFrequency


class IkPan(ABC):
    def __init__(self, target: Union[int, np.ndarray, Dict[str,  float]], arrived_at: float, max_distance: float, 
                 arm: Arm, dynamic: ReplicantDynamic, collision_detection: CollisionDetection, 
                 previous: Optional[Action], duration: float, scale_duration: bool, from_held: bool, held_point: str):
        """
        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        :param arrived_at: If the final [`ReachFor`](../actions/reach_for.md) action ends and the hand is this distance or less from the target, the motion succeeds.
        :param max_distance: If at the start of the first [`ReachFor`](../actions/reach_for.md) action the target is further away than this distance from the hand, the action fails.
        :param arm: The [`Arm`](../arm.md) that will reach for the `target`.
        :param dynamic: The [`ReplicantDynamic`](../replicant_dynamic.md) data that changes per `communicate()` call.
        :param collision_detection: The [`CollisionDetection`](../collision_detection.md) rules.
        :param previous: The previous action. Can be None.
        :param duration: The total duration of the motion in seconds. Each [`ReachFor`](../actions/reach_for.md) action is a fraction of this. For example, if there are 2 [`ReachFor`](../actions/reach_for.md) actions, then the duration of each of them is `duration / 2`.
        :param scale_duration: If True, `duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        :param from_held: If False, the Replicant will try to move its hand to the `target`. If True, the Replicant will try to move its held object to the `target`. This is ignored if the hand isn't holding an object.
        :param held_point: The bounds point of the held object from which the offset will be calculated. Can be `"bottom"`, `"top"`, etc. For example, if this is `"bottom"`, the Replicant will move the bottom point of its held object to the `target`. This is ignored if `from_held == False` or ths hand isn't holding an object.
        """

        """:field
        The total duration of the motion in seconds. Each [`ReachFor`](../actions/reach_for.md) action is a fraction of this. For example, if there are 2 [`ReachFor`](../actions/reach_for.md) actions, then the duration of each of them is `duration / 2`.
        """
        self.duration: float = duration
        """:field
        If True, `duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        """
        self.scale_duration: bool = scale_duration
        """:field
        The [`Arm`](../arm.md) that will reach for the `target`.
        """
        self.arm: Arm = arm
        """:field
        The [`CollisionDetection`](../collision_detection.md) rules.
        """
        self.collision_detection: CollisionDetection = collision_detection
        # Ignore collision detection for held items.
        self.__held_objects: List[int] = [v for v in dynamic.held_objects.values() if v not in self.collision_detection.exclude_objects]
        self.collision_detection.exclude_objects.extend(self.__held_objects)
        # Immediately end the action if the previous action was the same motion and it ended with a collision.
        if self.collision_detection.previous_was_same and previous is not None and isinstance(previous, ArmMotion) and arm in previous.collisions:
            if arm in previous.collisions:
                self.status = ActionStatus.collision            
        """:field
        The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        """
        self.target: Union[int, np.ndarray, Dict[str,  float]] = target
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
        """:field
        A list of [`ReachFor`](../actions/reach_for.md) sub-actions.
        """
        self.reach_fors: List[ReachFor] = self._get_reach_for_actions()
        """:field
        The index of the current action.
        """
        self.reach_for_index: int = 0
    
    @abstractmethod
    def _get_reach_for_actions(self) -> List[ReachFor]:
        """
        :return: A list of [`ReachFor`](../actions/reach_for.md) actions.
        """
        
        raise Exception()
