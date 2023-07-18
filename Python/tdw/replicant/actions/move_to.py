from typing import List, Optional, Dict
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.type_aliases import TARGET
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

    While walking, the Replicant will continuously play a walk cycle animation until the action ends.

    The action can end for several reasons depending on the collision detection rules (see [`self.collision_detection`](../collision_detection.md).

    - If the Replicant walks the target distance (i.e. it reaches its target), the action succeeds.
    - If `self.collision_detection.previous_was_same == True`, and the previous action was `MoveBy` or `MoveTo`, and it was in the same direction (forwards/backwards), and the previous action ended in failure, this action ends immediately.
    - If `self.collision_detection.avoid_obstacles == True` and the Replicant encounters a wall or object in its path:
      - If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
      - Otherwise, the action ends in failure.
    - If the Replicant collides with an object or a wall and `self.collision_detection.objects == True` and/or `self.collision_detection.walls == True` respectively:
      - If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
      - Otherwise, the action ends in failure.
    """

    def __init__(self, target: TARGET, collision_detection: CollisionDetection, previous: Optional[Action],
                 reset_arms: bool, reset_arms_duration: float, scale_reset_arms_duration: bool, arrived_at: float,
                 bounds_position: str, collision_avoidance_distance: float,
                 collision_avoidance_half_extents: Dict[str, float], animation: str = "walking_2",
                 library: str = "humanoid_animations.json"):
        """
        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        :param collision_detection: The [`CollisionDetection`](../collision_detection.md) rules.
        :param previous: The previous action, if any.
        :param reset_arms: If True, reset the arms to their neutral positions while beginning the walk cycle.
        :param reset_arms_duration: The speed at which the arms are reset in seconds.
        :param reset_arms_duration: The speed at which the arms are reset in seconds.
        :param arrived_at: If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful.
        :param bounds_position: If `target` is an integer object ID, move towards this bounds point of the object. Options: `"center"`, `"top`", `"bottom"`, `"left"`, `"right"`, `"front"`, `"back"`.
        :param collision_avoidance_distance: If `collision_detection.avoid == True`, an overlap will be cast at this distance from the Wheelchair Replicant to detect obstacles.
        :param collision_avoidance_half_extents: If `collision_detection.avoid == True`, an overlap will be cast with these half extents to detect obstacles.
        :param animation: The name of the walk animation.
        :param library: The name of the walk animation's library.
        """

        """:field
        The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        """
        self.target: TARGET = target
        """:field
        The [`CollisionDetection`](../collision_detection.md) rules.
        """
        self.collision_detection: CollisionDetection = collision_detection
        """:field
        If True, reset the arms to their neutral positions while beginning the walk cycle.
        """
        self.reset_arms: bool = reset_arms
        """:field
        The speed at which the arms are reset in seconds.
        """
        self.reset_arms_duration: float = reset_arms_duration
        """:field
        If True, `reset_arms_duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        """
        self.scale_reset_arms_duration: bool = scale_reset_arms_duration
        """:field
        If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful.
        """
        self.arrived_at: float = arrived_at
        """:field
        If `target` is an integer object ID, move towards this bounds point of the object. Options: `"center"`, `"top`", `"bottom"`, `"left"`, `"right"`, `"front"`, `"back"`.
        """
        self.bounds_position: str = bounds_position
        """:field
        The name of the walk animation.
        """
        self.animation: str = animation
        """:field
        The name of the walk animation's library.
        """
        self.library: str = library
        """:field
        If `collision_detection.avoid == True`, an overlap will be cast at this distance from the Wheelchair Replicant to detect obstacles.
        """
        self.collision_avoidance_distance: float = collision_avoidance_distance
        """:field
        If `collision_detection.avoid == True`, an overlap will be cast with these half extents to detect obstacles.
        """
        self.collision_avoidance_half_extents: Dict[str, float] = collision_avoidance_half_extents
        self._turning: bool = True
        self._image_frequency: ImageFrequency = ImageFrequency.once
        self._move_by: Optional[MoveBy] = None
        self._previous_action: Optional[Action] = previous
        super().__init__()

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        # Remember the image frequency for both the turn and move sub-actions.
        self._image_frequency = image_frequency
        # Turn to the target.
        return TurnTo(target=self.target).get_initialization_commands(resp=resp,
                                                                      static=static,
                                                                      dynamic=dynamic,
                                                                      image_frequency=image_frequency)

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
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
                                target_position = bound[self.bounds_position]
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
                                   reset_arms=self.reset_arms,
                                   reset_arms_duration=self.reset_arms_duration,
                                   scale_reset_arms_duration=self.scale_reset_arms_duration,
                                   arrived_at=self.arrived_at,
                                   collision_avoidance_distance=self.collision_avoidance_distance,
                                   collision_avoidance_half_extents=self.collision_avoidance_half_extents,
                                   animation=self.animation,
                                   library=self.library)
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
