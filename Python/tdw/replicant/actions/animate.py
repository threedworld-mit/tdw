from typing import List, Optional
from tdw.replicant.actions.action import Action
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.collision_detection import CollisionDetection
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.image_frequency import ImageFrequency
from tdw.replicant.replicant_body_part import ReplicantBodyPart
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.librarian import HumanoidAnimationLibrarian, HumanoidAnimationRecord


class Animate(Action):
    """
    Play an animation.

    The animation will end either when the animation clip is finished or if the Replicant collides with something (see `self.collision_detection`).

    - The collision detection will respond normally to walls, objects, obstacle avoidance, etc.
    - If `self.collision_detection.previous_was_same == True`, and it was the same animation, and it ended in a collision, this action ends immediately.
    """

    def __init__(self, animation: str, collision_detection: CollisionDetection, forward: bool, library: str,
                 previous: Optional[Action], ik_body_parts: List[ReplicantBodyPart], loop: bool):
        """
        :param animation: The name of the animation.
        :param collision_detection: The [`CollisionDetection`](../collision_detection.md) rules.
        :param forward: If True, play the animation forwards. If False, play the animation backwards.
        :param library: The name of the animation's library.
        :param previous: The previous action. Can be None.
        :param ik_body_parts: Maintain the IK positions of these body parts.
        :param loop: If True, the animation will continuously loop and the action will continue until interrupted.
        """

        super().__init__()
        # Add the animation library.
        if library not in Controller.HUMANOID_ANIMATION_LIBRARIANS:
            Controller.HUMANOID_ANIMATION_LIBRARIANS[library] = HumanoidAnimationLibrarian(library)
        """:field
        The `HumanoidAnimationRecord` of the animation.
        """
        self.record: HumanoidAnimationRecord = Controller.HUMANOID_ANIMATION_LIBRARIANS[library].get_record(animation)
        """:field
        The [`CollisionDetection`](../collision_detection.md) rules.
        """
        self.collision_detection: CollisionDetection = collision_detection
        # Don't try to play the same animation twice if the first one ended in a collision.
        if self.collision_detection.previous_was_same and previous is not None and isinstance(previous, Animate) and \
                previous.status == ActionStatus.collision and previous.record.name == self.record.name:
            self.status = ActionStatus.collision
        """:field
        If True, play the animation forwards. If False, play the animation backwards.
        """
        self.forward: bool = forward
        """:field
        If True, the animation will continuously loop and the action will continue until interrupted.
        """
        self.loop: bool = loop
        # Maintain the IK positions of these body parts.
        self._ik_body_parts: List[str] = [b.name for b in ik_body_parts]

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        # Download the animation if needed. Play the animation.
        commands.extend([{"$type": "add_humanoid_animation",
                          "name": self.record.name,
                          "url": self.record.get_url()},
                         {"$type": "play_replicant_animation",
                          "name": self.record.name,
                          "id": static.replicant_id,
                          "framerate": self.record.framerate,
                          "forward": self.forward,
                          "ik_body_parts": self._ik_body_parts,
                          "loop": self.loop}])
        return commands

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        # If there was a collision, stop the animation.
        if len(dynamic.get_collision_enters(collision_detection=self.collision_detection)) > 0:
            self.status = ActionStatus.collision
        # Check if the animation is done.
        elif dynamic.output_data_status != ActionStatus.ongoing:
            self.status = dynamic.output_data_status
        # Try to resolve collider intersections.
        commands = super().get_ongoing_commands(resp=resp, static=static, dynamic=dynamic)
        collider_intersections_direction = dynamic.transform.forward
        if not self.forward:
            collider_intersections_direction = -collider_intersections_direction
        commands.append({"$type": "replicant_resolve_collider_intersections",
                         "id": static.replicant_id,
                         "direction": TDWUtils.array_to_vector3(collider_intersections_direction)})
        return commands
