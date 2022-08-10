from typing import List, Union, Dict
from pathlib import Path
from tdw.add_ons.add_on import AddOn
from tdw.tdw_utils import TDWUtils
from tdw.librarian import HumanoidAnimationLibrarian, HumanoidLibrarian
from tdw.output_data import OutputData, Transforms
from random import uniform
import os
from math import ceil
import numpy as np
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.replicant_utils import ReplicantUtils
from tdw.replicant.actions.action import Action
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.actions.turn_by import TurnBy
from tdw.replicant.actions.turn_to import TurnTo
from tdw.replicant.actions.move_by import MoveBy
from tdw.replicant.actions.move_to import MoveTo

class Replicant(AddOn):

    def __init__(self, replicant_id: int = 0, position: Dict[str, float] = None, rotation: Dict[str, float] = None,
                 image_frequency: ImageFrequency = ImageFrequency.once):
        """
        :param replicant_id: The ID of the replicant.
        :param position: The position of the replicant. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param rotation: The rotation of the replicant in Euler angles (degrees). If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param image_frequency: [The frequency of image capture.](image_frequency.md)

        """

        super().__init__()
        self.walk_record = HumanoidAnimationLibrarian().get_record("walking_2")
        if position is None:
            """:field
            The initial position of the replicant.
            """
            self.initial_position: Dict[str, float] = {"x": 0, "y": 0, "z": 0}
        else:
            self.initial_position: Dict[str, float] = position
        if rotation is None:
            """:field
            The initial rotation of the replicant.
            """
            self.initial_rotation: Dict[str, float] = {"x": 0, "y": 0, "z": 0}
        else:
            self.initial_rotation: Dict[str, float] = rotation
        """:field
        The ID of this replicant.
        """
        self.replicant_id: int = replicant_id
        """:field
        The Magnebot's current [action](actions/action.md). Can be None (no ongoing action).
        """
        self.action: Optional[Action] = None
        """:field
        This sets [how often images are captured](image_frequency.md).
        """
        self.image_frequency: ImageFrequency = image_frequency
        """:field
        [The collision detection rules.](collision_detection.md) This determines whether the Magnebot will immediately stop moving or turning when it collides with something.
        """
        self.collision_detection: CollisionDetection = CollisionDetection()
        """:field
        The current (roll, pitch, yaw) angles of the Magnebot's camera in degrees as a numpy array. This is handled outside of `self.state` because it isn't calculated using output data from the build. See: `Magnebot.CAMERA_RPY_CONSTRAINTS` and `self.rotate_camera()`
        """
        self.camera_rpy: np.array = np.array([0, 0, 0])
        self._previous_resp: List[bytes] = list()
        self._previous_action: Optional[Action] = None


    # **<Probably add send_collisions here also>**
    def get_initialization_commands(self) -> List[dict]:
        commands = [{"$type": "set_target_framerate", "framerate": self.walk_record.framerate},
                    {"$type": "add_humanoid",
                      "name": "ha_proto_v1a",
                       "position": self.initial_position,
                       "rotation": self.initial_rotation,
                       "url": "file:///" + "D://TDW_Strategic_Plan_2021//Humanoid_Agent//HumanoidAgent_proto_V1//AssetBundles//Windows//non_t_pose",
                       "id": self.replicant_id},
                    self.get_add_humanoid_animation(humanoid_animation_name=self.walk_record.name)[0],
                    {"$type": "send_humanoids",
                           "ids": [self.replicant_id,
                           "frequency": "always"},
                    {"$type": "send_transforms",
                           "frequency": "always"}]
        return commands

    def on_send(self, resp: List[bytes]) -> None:
        """
        This is called after commands are sent to the build and a response is received.

        This function is called automatically by the controller; you don't need to call it yourself.

        :param resp: The response from the build.
        """

        super().on_send(resp=resp)
        self._previous_resp = resp
        if self.action is None or self.action.done:
            return
        else:
            if not self.action.initialized:
                # Some actions can fail immediately.
                if self.action.status == ActionStatus.ongoing:
                    self.action.initialized = True
                    initialization_commands = self.action.get_initialization_commands(resp=resp, static=self.static,
                                                                                      dynamic=self.dynamic, image_frequency=self.image_frequency)
                    # This is an ongoing action.
                    if self.action.status == ActionStatus.ongoing:
                        self.commands.extend(initialization_commands)
                        # Set the status after initialization.
                        # This is required from one-frame actions such as RotateCamera.
                        self.action.set_status_after_initialization()
                        # This action is done. Append end commands.
                        if self.action.status != ActionStatus.ongoing:
                            self.commands.extend(self.action.get_end_commands(resp=resp,
                                                                              static=self.static,
                                                                              dynamic=self.dynamic,
                                                                              image_frequency=self.image_frequency))
            else:
                action_commands = self.action.get_ongoing_commands(resp=resp, static=self.static, dynamic=self.dynamic)
                # This is an ongoing action. Append ongoing commands.
                if self.action.status == ActionStatus.ongoing:
                    self.commands.extend(action_commands)
                # This action is done. Append end commands.
                else:
                    self.commands.extend(self.action.get_end_commands(resp=resp,
                                                                      static=self.static,
                                                                      dynamic=self.dynamic,
                                                                      image_frequency=self.image_frequency))
            # This action ended. Remember it as the previous action.
            if self.action.status != ActionStatus.ongoing:
                # Mark the action as done.
                self.action.done = True
                # Remember the previous action.
                self._previous_action = deepcopy(self.action)


    def turn_by(self, angle: float, aligned_at: float = 1) -> None:
        """
        Turn the Magnebot by an angle.

        While turning, the left wheels will turn one way and the right wheels in the opposite way, allowing the Magnebot to turn in place.

        :param angle: The target angle in degrees. Positive value = clockwise turn.
        :param aligned_at: If the difference between the current angle and the target angle is less than this value, then the action is successful.
        """

        self.action = TurnBy(angle=angle, aligned_at=aligned_at, collision_detection=self.collision_detection,
                             previous=self._previous_action, dynamic=self.dynamic)

    def turn_to(self, target: Union[int, Dict[str, float], np.ndarray], aligned_at: float = 1) -> None:
        """
        Turn the Magnebot to face a target object or position.

        While turning, the left wheels will turn one way and the right wheels in the opposite way, allowing the Magnebot to turn in place.

        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        :param aligned_at: If the difference between the current angle and the target angle is less than this value, then the action is successful.
        """

        self.action = TurnTo(target=target, resp=self._previous_resp, aligned_at=aligned_at,
                             collision_detection=self.collision_detection, previous=self._previous_action,
                             dynamic=self.dynamic)

    def move_by(self, distance: float, arrived_at: float = 0.1) -> None:
        """
        Move the Magnebot forward or backward by a given distance.

        :param distance: The target distance. If less than zero, the Magnebot will move backwards.
        :param arrived_at: If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful.
        """

        self.action = MoveBy(distance=distance, arrived_at=arrived_at, collision_detection=self.collision_detection,
                             previous=self._previous_action, dynamic=self.dynamic)

    def move_to(self, target: Union[int, Dict[str, float], np.ndarray], arrived_at: float = 0.1, aligned_at: float = 1,
                arrived_offset: float = 0) -> None:
        """
        Move to a target object or position. This combines turn_to() followed by move_by().

        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        :param arrived_at: If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful.
        :param aligned_at: If the difference between the current angle and the target angle is less than this value, then the action is successful.
        :param arrived_offset: Offset the arrival position by this value. This can be useful if the Magnebot needs to move to an object but shouldn't try to move to the object's centroid. This is distinct from `arrived_at` because it won't affect the Magnebot's braking solution.
        """

        self.action = MoveTo(target=target, resp=self._previous_resp, dynamic=self.dynamic,
                             collision_detection=self.collision_detection, arrived_at=arrived_at, aligned_at=aligned_at,
                             arrived_offset=arrived_offset, previous=self._previous_action)


        