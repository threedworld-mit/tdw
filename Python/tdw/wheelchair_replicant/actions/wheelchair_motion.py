from abc import ABC, abstractmethod
from typing import Optional, List, Dict
import numpy as np
from tdw.type_aliases import TARGET
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Overlap
from tdw.replicant.arm import Arm
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.actions.action import Action
from tdw.replicant.collision_detection import CollisionDetection
from tdw.replicant.image_frequency import ImageFrequency
from tdw.wheelchair_replicant.wheel_values import WheelValues


class WheelchairMotion(Action, ABC):
    """
    Abstract base class for actions involving wheelchair motion (motor torques, brake torques, etc.)
    """

    def __init__(self, wheel_values: WheelValues, dynamic: ReplicantDynamic, collision_detection: CollisionDetection,
                 previous: Optional[Action], reset_arms: bool, reset_arms_duration: float,
                 scale_reset_arms_duration: bool, arrived_at: float, collision_avoidance_distance: float,
                 collision_avoidance_half_extents: Dict[str, float]):
        """
        :param wheel_values: The [`WheelValues`](../wheel_values.md) that will be applied to the wheelchair's wheels.
        :param dynamic: The [`ReplicantDynamic`](../../replicant/replicant_dynamic.md) data that changes per `communicate()` call.
        :param collision_detection: The [`CollisionDetection`](../../replicant/collision_detection.md) rules.
        :param previous: The previous action, if any.
        :param reset_arms: If True, reset the arms to their neutral positions while beginning to move.
        :param reset_arms_duration: The speed at which the arms are reset in seconds.
        :param scale_reset_arms_duration: If True, `reset_arms_duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        :param arrived_at: A distance or time determines whether the WheelchairReplicant arrived at the target.
        :param collision_avoidance_distance: If `collision_detection.avoid == True`, an overlap will be cast at this distance from the Wheelchair Replicant to detect obstacles.
        :param collision_avoidance_half_extents: If `collision_detection.avoid == True`, an overlap will be cast with these half extents to detect obstacles.
        """

        super().__init__()
        """:field
        The [`WheelValues`](../wheel_values.md) that will be applied to the wheelchair's wheels.
        """
        self.wheel_values: WheelValues = wheel_values
        """:field
        If True, reset the arms to their neutral positions while beginning to move.
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
        A distance or time determines whether the WheelchairReplicant arrived at the target.
        """
        self.arrived_at: float = arrived_at
        self._braking: bool = False
        """:field
        The [`CollisionDetection`](../collision_detection.md) rules.
        """
        self.collision_detection: CollisionDetection = collision_detection
        """:field
        If `collision_detection.avoid == True`, an overlap will be cast at this distance from the Wheelchair Replicant to detect obstacles.
        """
        self.collision_avoidance_distance: float = collision_avoidance_distance
        """:field
        If `collision_detection.avoid == True`, an overlap will be cast with these half extents to detect obstacles.
        """
        self.collision_avoidance_half_extents: Dict[str, float] = collision_avoidance_half_extents
        if self._previous_was_collision(previous=previous):
            self.status = ActionStatus.collision
        # Ignore collision detection for held items.
        self.__held_objects: List[int] = [v for v in dynamic.held_objects.values() if
                                          v not in self.collision_detection.exclude_objects]
        self.collision_detection.exclude_objects.extend(self.__held_objects)
        self._frame: int = 0

    def get_initialization_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        """
        :param resp: The response from the build.
        :param static: The [`ReplicantStatic`](../../replicant/replicant_static.md) data that doesn't change after the Replicant is initialized.
        :param dynamic: The [`ReplicantDynamic`](../../replicant/replicant_dynamic.md) data that changes per `communicate()` call.
        :param image_frequency: An [`ImageFrequency`](../../replicant/image_frequency.md) value describing how often image data will be captured.

        :return: A list of commands to initialize this action.
        """

        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        # Scale the reset arms motion duration.
        if self.scale_reset_arms_duration:
            self.reset_arms_duration = Action._get_scaled_duration(duration=self.reset_arms_duration, resp=resp)
        # Reset the arms.
        if self.reset_arms:
            commands.extend([{"$type": "wheelchair_replicant_reset_arm",
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
        # Set the motor torques, brake torques, and steer angles.
        commands.extend([{"$type": "set_wheelchair_motor_torque",
                          "id": static.replicant_id,
                          "left": self.wheel_values.left_motor_torque,
                          "right": self.wheel_values.right_motor_torque},
                         {"$type": "set_wheelchair_brake_torque",
                          "id": static.replicant_id,
                          "torque": 0},
                         {"$type": "set_wheelchair_steer_angle",
                          "id": static.replicant_id,
                          "angle": self.wheel_values.steer_angle}])
        return commands

    def get_ongoing_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        """
        Evaluate an action per-frame to determine whether it's done.

        :param resp: The response from the build.
        :param static: The [`ReplicantStatic`](../../replicant/replicant_static.md) data that doesn't change after the Replicant is initialized.
        :param dynamic: The [`ReplicantDynamic`](../../replicant/replicant_dynamic.md) data that changes per `communicate()` call.

        :return: A list of commands to send to the build to continue the action.
        """

        commands = super().get_ongoing_commands(resp=resp, static=static, dynamic=dynamic)
        if self.status != ActionStatus.ongoing:
            return commands
        else:
            if self._is_success(resp=resp, static=static, dynamic=dynamic):
                self.status = ActionStatus.success
                commands.extend(self._get_brake_commands(replicant_id=static.replicant_id))
            # Stop moving if there is a collision.
            elif len(dynamic.get_collision_enters(collision_detection=self.collision_detection)) > 0:
                self.status = ActionStatus.collision
            else:
                # Start braking.
                if not self._braking and self._is_time_to_brake(resp=resp, static=static, dynamic=dynamic):
                    self._braking = True
                    commands.extend(self._get_brake_commands(replicant_id=static.replicant_id))
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
                                object_ids = overlap.get_object_ids()
                                for object_id in object_ids:
                                    # We detected an object.
                                    if object_id != static.replicant_id and object_id not in self.collision_detection.exclude_objects:
                                        self.status = ActionStatus.detected_obstacle
                                        commands.extend(self._get_brake_commands(replicant_id=static.replicant_id))
            # Wait a few frames for the wheelchair to start moving.
            if self._frame < 100:
                self._frame += 1
            else:
                # The wheelchair isn't moving.
                if self._is_failure(dynamic=dynamic):
                    self.status = self._get_fail_status()
                # Continue the action.
                else:
                    self._continue_action(dynamic=dynamic)
            return commands

    def get_end_commands(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic,
                         image_frequency: ImageFrequency) -> List[dict]:
        """
        :param resp: The response from the build.
        :param static: The [`ReplicantStatic`](../../replicant/replicant_static.md) data that doesn't change after the Replicant is initialized.
        :param dynamic: The [`ReplicantDynamic`](../../replicant/replicant_dynamic.md) data that changes per `communicate()` call.
        :param image_frequency: An [`ImageFrequency`](../../replicant/image_frequency.md) value describing how often image data will be captured.

        :return: A list of commands that must be sent to end any action.
        """

        # Stop excluding held objects.
        for object_id in self.__held_objects:
            self.collision_detection.exclude_objects.remove(object_id)
        commands = super().get_end_commands(resp=resp, static=static, dynamic=dynamic, image_frequency=image_frequency)
        # Hit the brakes.
        commands.extend(self._get_brake_commands(replicant_id=static.replicant_id))
        commands.append({"$type": "set_wheelchair_steer_angle",
                         "id": static.replicant_id,
                         "angle": 0})
        return commands

    def _get_brake_commands(self, replicant_id: int) -> List[dict]:
        """
        Set the motor torques to 0 and the brake torques to `brake_torque`.

        :param replicant_id: The ID of this Replicant.

        :return: A list of commands.
        """

        return [{"$type": "set_wheelchair_motor_torque",
                 "id": replicant_id,
                 "left": 0,
                 "right": 0},
                {"$type": "set_wheelchair_brake_torque",
                 "id": replicant_id,
                 "torque": self.wheel_values.brake_torque}]

    def _overlap(self, static: ReplicantStatic, dynamic: ReplicantDynamic) -> List[dict]:
        """
        :param static: The static Replicant data.
        :param dynamic: The dynamic Replicant data.

        :return: A list of commands to send an overlap box.
        """

        if not self.collision_detection.avoid:
            return []
        # Get the position of the overlap shape.
        overlap_position = dynamic.transform.position + self._get_overlap_direction(dynamic=dynamic)
        overlap_position[1] = 0
        # Send the next overlap command.
        return [{"$type": "send_overlap_box",
                 "id": static.replicant_id,
                 "half_extents": self.collision_avoidance_half_extents,
                 "rotation": TDWUtils.array_to_vector4(dynamic.transform.rotation),
                 "position": TDWUtils.array_to_vector3(overlap_position)}]

    @staticmethod
    def _get_target_array(target: TARGET, resp: List[bytes]) -> np.ndarray:
        """
        :param target: A target object, numpy array position, or dictionary position.
        :param resp: The response from the build.

        :return: A target numpy array position.
        """

        # Get the target position.
        if isinstance(target, int):
            return WheelchairMotion._get_object_position(object_id=target, resp=resp)
        elif isinstance(target, dict):
            return TDWUtils.vector3_to_array(target)
        elif isinstance(target, np.ndarray):
            return target
        else:
            raise Exception(f"Invalid target: {target}")

    @abstractmethod
    def _get_fail_status(self) -> ActionStatus:
        """
        :return: The ActionStatus when the action fails.
        """

        raise Exception()

    @abstractmethod
    def _previous_was_collision(self, previous: Optional[Action]) -> bool:
        """
        :param previous: The previous action.

        :return: True if we should immediately set the status to collision.
        """

        raise Exception()

    @abstractmethod
    def _is_success(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> bool:
        """
        :param resp: The response from the build.
        :param static: The `ReplicantStatic` data that doesn't change after the Replicant is initialized.
        :param dynamic: The `ReplicantDynamic` data that changes per `communicate()` call.

        :return: True if the action ended in success.
        """

        raise Exception()

    @abstractmethod
    def _is_time_to_brake(self, resp: List[bytes], static: ReplicantStatic, dynamic: ReplicantDynamic) -> bool:
        """
        :param resp: The response from the build.
        :param static: The `ReplicantStatic` data that doesn't change after the Replicant is initialized.
        :param dynamic: The `ReplicantDynamic` data that changes per `communicate()` call.

        :return: True if it's time to start braking.
        """
        raise Exception()

    @abstractmethod
    def _get_overlap_direction(self, dynamic: ReplicantDynamic) -> np.ndarray:
        """
        :param dynamic: The `ReplicantDynamic` data that changes per `communicate()` call.

        :return: The overlap direction.
        """

        raise Exception()

    @abstractmethod
    def _is_failure(self, dynamic: ReplicantDynamic) -> bool:
        """
        :param dynamic: The `ReplicantDynamic` data that changes per `communicate()` call.

        :return: True if the action failed.
        """

        raise Exception()

    def _continue_action(self, dynamic: ReplicantDynamic):
        """
        Do something to continue the action if it didn't fail.

        :param dynamic: The `ReplicantDynamic` data that changes per `communicate()` call.
        """

        raise Exception()
