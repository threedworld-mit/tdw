from __future__ import annotations
from typing import List
from tdw.replicant.actions.action import Action
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.collision_detection import CollisionDetection
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.image_frequency import ImageFrequency
from tdw.controller import Controller
from tdw.librarian import HumanoidAnimationLibrarian, HumanoidAnimationRecord


class Animate(Action):
    """
    Play an animation.
    """

    def __init__(self, animation: str, collision_detection: CollisionDetection, forward: bool = True,
                 library: str = "humanoid_animations.json", previous: Action = None):
        """
        :param animation: The name of the animation.
        :param collision_detection: The [`CollisionDetection`](../collision_detection.md) rules.
        :param forward: If True, play the animation forwards. If False, play the animation backwards.
        :param library: The name animation library.
        :param previous: The previous action. Can be None.
        """

        super().__init__()
        # Add the animation library.
        if library not in Controller.HUMANOID_ANIMATION_LIBRARIANS:
            Controller.HUMANOID_ANIMATION_LIBRARIANS[library] = HumanoidAnimationLibrarian(library)
        # Get the animation record.
        self._record: HumanoidAnimationRecord = Controller.HUMANOID_ANIMATION_LIBRARIANS[library].get_record(animation)
        self._collision_detection: CollisionDetection = collision_detection
        # Don't try to play the same animation twice if the first one ended in a collision.
        if self._collision_detection.previous_was_same and previous is not None and isinstance(previous, Animate) and \
                previous.status == ActionStatus.collision and previous._record.name == self._record.name:
            self.status = ActionStatus.collision
        self._forward: bool = forward

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        # Download the animation if needed. Play the animation.
        commands.extend([{"$type": "add_humanoid_animation",
                          "name": self._record.name,
                          "url": self._record.get_url()},
                         {"$type": "play_humanoid_animation",
                          "name": self._record.name,
                          "id": static.replicant_id,
                          "framerate": self._record.framerate,
                          "forward": self._forward}])
        return commands

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        # If there was a collision, stop the animation.
        if len(dynamic.get_collision_enters(collision_detection=self._collision_detection)) > 0:
            self.status = ActionStatus.collision
        # Continue the animation.
        elif self._get_motion_complete(replicant_id=static.replicant_id, resp=resp):
            self.status = ActionStatus.success
        return []

    def get_end_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                         image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_end_commands(resp=resp, static=static, dynamic=dynamic, image_frequency=image_frequency)
        # Stop the animation.
        commands.append({"$type": "stop_humanoid_animation",
                         "id": static.replicant_id})
        return commands
