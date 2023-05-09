from typing import Union, Dict, List, Optional
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Bounds
from tdw.drone.actions.action import Action
from tdw.drone.actions.turn_to import TurnTo
from tdw.drone.actions.move_by import MoveBy
from tdw.drone.drone_dynamic import droneDynamic
from tdw.drone.collision_detection import CollisionDetection
from tdw.drone.image_frequency import ImageFrequency


class MoveTo(Action):
    """
    Turn the drone to a target position or object and then fly to it.

    The action can end for several reasons depending on the collision detection rules (see [`self.collision_detection`](../collision_detection.md).

    - If the drone flys the target distance (i.e. it reaches its target), the action succeeds.
    - If `self.collision_detection.previous_was_same == True`, and the previous action was `MoveBy` or `MoveTo`, and it was in the same direction (forwards/backwards), and the previous action ended in failure, this action ends immediately.
    - If `self.collision_detection.avoid_obstacles == True` and the drone encounters a wall or object in its path:
      - If the object is in `self.collision_detection.exclude_objects`, the drone ignores it.
      - Otherwise, the action ends in failure.
    - If the drone collides with an object and `self.collision_detection.objects == True` and/or `self.collision_detection.walls == True` respectively:
      - If the object is in `self.collision_detection.exclude_objects`, the drone ignores it.
      - Otherwise, the action ends in failure.
    - If the drone takes too long to reach the target distance, the action ends in failure (see `self.max_walk_cycles`).
    """

    def __init__(self, target: Union[int, Dict[str, float], np.ndarray], collision_detection: CollisionDetection,
                 previous: Optional[Action], arrived_at: float, bounds_position: str):
        """
        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        :param collision_detection: The [`CollisionDetection`](../collision_detection.md) rules.
        :param previous: The previous action, if any.s.
        :param arrived_at: If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful.
        :param bounds_position: If `target` is an integer object ID, move towards this bounds point of the object. Options: `"center"`, `"top`", `"bottom"`, `"left"`, `"right"`, `"front"`, `"back"`.
        """

        """:field
        The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        """
        self.target: Union[int, Dict[str, float], np.ndarray] = target
        """:field
        The [`CollisionDetection`](../collision_detection.md) rules.
        """
        self.collision_detection: CollisionDetection = collision_detection
        """:field
        If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful.
        """
        self.arrived_at: float = arrived_at
        """:field
        If `target` is an integer object ID, move towards this bounds point of the object. Options: `"center"`, `"top`", `"bottom"`, `"left"`, `"right"`, `"front"`, `"back"`.
        """
        self.bounds_position: str = bounds_position
        self._turning: bool = True
        self._image_frequency: ImageFrequency = ImageFrequency.once
        self._move_by: Optional[MoveBy] = None
        self._previous_action: Optional[Action] = previous
        super().__init__()

    def get_initialization_commands(self, resp: List[bytes], dynamic: droneDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        # Remember the image frequency for both the turn and move sub-actions.
        self._image_frequency = image_frequency
        # Turn to the target.
        return TurnTo(target=self.target).get_initialization_commands(resp=resp,
                                                                      dynamic=dynamic,
                                                                      image_frequency=image_frequency)

    def get_ongoing_commands(self, resp: List[bytes], dynamic: droneDynamic) -> List[dict]:
        # Turning requires only one `communicate()` call. Now, it's time to start walking.
        if self._turning:
            self._turning = False
            # Get the target position.
            if isinstance(self.target, np.ndarray):
                target_position: np.ndarray = self.target
            elif isinstance(self.target, dict):
                target_position = TDWUtils.vector3_to_array(self.target)
            # If the target is and object ID, the target position is a bounds position.
            elif isinstance(self.target, int):
                target_position = np.zeros(shape=3)
                for i in range(len(resp) - 1):
                    # Get the output data ID.
                    r_id = OutputData.get_data_type_id(resp[i])
                    # Get the bounds data.
                    if r_id == "boun":
                        bounds = Bounds(resp[i])
                        for j in range(bounds.get_num()):
                            if bounds.get_id(j) == self.target:
                                bound = TDWUtils.get_bounds_dict(bounds, j)
                                target_position = bound[self.bounds_position].
                                break
                        break
            else:
                raise Exception(f"Invalid target: {self.target}")
            # Get the distance to the target. The distance is positive because we already turned to the target.
            distance = np.linalg.norm(dynamic.transform.position - target_position)
            # Start walking.
            self._move_by = MoveBy(distance=float(distance),
                                   dynamic=dynamic,
                                   collision_detection=self.collision_detection,
                                   previous=self._previous_action,
                                   arrived_at=self.arrived_at)
            commands = self._move_by.get_initialization_commands(resp=resp,
                                                                 dynamic=dynamic,
                                                                 image_frequency=self._image_frequency)
            self.status = self._move_by.status
            return commands
        # Keep walking.
        commands = self._move_by.get_ongoing_commands(resp=resp, dynamic=dynamic)
        self.status = self._move_by.status
        return commands

    def get_end_commands(self, resp: List[bytes], dynamic: droneDynamic,
                         image_frequency: ImageFrequency) -> List[dict]:
        if self._move_by is not None:
            return self._move_by.get_end_commands(resp=resp, dynamic=dynamic, image_frequency=image_frequency)
        else:
            return super().get_end_commands(resp=resp, dynamic=dynamic, image_frequency=image_frequency)
