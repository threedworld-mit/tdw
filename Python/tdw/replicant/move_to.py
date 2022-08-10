from typing import Union, Dict, List
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.output_data import Transforms
from tdw.replicant.replicant_utils import ReplicantUtils
from tdw.replicant.action import Action
from tdw.replicant.actions.turn_to import TurnTo
from tdw.replicant.actions.move_by import MoveBy
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic


class MoveTo(Action):
    """
    Turn the Replicant to a target position or object and then move to it.

    This action has two "sub-actions": A [`TurnTo`](turn_by.md) and a [`MoveBy`](move_by.md).
    """

    def __init__(self, target: Union[int, Dict[str, float]], resp: List[bytes], dynamic: ReplicantDynamic,
                 walk_motion_name: str, collision_detection: CollisionDetection, arrived_at: float = 0.1, 
                 aligned_at: float = 1, arrived_offset: float = 0, previous: Action = None):
        """
        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        :param resp: The response from the build.
        :param arrived_at: If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful.
        :param aligned_at: If the difference between the current angle and the target angle is less than this value, then the action is successful.
        :param arrived_offset: Offset the arrival position by this value. This can be useful if the Magnebot needs to move to an object but shouldn't try to move to the object's centroid. This is distinct from `arrived_at` because it won't affect the Magnebot's braking solution.
        :param dynamic: [The dynamic Replicant data.](../magnebot_dynamic.md)
        :param collision_detection: [The collision detection rules.](../collision_detection.md)
        :param previous: The previous action, if any.
        """

        super().__init__()
        self.target = target
        self._turn_to: TurnTo = TurnTo(target=target, resp=resp, dynamic=dynamic,
                                       collision_detection=collision_detection, aligned_at=aligned_at,
                                       previous=previous)
        self.__image_frequency: ImageFrequency = ImageFrequency.once
        # Cache these in order to initialize the MoveBy action later.
        self.__collision_detection: CollisionDetection = collision_detection
        self.__arrived_at: float = arrived_at
        self.__arrived_offset: float = arrived_offset
        self._move_by: Optional[MoveBy] = None

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        # Remember the image frequency for the move action.
        self.__image_frequency: ImageFrequency = image_frequency
        return self._turn_to.get_initialization_commands(resp=resp, static=static, dynamic=dynamic)

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        commands = []
        object_position = {"x": 0,"y": 0,"z": 0}
        # Set the target position.
        if isinstance(self.target, int):
            # Get the position of the object.
            object_position = ReplicantUtils.get_object_position(resp=resp, self.target)
        elif isinstance(self.target, dict):
            object_position = self.target
        else:
           raise Exception(f"Invalid target: {self.target}")
        # Compute distance from Replicant current location to object.
        distance = ReplicantUtils.get_distance(resp=resp, dynamic.replicant_id, object_position) 
        self._move_by = MoveBy(distance=distance, arrived_at=self.__arrived_at, dynamic=dynamic,
                               walk_motion_name=walk_motion_name, collision_detection=self.__collision_detection, previous=self._turn_to)
        self._move_by.initialized = True
        # Initialize the move_by action.
        commands.extend(self._move_by.get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                                  image_frequency=self.__image_frequency))
        # The move immediately ended.
        if self._move_by.status != ActionStatus.ongoing:
            self.status = self._move_by.status
            return []
        else:
            return commands

