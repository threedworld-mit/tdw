from typing import List
from abc import ABC
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.actions.action import Action
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.collision_detection import CollisionDetection
from tdw.output_data import Collision, EnvironmentCollision
from tdw.agents.arm import Arm


class ArmMotion(Action, ABC):
    """
    Abstract base class for actions related to Replicant arm motion.
    """

    def __init__(self, arms: List[Arm], collision_detection: CollisionDetection, previous_collisions: List[Arm] = None,
                 num_frames: int = 15):
        """
        :param arms: The [`Arm`](../../agents/arm.md) values that will reach for the `target`. Example: `[Arm.left, Arm.right]`.
        :param collision_detection: [The collision detection rules.](../collision_detection.md)
        :param previous_collisions: Arms that reached for a target during the previous action but failed because they collided with something.
        :param num_frames: The number of frames for the action. This controls the speed of the action.
        """

        super().__init__()
        self._arms: List[Arm] = arms
        self._collision_detection: CollisionDetection = collision_detection
        self._num_frames: int = num_frames
        self._frame_count: int = 0
        # Immediately end the action if the previous action was the same motion and it ended with a collision.
        if self._collision_detection.previous_was_same and previous_collisions is not None and \
                len([a for a in Arm if a in arms and a in previous_collisions]) > 0:
            self.status = ActionStatus.collision
        """:field
        If the action fails in a collision, this is a list of arms that collided with something.
        """
        self.collisions: List[Arm] = list()

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        # Check only for collisions with arm joints.
        for arm in self._arms:
            arm_enters: List[int] = list()
            arm_exits: List[int] = list()
            for body_part in ReplicantStatic.ARM_JOINTS[arm]:
                body_part_id = static.body_parts[body_part]
                for collision in dynamic.collisions[body_part_id]:
                    if isinstance(collision, EnvironmentCollision):
                        state = collision.get_state()
                        if (self._collision_detection.floor and collision.get_floor()) or \
                                (self._collision_detection.walls and not collision.get_floor()):
                            if state == "enter":
                                arm_enters.append(body_part_id)
                            elif state == "exit":
                                arm_exits.append(body_part_id)
                    elif isinstance(collision, Collision):
                        collider_id = collision.get_collider_id()
                        # Accept the collision if the object is in the includes list or if it's not in the excludes list.
                        if collider_id in self._collision_detection.include_objects or \
                                (self._collision_detection.objects and collider_id not in
                                 self._collision_detection.exclude_objects):
                            if collision.get_state() == "enter":
                                arm_enters.append(body_part_id)
                            elif collision.get_state() == "exit":
                                arm_exits.append(body_part_id)
            # Ignore exit events.
            arm_enters = [e for e in arm_enters if e not in arm_exits]
            if len(arm_enters) > 0:
                self.collisions.append(arm)
        if len(self.collisions) > 0:
            self.status = ActionStatus.collision
        else:
            self._frame_count += 1
            if self._frame_count >= self._num_frames:
                self.status = ActionStatus.success
        return []
