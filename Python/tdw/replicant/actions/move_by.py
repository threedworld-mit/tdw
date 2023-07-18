from typing import Dict, List, Optional
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.replicant.actions.animate import Animate
from tdw.replicant.actions.action import Action
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.collision_detection import CollisionDetection
from tdw.replicant.image_frequency import ImageFrequency
from tdw.replicant.replicant_body_part import ReplicantBodyPart
from tdw.replicant.arm import Arm
from tdw.output_data import OutputData, Overlap


class MoveBy(Animate):
    """
    Walk a given distance.

    The Replicant will continuously play a walk cycle animation until the action ends.

    The action can end for several reasons depending on the collision detection rules (see [`self.collision_detection`](../collision_detection.md).

    - If the Replicant walks the target distance, the action succeeds.
    - If `self.collision_detection.previous_was_same == True`, and the previous action was `MoveBy` or `MoveTo`, and it was in the same direction (forwards/backwards), and the previous action ended in failure, this action ends immediately.
    - If `self.collision_detection.avoid_obstacles == True` and the Replicant encounters a wall or object in its path:
      - If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
      - Otherwise, the action ends in failure.
    - If the Replicant collides with an object or a wall and `self.collision_detection.objects == True` and/or `self.collision_detection.walls == True` respectively:
      - If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
      - Otherwise, the action ends in failure.
    """

    # The body parts which will maintain IK positions and rotations, assuming `self.reset_arms == False`.
    _ARM_BODY_PARTS: List[str] = [ReplicantBodyPart.hand_l, ReplicantBodyPart.hand_r,
                                  ReplicantBodyPart.lowerarm_l, ReplicantBodyPart.lowerarm_r,
                                  ReplicantBodyPart.upperarm_l, ReplicantBodyPart.upperarm_r]

    def __init__(self, distance: float, dynamic: ReplicantDynamic, collision_detection: CollisionDetection,
                 previous: Optional[Action], reset_arms: bool, reset_arms_duration: float,
                 scale_reset_arms_duration: bool, arrived_at: float, collision_avoidance_distance: float,
                 collision_avoidance_half_extents: Dict[str, float], animation: str = "walking_2",
                 library: str = "humanoid_animations.json"):
        """
        :param distance: The target distance. If less than 0, the Replicant will walk backwards.
        :param dynamic: The [`ReplicantDynamic`](../replicant_dynamic.md) data that changes per `communicate()` call.
        :param collision_detection: The [`CollisionDetection`](../collision_detection.md) rules.
        :param previous: The previous action, if any.
        :param reset_arms: If True, reset the arms to their neutral positions while beginning the walk cycle.
        :param reset_arms_duration: The speed at which the arms are reset in seconds.
        :param scale_reset_arms_duration: If True, `reset_arms_duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        :param arrived_at: If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful.
        :param collision_avoidance_distance: If `collision_detection.avoid == True`, an overlap will be cast at this distance from the Wheelchair Replicant to detect obstacles.
        :param collision_avoidance_half_extents: If `collision_detection.avoid == True`, an overlap will be cast with these half extents to detect obstacles.
        :param animation: The name of the walk animation.
        :param library: The name of the walk animation's library.
        """

        """:field
        The target distance. If less than 0, the Replicant will walk backwards.
        """
        self.distance: float = distance
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
        If `collision_detection.avoid == True`, an overlap will be cast at this distance from the Wheelchair Replicant to detect obstacles.
        """
        self.collision_avoidance_distance: float = collision_avoidance_distance
        """:field
        If `collision_detection.avoid == True`, an overlap will be cast with these half extents to detect obstacles.
        """
        self.collision_avoidance_half_extents: Dict[str, float] = collision_avoidance_half_extents
        super().__init__(animation=animation,
                         collision_detection=collision_detection,
                         library=library,
                         previous=previous,
                         forward=self.distance > 0,
                         ik_body_parts=[] if self.reset_arms else MoveBy._ARM_BODY_PARTS,
                         loop=True)
        self._destination: np.ndarray = dynamic.transform.position + (dynamic.transform.forward * distance)
        # Don't try to walk in the same direction twice.
        if self.collision_detection.previous_was_same and previous is not None and isinstance(previous, MoveBy) and \
                previous.status == ActionStatus.collision and np.sign(previous.distance) == np.sign(self.distance):
            self.status = ActionStatus.collision
        # Ignore collision detection for held items.
        self.__held_objects: List[int] = [v for v in dynamic.held_objects.values() if v not in self.collision_detection.exclude_objects]
        self.collision_detection.exclude_objects.extend(self.__held_objects)
        # The initial position. This is used to determine the distance traversed. This is set in `get_initialization_commands()`.
        self._initial_position: np.ndarray = np.zeros(shape=3)

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        self._initial_position = dynamic.transform.position
        # Scale the reset arms motion duration.
        if self.scale_reset_arms_duration:
            self.reset_arms_duration = Action._get_scaled_duration(duration=self.reset_arms_duration, resp=resp)
        # Reset the arms.
        if self.reset_arms:
            commands.extend([{"$type": "replicant_reset_arm",
                              "id": static.replicant_id,
                              "duration": self.reset_arms_duration,
                              "arm": arm.name,
                              "set_status": False} for arm in Arm])
        # Reset the head.
        commands.append({"$type": "replicant_reset_head",
                         "id": static.replicant_id,
                         "set_status": False})
        # Request an initial overlap.
        commands.extend(self._overlap(static=static, dynamic=dynamic))
        return commands

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        commands = super().get_ongoing_commands(resp=resp, static=static, dynamic=dynamic)
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
            # Stop walking if there is a collision.
            elif len(dynamic.get_collision_enters(collision_detection=self.collision_detection)) > 0:
                self.status = ActionStatus.collision
            else:
                commands.extend(self._overlap(static=static, dynamic=dynamic))
                # Try to avoid obstacles by detecting them ahead of time by requesting an overlap shape.
                if self.collision_detection.avoid:
                    for i in range(len(resp) - 1):
                        r_id = OutputData.get_data_type_id(resp[i])
                        if r_id == "over":
                            overlap = Overlap(resp[i])
                            if overlap.get_id() == static.replicant_id:
                                # We detected a wall.
                                if overlap.get_env() and overlap.get_walls():
                                    self.status = ActionStatus.detected_obstacle
                                    return commands
                                object_ids = overlap.get_object_ids()
                                for object_id in object_ids:
                                    # We detected an object.
                                    if object_id != static.replicant_id and object_id not in self.collision_detection.exclude_objects:
                                        self.status = ActionStatus.detected_obstacle
                                        return commands
            return commands

    def get_end_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                         image_frequency: ImageFrequency) -> List[dict]:
        # Stop excluding held objects.
        for object_id in self.__held_objects:
            self.collision_detection.exclude_objects.remove(object_id)
        return super().get_end_commands(resp=resp, static=static, dynamic=dynamic, image_frequency=image_frequency)

    def _overlap(self, static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        """
        :param static: The static Replicant data.
        :param dynamic: The dynamic Replicant data.

        :return: A list of commands to send an overlap box.
        """

        if not self.collision_detection.avoid:
            return []
        # Get the position of the overlap shape.
        overlap_z = self.collision_avoidance_distance
        if self.distance < 0:
            overlap_z *= -1
        overlap_position = dynamic.transform.position + (dynamic.transform.forward * overlap_z)
        overlap_position[1] += 1
        # Send the next overlap command.
        return [{"$type": "send_overlap_box",
                 "id": static.replicant_id,
                 "half_extents": self.collision_avoidance_half_extents,
                 "rotation": TDWUtils.array_to_vector4(dynamic.transform.rotation),
                 "position": TDWUtils.array_to_vector3(overlap_position)}]
