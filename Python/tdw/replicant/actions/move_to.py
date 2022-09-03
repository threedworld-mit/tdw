from typing import Union, Dict, List
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.output_data import Transforms
from tdw.replicant.replicant_utils import ReplicantUtils
from tdw.replicant.actions.action import Action
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.actions.turn_to import TurnTo
from tdw.replicant.actions.move_by import MoveBy
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.collision_detection import CollisionDetection
from tdw.replicant.image_frequency import ImageFrequency


class MoveTo(Action):
    """
    Turn the Replicant to a target position or object and then move to it.

    This action has two "sub-actions": A [`TurnTo`](turn_by.md) and a [`MoveBy`](move_by.md).
    """

    def __init__(self, target: Union[int, Dict[str, float]], resp: List[bytes], dynamic: ReplicantDynamic,
                 collision_detection: CollisionDetection, arrived_at: float = 0.1, aligned_at: float = 1,
                 arrived_offset: float = 0, previous: Action = None):
        """
        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        :param resp: The response from the build.
        :param arrived_at: If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful.
        :param aligned_at: If the difference between the current angle and the target angle is less than this value, then the action is successful.
        :param arrived_offset: Offset the arrival position by this value. This can be useful if the Magnebot needs to move to an object but shouldn't try to move to the object's centroid. This is distinct from `arrived_at` because it won't affect the Magnebot's braking solution.
        :param dynamic: [The dynamic Magnebot data.](../magnebot_dynamic.md)
        :param collision_detection: [The collision detection rules.](../collision_detection.md)
        :param previous: The previous action, if any.
        """

        super().__init__()
        self._turn_to: TurnTo = TurnTo(target=target, resp=resp, dynamic=dynamic,
                                       collision_detection=collision_detection,
                                       previous=previous)
        self.__image_frequency: ImageFrequency = ImageFrequency.once
        # Cache these in order to initialize the MoveBy action later.
        self.__collision_detection: CollisionDetection = collision_detection
        self.__arrived_at: float = arrived_at
        self.__arrived_offset: float = arrived_offset
        self._move_by: Optional[MoveBy] = None
        target_position = {"x": 0,"y": 0,"z": 0}
        # Set the target position.
        if isinstance(target, int):
            # Get the position of the object.
            target_position = ReplicantUtils.get_object_position(resp=resp, object_id=target)
            # We want the Replicant to stay on the floor, if the object is on a table for example.
            target_position["y"] = 0
        elif isinstance(target, dict):
            target_position = target
        else:
           raise Exception(f"Invalid target: {target}")
        # Compute distance from Replicant current location to object.
        self.distance = TDWUtils.get_distance(TDWUtils.array_to_vector3(dynamic.position), target_position) - self.__arrived_offset
        print(target_position)

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        # Remember the image frequency for the move action.
        self.__image_frequency: ImageFrequency = image_frequency
        return self._turn_to.get_initialization_commands(resp=resp, static=static, dynamic=dynamic, image_frequency=image_frequency)

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        commands = []
        # We haven't started moving yet (we are turning).
        if self._move_by is None:
            commands.extend(self._turn_to.get_ongoing_commands(resp=resp, static=static, dynamic=dynamic))
            # Continue turning.
            if self._turn_to.status == ActionStatus.ongoing:
                return commands
            # The turn succeeded. Start the move action.
            self._move_by = MoveBy(distance=self.distance, arrived_at=self.__arrived_at, dynamic=dynamic,
                                   collision_detection=self.__collision_detection, previous=self._turn_to)
            self._move_by.initialized = True
            # Initialize the move_by action.
            commands.extend(self._move_by.get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                                      image_frequency=self.__image_frequency))
            # The move immediately ended.
            if self._move_by.status != ActionStatus.ongoing:
                self.status = self._move_by.status
            return commands
        # Continue moving.
        else:
            # The move ended.
            if self._move_by.status != ActionStatus.ongoing:
                self.status = self._move_by.status
                return []
            else:
                commands.extend(self._move_by.get_ongoing_commands(resp=resp, static=static, dynamic=dynamic))
                return commands
