from typing import List, Optional
from abc import ABC
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.actions.action import Action
from tdw.replicant.actions.ik_motion import IkMotion
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.collision_detection import CollisionDetection
from tdw.replicant.arm import Arm
from tdw.replicant.image_frequency import ImageFrequency


class ArmMotion(IkMotion, ABC):
    """
    Abstract base class for actions related to Replicant arm motion.

    Duration an arm motion, the Replicant's arm(s) will continuously over multiple `communicate()` calls move until either the motion is complete or the arm collides with something (see `self.collision_detection`).

    - The collision detection will respond normally to walls, objects, obstacle avoidance, etc.
    - If `self.collision_detection.previous_was_same == True`, and if the previous action was a subclass of `ArmMotion`, and it ended in a collision, this action ends immediately.
    """

    def __init__(self, arms: List[Arm], dynamic: ReplicantDynamic, collision_detection: CollisionDetection,
                 previous: Optional[Action], duration: float, scale_duration: bool):
        """
        :param arms: A list of [`Arm`](../arm.md) values that will reach for the `target`. Example: `[Arm.left, Arm.right]`.
        :param dynamic: The [`ReplicantDynamic`](../replicant_dynamic.md) data that changes per `communicate()` call.
        :param collision_detection: The [`CollisionDetection`](../collision_detection.md) rules.
        :param previous: The previous action. Can be None.
        :param duration: The duration of the motion in seconds.
        :param scale_duration: If True, `duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        """

        super().__init__(duration=duration, scale_duration=scale_duration)
        """:field
        A list of [`Arm`](../arm.md) values that will reach for the `target`. Example: `[Arm.left, Arm.right]`.
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
        If the action fails in a collision, this is a list of arms that collided with something.
        """
        self.collisions: List[Arm] = list()
        # Immediately end the action if the previous action was the same motion and it ended with a collision.
        if self.collision_detection.previous_was_same and previous is not None and isinstance(previous, ArmMotion):
            for arm in self.arms:
                if arm in previous.collisions:
                    self.status = ActionStatus.collision

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        if len(dynamic.get_collision_enters(collision_detection=self.collision_detection)) > 0:
            self.status = ActionStatus.collision
        # Check if the motion is done.
        elif dynamic.output_data_status != ActionStatus.ongoing:
            self.status = dynamic.output_data_status
        return super().get_ongoing_commands(resp=resp, static=static, dynamic=dynamic)

    def get_end_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                         image_frequency: ImageFrequency) -> List[dict]:
        # Ignore held objects.
        for object_id in self.__held_objects:
            self.collision_detection.exclude_objects.remove(object_id)
        return super().get_end_commands(resp=resp, static=static, dynamic=dynamic, image_frequency=image_frequency)
