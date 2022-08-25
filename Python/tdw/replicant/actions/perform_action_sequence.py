from typing import Dict, List
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.output_data import Transforms
from tdw.replicant.replicant_utils import ReplicantUtils
from tdw.replicant.actions.action import Action
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.collision_detection import CollisionDetection


class PerformActionSequence(Action):
    """
    Perform a sequence chain of motion capture animations.
    """

    def __init__(self, animation_list: List[str], dynamic: ReplicantDynamic, collision_detection: CollisionDetection, previous: Action = None):
        """
        :param animation_list: The list of animation names in the sequence we want to play.
        :param dynamic: [The dynamic Magnebot data.](../magnebot_dynamic.md)
        :param collision_detection: [The collision detection rules.](../collision_detection.md)
        :param previous: The previous action, if any.
        """
        super().__init__(dynamic=dynamic, collision_detection=collision_detection, previous=previous)
        self.animation_list = animation_list
        # Running frame count.
        self.total_frame_count: int = 0
        # Per-animation frame count.
        self.frame_count: int = 0
        self.current_anim_length: int= 0
        # Total number of animations.
        self.num_anims: int = 0
        # Running count of animations.
        self.anim_count: int = 0

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        # Remember the image frequency for the action.
        self.__image_frequency: ImageFrequency = image_frequency
        # Download all of the animations in the list.
        for anim_name in self.animation_list:
            commands.append({"$type": "add_humanoid_animation", 
                             "name": anim_name, 
                             "url": "https://tdw-public.s3.amazonaws.com/humanoid_animations/windows/2019.2/" + anim_name})
        return commands


    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        p1 = dynamic.position
        d = np.linalg.norm(p1 - self._target_position_arr)
        # We've played all of the animations.
        if self.anim_count >= self.num_anims:
            self.status = ActionStatus.success
            commands = []
            commands.extend(self.get_end_commands(resp=resp, static=static, dynamic=dynamic, image_frequency=None))
            return commands
        elif not self._is_valid_ongoing(dynamic=dynamic):
            return []
        elif self.status == ActionStatus.ongoing:
            # We still have animations to play.
            if self.anim_count < self.num_anims
                # Still playing back current animation.
                if self.frame_count < self.current_anim_length
                    self.frame_count += 1 
                    return []
                else:
                    # Start the next animation in the sequence.
                    #print("Starting new anim")
                    commands = []
                    self.anim_count += 1
                    self.frame_count = 0
                    commands.extend(self._get_walk_commands(dynamic=dynamic))
                    return commands
                
                

    def _previous_was_same(self, previous: Action) -> bool:
        if isinstance(previous, MoveBy):
            return (previous.distance > 0 and self.distance > 0) or (previous.distance < 0 and self.distance < 0)
        else:
            return False

