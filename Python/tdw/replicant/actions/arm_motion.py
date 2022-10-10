from typing import List
from abc import ABC
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.actions.action import Action
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.collision_detection import CollisionDetection
from tdw.agents.arm import Arm


class ArmMotion(Action, ABC):
    """
    Abstract base class for actions related to Replicant arm motion.
    """

    def __init__(self, arms: List[Arm], collision_detection: CollisionDetection,
                 previous=None, num_frames: int = 15):
        """
        :param arms: The [`Arm`](../../agents/arm.md) values that will reach for the `target`. Example: `[Arm.left, Arm.right]`.
        :param collision_detection: [The collision detection rules.](../collision_detection.md)
        :param previous: The previous action. Can be None.
        :param num_frames: The number of frames for the action. This controls the speed of the action.
        """

        super().__init__()
        self._arms: List[Arm] = arms
        self._collision_detection: CollisionDetection = collision_detection
        self._num_frames: int = num_frames
        self._frame_count: int = 0
        # Immediately end the action if the previous action was the same motion and it ended with a collision.
        if self._collision_detection.previous_was_same and previous is not None and isinstance(previous, ArmMotion):
            for arm in self._arms:
                if arm in previous.collisions:
                    self.status = ActionStatus.collision
        """:field
        If the action fails in a collision, this is a list of arms that collided with something.
        """
        self.collisions: List[Arm] = list()

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        # Get body part collisions.
        body_part_collisions = dynamic.get_collision_enters(collision_detection=self._collision_detection)
        # Filter for only collisions involving arm joints.
        for arm in self._arms:
            if len([b for b in body_part_collisions if static.body_parts_by_id[b] in ReplicantStatic.ARM_JOINTS[arm]]) > 0:
                self.collisions.append(arm)
        if len(self.collisions) > 0:
            self.status = ActionStatus.collision
        else:
            self._frame_count += 1
            if self._frame_count >= self._num_frames:
                self.status = ActionStatus.success
        return []
