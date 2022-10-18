from typing import List
from abc import ABC
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.actions.action import Action
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.collision_detection import CollisionDetection
from tdw.agents.arm import Arm
from tdw.agents.image_frequency import ImageFrequency


class ArmMotion(Action, ABC):
    """
    Abstract base class for actions related to Replicant arm motion.
    """

    def __init__(self, arms: List[Arm], dynamic: ReplicantDynamic, collision_detection: CollisionDetection,
                 previous=None, duration: float = 0.25):
        """
        :param arms: The [`Arm`](../../agents/arm.md) values that will reach for the `target`. Example: `[Arm.left, Arm.right]`.
        :param dynamic: [`ReplicantDynamic`](../replicant_dynamic.md) data.
        :param collision_detection: [The collision detection rules.](../collision_detection.md)
        :param previous: The previous action. Can be None.
        :param duration: The duration of the motion in seconds.
        """

        super().__init__()
        self._arms: List[Arm] = arms
        self._collision_detection: CollisionDetection = collision_detection
        # Ignore collision detection for held items.
        self.__held_objects: List[int] = [v for v in dynamic.held_objects.values() if v not in self._collision_detection.exclude_objects]
        self._collision_detection.exclude_objects.extend(self.__held_objects)
        self._duration: float = duration
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
        elif self._get_motion_complete(replicant_id=static.replicant_id, resp=resp):
            self.status = ActionStatus.success
        return []

    def get_end_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                         image_frequency: ImageFrequency) -> List[dict]:
        # Ignore held objects.
        for object_id in self.__held_objects:
            self._collision_detection.exclude_objects.remove(object_id)
        return super().get_end_commands(resp=resp, static=static, dynamic=dynamic, image_frequency=image_frequency)
