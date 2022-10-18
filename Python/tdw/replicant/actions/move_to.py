from typing import Union, Dict, List, Optional
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Bounds
from tdw.replicant.actions.action import Action
from tdw.replicant.actions.turn_to import TurnTo
from tdw.replicant.actions.move_by import MoveBy
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.collision_detection import CollisionDetection
from tdw.replicant.image_frequency import ImageFrequency


class MoveTo(Action):
    """
    Turn the Replicant to a target position or object and then walk to it.
    """

    def __init__(self, target: Union[int, Dict[str, float], np.ndarray], resp: List[bytes],
                 collision_detection: CollisionDetection, previous: Action = None, reset_arms_num_frames: int = 15,
                 arrived_at: float = 0.1, max_walk_cycles: int = 100, bounds_position: str = "center"):
        """
        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        :param resp: The response from the build.
        :param collision_detection: [The collision detection rules.](../collision_detection.md)
        :param previous: The previous action, if any.
        :param reset_arms_num_frames: The number of frames for resetting the arms while walking. This controls the speed of the arm motion.
        :param arrived_at: If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful.
        :param max_walk_cycles: The walk animation will loop this many times maximum. If by that point the Replicant hasn't reached its destination, the action fails.
        :param bounds_position: If `target` is an integer object ID, move towards this bounds point of the object. Options: `"center"`, `"top`", `"bottom"`, `"left"`, `"right"`, `"front"`, `"back"`.
        """

        self._target: Union[int, Dict[str, float], np.ndarray] = target
        if isinstance(self._target, np.ndarray):
            self._target_position: np.ndarray = self._target
        elif isinstance(self._target, dict):
            self._target_position = TDWUtils.vector3_to_array(self._target)
        # Get the target position.
        elif isinstance(self._target, int):
            self._target_position = np.zeros(shape=3)
            for i in range(len(resp) - 1):
                # Get the output data ID.
                r_id = OutputData.get_data_type_id(resp[i])
                # Get the bounds data.
                if r_id == "boun":
                    bounds = Bounds(resp[i])
                    for j in range(bounds.get_num()):
                        if bounds.get_id(j) == self._target:
                            bound = TDWUtils.get_bounds_dict(bounds, j)
                            self._target_position = bound[bounds_position]
                            break
                    break
        else:
            raise Exception(f"Invalid target: {self._target}")
        self._turning: bool = True
        self._image_frequency: ImageFrequency = ImageFrequency.once
        self._move_by: Optional[MoveBy] = None
        self._collision_detection: CollisionDetection = collision_detection
        self._previous_action: Optional[Action] = previous
        self._reset_arms_num_frames: int = reset_arms_num_frames
        self._arrived_at: float = arrived_at
        self._max_walk_cycles: int = max_walk_cycles
        super().__init__()

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        # Remember the image frequency.
        self._image_frequency = image_frequency
        # Turn to the target.
        return TurnTo(target=self._target).get_initialization_commands(resp=resp,
                                                                       static=static,
                                                                       dynamic=dynamic,
                                                                       image_frequency=image_frequency)

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        if self._turning:
            # Start walking.
            self._turning = False
            # Get the distance.
            distance = np.linalg.norm(dynamic.transform.position - self._target_position)
            # Get the direction.
            forward = np.linalg.norm(dynamic.transform.position - (dynamic.transform.position + dynamic.transform.forward * distance))
            backward = np.linalg.norm(dynamic.transform.position - (dynamic.transform.position + dynamic.transform.forward * -distance))
            if forward > backward:
                distance *= -1
            # Start walking.
            self._move_by = MoveBy(distance=float(distance),
                                   dynamic=dynamic,
                                   collision_detection=self._collision_detection,
                                   previous=self._previous_action,
                                   reset_arms_num_frames=self._reset_arms_num_frames,
                                   arrived_at=self._arrived_at,
                                   max_walk_cycles=self._max_walk_cycles)
            commands = self._move_by.get_initialization_commands(resp=resp,
                                                                 static=static,
                                                                 dynamic=dynamic,
                                                                 image_frequency=self._image_frequency)
            self.status = self._move_by.status
            return commands
        # Keep walking.
        commands = self._move_by.get_ongoing_commands(resp=resp,
                                                      static=static,
                                                      dynamic=dynamic)
        self.status = self._move_by.status
        return commands

    def get_end_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                         image_frequency: ImageFrequency) -> List[dict]:
        if self._move_by is not None:
            return self._move_by.get_end_commands(resp=resp, static=static, dynamic=dynamic, image_frequency=image_frequency)
        else:
            return super().get_end_commands(resp=resp, static=static, dynamic=dynamic, image_frequency=image_frequency)
