from abc import ABC, abstractmethod
from typing import Optional, List, Dict
import numpy as np
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Overlap
from tdw.replicant.arm import Arm
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.actions.action import Action
from tdw.replicant.collision_detection import CollisionDetection
from tdw.replicant.image_frequency import ImageFrequency
from tdw.wheelchair_replicant.wheelchair_replicant_dynamic import WheelchairReplicantDynamic
from tdw.wheelchair_replicant.wheelchair_replicant_static import WheelchairReplicantStatic


class WheelchairMotion(Action, ABC):
    """
    Abstract base class for actions involving wheelchair motion (motor torques, brake torques, etc.)
    """

    """:class_var
    While moving or turning, the WheelchairReplicant will cast an overlap shape in the direction it is traveling. The overlap is used to detect object prior to collision (see `self.collision_detection.avoid_obstacles`). These are the half-extents of the overlap shape.
    """
    OVERLAP_HALF_EXTENTS: Dict[str, float] = {"x": 0.31875, "y": 0.8814, "z": 0.0875}

    def __init__(self, dynamic: WheelchairReplicantDynamic, collision_detection: CollisionDetection,
                 previous: Optional[Action], reset_arms: bool, reset_arms_duration: float,
                 scale_reset_arms_duration: bool, arrived_at: float, brake_at: float, brake_torque: float,
                 left_motor_torque: float, right_motor_torque: float, steer_angle: float):
        """
        :param dynamic: The [`WheelchairReplicantDynamic`](../wheelchair_replicant_dynamic.md) data that changes per `communicate()` call.
        :param collision_detection: The [`CollisionDetection`](../collision_detection.md) rules.
        :param previous: The previous action, if any.
        :param reset_arms: If True, reset the arms to their neutral positions while beginning to move.
        :param reset_arms_duration: The speed at which the arms are reset in seconds.
        :param scale_reset_arms_duration: If True, `reset_arms_duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        :param arrived_at: A distance or time determines whether the WheelchairReplicant arrived at the target.
        :param brake_at: Start to brake at this distance or angle.
        :param brake_torque: The torque that will be applied to the rear wheels at the end of the action.
        :param left_motor_torque: The torque that will be applied to the left rear wheel at the start of the action.
        :param right_motor_torque: The torque that will be applied to the right rear wheel at the start of the action.
        :param steer_angle: The steer angle in degrees that will applied to the front wheels at the start of the action.
        """

        super().__init__()
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
        """:field
        Start to brake at this distance or angle.
        """
        self.brake_at: float = brake_at
        """:field
        The torque that will be applied to the rear wheels at the end of the action.
        """
        self.brake_torque: float = brake_torque
        """:field
        The torque that will be applied to the left rear wheel at the start of the action.
        """
        self.left_motor_torque: float = left_motor_torque
        """:field
        The torque that will be applied to the right rear wheel at the start of the action.
        """
        self.right_motor_torque: float = right_motor_torque
        """:field
        The steer angle in degrees that will applied to the front wheels at the start of the action.
        """
        self.steer_angle: float = steer_angle
        self._braking: bool = False
        """:field
        The [`CollisionDetection`](../collision_detection.md) rules.
        """
        self.collision_detection: CollisionDetection = collision_detection
        if self._previous_was_collision(previous=previous):
            self.status = ActionStatus.collision
        # Ignore collision detection for held items.
        self.__held_objects: List[int] = [v for v in dynamic.held_objects.values() if
                                          v not in self.collision_detection.exclude_objects]
        self.collision_detection.exclude_objects.extend(self.__held_objects)

    def get_initialization_commands(self, resp: List[bytes],
                                    static: WheelchairReplicantStatic,
                                    dynamic: WheelchairReplicantDynamic,
                                    image_frequency: ImageFrequency) -> List[dict]:
        commands = super().get_initialization_commands(resp=resp, static=static, dynamic=dynamic,
                                                       image_frequency=image_frequency)
        self._initial_position = dynamic.transform.position
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
                          "left": self.left_motor_torque,
                          "right": self.right_motor_torque},
                         {"$type": "set_wheelchair_replicant_brake_torque",
                          "id": static.replicant_id,
                          "left": 0,
                          "right": 0},
                         {"$type": "set_wheelchair_replicant_steer_angle",
                          "id": static.replicant_id,
                          "angle": self.steer_angle}])
        return commands

    def get_ongoing_commands(self, resp: List[bytes], static: WheelchairReplicantStatic, dynamic: WheelchairReplicantDynamic) -> List[dict]:
        """
        Evaluate an action per-frame to determine whether it's done.

        :param resp: The response from the build.
        :param static: The [`WheelchairReplicantStatic`](../wheelchair_replicant_static.md) data that doesn't change after the Replicant is initialized.
        :param dynamic: The [`WheelchairReplicantStatic`](../wheelchair_replicant_dynamic.md) data that changes per `communicate()` call.

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
            return commands

    def get_end_commands(self, resp: List[bytes], static: WheelchairReplicantStatic, dynamic: WheelchairReplicantDynamic,
                         image_frequency: ImageFrequency) -> List[dict]:
        # Stop excluding held objects.
        for object_id in self.__held_objects:
            self.collision_detection.exclude_objects.remove(object_id)
        commands = super().get_end_commands(resp=resp, static=static, dynamic=dynamic, image_frequency=image_frequency)
        # Hit the brakes.
        commands.extend(self._get_brake_commands(replicant_id=static.replicant_id))
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
                {"$type": "set_wheelchair_replicant_brake_torque",
                 "id": replicant_id,
                 "left": self.brake_torque,
                 "right": self.brake_torque},
                {"$type": "set_wheelchair_replicant_steer_angle",
                 "id": replicant_id,
                 "angle": 0}]

    def _overlap(self, static: WheelchairReplicantStatic, dynamic: WheelchairReplicantDynamic) -> List[dict]:
        """
        :param static: The static Replicant data.
        :param dynamic: The dynamic Replicant data.

        :return: A list of commands to send an overlap box.
        """

        if not self.collision_detection.avoid:
            return []
        # Get the position of the overlap shape.
        overlap_position = dynamic.transform.position + self._get_overlap_direction(dynamic=dynamic)
        overlap_position[1] += 1
        # Send the next overlap command.
        return [{"$type": "send_overlap_box",
                 "id": static.replicant_id,
                 "half_extents": WheelchairMotion.OVERLAP_HALF_EXTENTS,
                 "rotation": TDWUtils.array_to_vector4(dynamic.transform.rotation),
                 "position": TDWUtils.array_to_vector3(overlap_position)}]

    @abstractmethod
    def _previous_was_collision(self, previous: Optional[Action]) -> bool:
        """
        :param previous: The previous action.

        :return: True if we should immediately set the status to collision.
        """

        raise Exception()

    @abstractmethod
    def _is_success(self, resp: List[bytes],
                    static: WheelchairReplicantStatic,
                    dynamic: WheelchairReplicantDynamic) -> bool:
        """
        :param resp: The response from the build.
        :param static: The `WheelchairReplicantStatic` data that doesn't change after the Replicant is initialized.
        :param dynamic: The `WheelchairReplicantStatic` data that changes per `communicate()` call.

        :return: True if the action ended in success.
        """

        raise Exception()

    @abstractmethod
    def _is_time_to_brake(self, resp: List[bytes],
                          static: WheelchairReplicantStatic,
                          dynamic: WheelchairReplicantDynamic) -> bool:
        """
        :param resp: The response from the build.
        :param static: The `WheelchairReplicantStatic` data that doesn't change after the Replicant is initialized.
        :param dynamic: The `WheelchairReplicantStatic` data that changes per `communicate()` call.

        :return: True if it's time to start braking.
        """
        raise Exception()

    @abstractmethod
    def _get_overlap_direction(self, dynamic: WheelchairReplicantDynamic) -> np.ndarray:
        """
        :param dynamic: The `WheelchairReplicantStatic` data that changes per `communicate()` call.

        :return: The overlap direction.
        """

        raise Exception()