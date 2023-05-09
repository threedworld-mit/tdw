from typing import Dict, List, Optional
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.drone.actions.action import Action
from tdw.drone.action_status import ActionStatus
from tdw.drone.drone_dynamic import droneDynamic
from tdw.drone.collision_detection import CollisionDetection
from tdw.drone.image_frequency import ImageFrequency
from tdw.output_data import OutputData, Overlap


class MoveBy(Action):
    """
    Fly a given distance.

    The action can end for several reasons depending on the collision detection rules (see [`self.collision_detection`](../collision_detection.md).

    - If the drone flys the target distance, the action succeeds.
    - If `self.collision_detection.previous_was_same == True`, and the previous action was `MoveBy` or `MoveTo`, and it was in the same direction (forwards/backwards), and the previous action ended in failure, this action ends immediately.
    - If `self.collision_detection.avoid_obstacles == True` and the drone encounters a wall or object in its path:
      - If the object is in `self.collision_detection.exclude_objects`, the drone ignores it.
      - Otherwise, the action ends in failure.
    - If the drone collides with an object or a wall and `self.collision_detection.objects == True` and/or `self.collision_detection.walls == True` respectively:
      - If the object is in `self.collision_detection.exclude_objects`, the drone ignores it.
      - Otherwise, the action ends in failure.
    - If the drone takes too long to reach the target distance, the action ends in failure (see `self.max_walk_cycles`).
    """

    def __init__(self, distance: float, dynamic: droneDynamic, collision_detection: CollisionDetection, arrived_at: float):
        """
        :param distance: The target distance. If less than 0, the drone will walk backwards.
        :param dynamic: The [`droneDynamic`](../drone_dynamic.md) data that changes per `communicate()` call.
        :param collision_detection: The [`CollisionDetection`](../collision_detection.md) rules.
        :param previous: The previous action, if any.
        :param arrived_at: If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful.
        """

        """:field
        The target distance. If less than 0, the drone will walk backwards.
        """
        self.distance: float = distance
        """:field
        If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful.
        """
        self.arrived_at: float = arrived_at
        super().__init__()

        self._destination: np.ndarray = dynamic.transform.position + (dynamic.transform.forward * distance)
        # Don't try to walk in the same direction twice.
        if self.collision_detection.previous_was_same and previous is not None and isinstance(previous, MoveBy) and \
                previous.status == ActionStatus.collision and np.sign(previous.distance) == np.sign(self.distance):
            self.status = ActionStatus.collision
        # The initial position. This is used to determine the distance traversed. This is set in `get_initialization_commands()`.
        self._initial_position: np.ndarray = np.zeros(shape=3)

    def get_initialization_commands(self, resp: List[bytes], dynamic: droneDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        self._initial_position = dynamic.transform.position
        return commands

    def get_ongoing_commands(self, resp: List[bytes], static: droneStatic, dynamic: droneDynamic) -> List[dict]:
        commands = super().get_ongoing_commands(resp=resp, dynamic=dynamic)
        # Reset the action status because we want to loop the animation.
        if self.status == ActionStatus.success:
            self.status = ActionStatus.ongoing
        if self.status != ActionStatus.ongoing:
            return commands
        else:
            distance_to_target = np.linalg.norm(dynamic.transform.position - self._destination)
            distance_traversed = np.linalg.norm(dynamic.transform.position - self._initial_position)
            # We arrived at the target.
            if distance_to_target < self.arrived_at or distance_traversed > abs(self.distance) - self.arrived_at:
                self.status = ActionStatus.success
            else:
                commands.extend(self._overlap(dynamic=dynamic))
                # Try to avoid obstacles by detecting them ahead of time by requesting an overlap shape.
                if self.collision_detection.avoid:
                    for i in range(len(resp) - 1):
                        r_id = OutputData.get_data_type_id(resp[i])
                        if r_id == "over":
                            overlap = Overlap(resp[i])
                            if overlap.get_id() == dynamic.drone_id:
                                # We detected a wall.
                                if overlap.get_env() and overlap.get_walls():
                                    self.status = ActionStatus.detected_obstacle
                                    return commands
                                object_ids = overlap.get_object_ids()
                                for object_id in object_ids:
                                    # We detected an object.
                                    if object_id != static.drone_id and object_id not in self.collision_detection.exclude_objects:
                                        self.status = ActionStatus.detected_obstacle
                                        return commands
            return commands

    def get_end_commands(self, resp: List[bytes], dynamic: droneDynamic,
                         image_frequency: ImageFrequency) -> List[dict]:
        return super().get_end_commands(resp=resp, dynamic=dynamic, image_frequency=image_frequency)

    def _overlap(self, dynamic: droneDynamic) -> List[dict]:
        """
        :param dynamic: The dynamic drone data.

        :return: A list of commands to send an overlap box.
        """

        if not self.collision_detection.avoid:
            return []
        # Get the position of the overlap shape.
        overlap_z = 0.5
        if self.distance < 0:
            overlap_z *= -1
        overlap_position = dynamic.transform.position + (dynamic.transform.forward * overlap_z)
        overlap_position[1] += 1
        # Send the next overlap command.
        return [{"$type": "send_overlap_box",
                 "id": dynamic.drone_id,
                 "half_extents": MoveBy.OVERLAP_HALF_EXTENTS,
                 "rotation": TDWUtils.array_to_vector4(dynamic.transform.rotation),
                 "position": TDWUtils.array_to_vector3(overlap_position)}]
