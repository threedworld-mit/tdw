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
from tdw.replicant.animation_manager import AnimationManager
from tdw.replicant.image_frequency import ImageFrequency


class PerformActionSequence(Action):
    """
    Perform a sequence of motion capture animations.
    """

    def __init__(self, animation_list: List[str], resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic, 
                 collision_detection: CollisionDetection, previous: Action = None):
        """
        :param animation_list: The list of animation names in the sequence we want to play.
        :param dynamic: [The dynamic Replicant data.](../magnebot_dynamic.md)
        :param collision_detection: [The collision detection rules.](../collision_detection.md)
        :param previous: The previous action, if any.
        """
        super().__init__()
        self._collision_detection: CollisionDetection = collision_detection
        self._animation_list = animation_list
        self._animation_manager = AnimationManager(self._animation_list)
        self._current_anim_name: str = ""
        # Per-animation frame count.
        self._frame_count: int = 0
        # Number of frames in current animation.
        self._current_anim_length: int = 0
        # Running count of played animations.
        self._played_anim_count: int = 0
        # Running count of played animations.
        self._anim_index: int = 0
        self._initialized = False

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        # Remember the image frequency for the action.
        self.__image_frequency: ImageFrequency = image_frequency
        # Download all 
        commands.extend(self._animation_manager.download_animations())
        return commands


    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        if not self._is_valid_ongoing(dynamic=dynamic):
            return []
        elif self.status == ActionStatus.ongoing:
            # Still playing back current animation.
            if self._frame_count < self._current_anim_length:
                self._frame_count += 1 
                return []
            else:
                self._played_anim_count += 1
                # We've played all of the animations.
                if self._played_anim_count > len(self._animation_list):
                    self.status = ActionStatus.success
                    commands = []
                    #commands.extend(self.get_end_commands(resp=resp, static=static, dynamic=dynamic, image_frequency=None))
                    return commands
                else:
                    # Start the next animation in the sequence.
                    commands = []
                    # Fetch next animation in the sequence.
                    self._current_anim_name = self._animation_list[self._anim_index]
                    self._current_anim_length = self._animation_manager.ANIMATION_DATA_LIST[self._current_anim_name].get_num_frames()
                    commands.extend(self._get_play_anim_commands(anim_name=self._current_anim_name, 
                                                                     framerate=self._animation_manager.ANIMATION_DATA_LIST[self._current_anim_name].framerate,
                                                                     static=static))
                    self._anim_index += 1
                    return commands
                
    def _get_play_anim_commands(self, anim_name: str, framerate: int, static: ReplicantStatic) -> List[dict]:
        self._frame_count = 0
        commands = []
        commands.extend([{"$type": "set_target_framerate", 
                          "framerate": framerate},
                         {"$type": "play_humanoid_animation",
                          "name": anim_name,
                          "id": static.replicant_id}])
        self._playing = True
        return commands  


    def _is_valid_ongoing(self, dynamic: ReplicantDynamic) -> bool:
        """
        :param replicant_id: The ID of this Replicant

        :return: True if the Replicant didn't collide with something that should make it stop.
        """
        # Stop if the Replicant is colliding with something.
        if self._is_collision(dynamic=dynamic):
            self.status = ActionStatus.collision
            return False
        else:
            return True

    def _is_collision(self, dynamic: ReplicantDynamic) -> bool:
        """
        :param replicant_id: The ID of this Replicant

        :return: True if there was a collision that according to the current detection rules means that the Replicant needs to stop moving.
        """
        # Check environment collisions.
        if self._collision_detection.floor or self._collision_detection.walls:
            enters: List[int] = list()
            exits: List[int] = list()
            for object_id in dynamic.collisions_with_environment:
                for collision in dynamic.collisions_with_environment[object_id]:
                    if (self._collision_detection.floor and collision.floor) or \
                            (self._collision_detection.walls and not collision.floor):
                        if collision.state == "enter":
                            enters.append(object_id)
                        elif collision.state == "exit":
                            exits.append(object_id)
            # Ignore exit events.
            enters = [e for e in enters if e not in exits]
            if len(enters) > 0:
                return True
        # Check object collisions.
        if self._collision_detection.objects or len(self._collision_detection.include_objects) > 0:
            enters: List[Tuple[int, int]] = list()
            exits: List[Tuple[int, int]] = list()
            for object_ids in dynamic.collisions_with_objects:
                for collision in dynamic.collisions_with_objects[object_ids]:
                    object_id = object_ids[1]
                    # Accept the collision if the object is in the includes list or if it's not in the excludes list.
                    if object_id in self._collision_detection.include_objects or \
                            (self._collision_detection.objects and object_id not in
                             self._collision_detection.exclude_objects):
                        if collision.state == "enter":
                            enters.append(object_ids)
                        elif collision.state == "exit":
                            exits.append(object_ids)
            # Ignore exit events.
            enters: List[Tuple[int, int]] = [e for e in enters if e not in exits]
            if len(enters) > 0:
                return True
        return False          

    def _previous_was_same(self, previous: Action) -> bool:
        if isinstance(previous, MoveBy):
            return (previous.distance > 0 and self.distance > 0) or (previous.distance < 0 and self.distance < 0)
        else:
            return False

