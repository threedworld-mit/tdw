from typing import List, Union, Dict
from typing import List, Optional, Dict, Union
from copy import deepcopy
from pathlib import Path
from tdw.add_ons.add_on import AddOn
from tdw.tdw_utils import TDWUtils
from tdw.output_data import OutputData, Transforms
from tdw.add_ons.container_manager import ContainerManager
from random import uniform
import os
from math import ceil
import numpy as np
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
from tdw.replicant.replicant_utils import ReplicantUtils
from tdw.replicant.collision_detection import CollisionDetection
from tdw.replicant.actions.action import Action
from tdw.replicant.action_status import ActionStatus
from tdw.replicant.actions.turn_by import TurnBy
from tdw.replicant.actions.turn_to import TurnTo
from tdw.replicant.actions.move_by import MoveBy
from tdw.replicant.actions.move_to import MoveTo
from tdw.replicant.actions.reach_for import ReachFor
from tdw.replicant.actions.grasp import Grasp
from tdw.replicant.actions.drop import Drop
from tdw.replicant.actions.reset_arm import ResetArm
from tdw.replicant.actions.perform_action_sequence import PerformActionSequence
from tdw.replicant.image_frequency import ImageFrequency
from tdw.replicant.arm import Arm

class Replicant(AddOn):

    def __init__(self, replicant_id: int = 0, position: Dict[str, float] = None, rotation: Dict[str, float] = None,
                 image_frequency: ImageFrequency = ImageFrequency.once, avoid_objects: bool = False):
        """
        :param replicant_id: The ID of the replicant.
        :param position: The position of the replicant. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param rotation: The rotation of the replicant in Euler angles (degrees). If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param image_frequency: [The frequency of image capture.](image_frequency.md)

        """
        super().__init__()
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

        self.static: Optional[ReplicantStatic] = None
        self.dynamic: Optional[ReplicantDynamic] = None

        """:field
        The ID of this replicant.
        """
        self.replicant_id: int = replicant_id
        """:field
        The Replicant's current [action](actions/action.md). Can be None (no ongoing action).
        """
        self.action: Optional[Action] = None
        """:field
        This sets [how often images are captured](image_frequency.md).
        """
        self.image_frequency: ImageFrequency = image_frequency
        """:field
        [The collision detection rules.](collision_detection.md) This determines whether the Replicant will immediately stop moving or turning when it collides with something.
        """
        self.collision_detection: CollisionDetection = CollisionDetection()
        """:field
        The current (roll, pitch, yaw) angles of the Replicant's camera in degrees as a numpy array. This is handled outside of `self.state` because it isn't calculated using output data from the build. See: `Replicant.CAMERA_RPY_CONSTRAINTS` and `self.rotate_camera()`
        """
        """:field
        A dictionary of object IDs currently held by the Replicant. Key = The arm. Value = a list of object IDs.
        """
        self.held: Dict[Arm, List[int]] = {Arm.left: [], Arm.right: [], Arm.both: []}
        """:field
        Whether this replicant should avoid other objects in the scene.
        """
        self.avoid_objects: bool = avoid_objects

        self.camera_rpy: np.array = np.array([0, 0, 0])
        self._previous_resp: List[bytes] = list()
        self._previous_action: Optional[Action] = None
        # Create a container manager.
        self.container_manager = ContainerManager()


    def get_initialization_commands(self) -> List[dict]:
        commands = [{"$type": "add_replicant",
                      "name": "replicant",
                      "position": self.initial_position,
                      "rotation": self.initial_rotation,
                      "url": "file:///" + "D://TDW_Strategic_Plan_2021//Humanoid_Agent//HumanoidAgent_proto_V1//AssetBundles//Windows//non_t_pose",
                      #"url": "file:///" + "D://TDW_Strategic_Plan_2021//Humanoid_Agent//HumanoidAgent_proto_V1//AssetBundles//Windows//replicant",
                      "id": self.replicant_id},
                    {"$type": "send_replicants",
                     "frequency": "always"},
                    {"$type": "send_transforms",
                     "frequency": "always"},
                    {"$type": "send_empty_transforms",
                     "frequency": "always"},
                    {"$type": "send_collisions",
                              "enter": True,
                              "stay": False,
                              "exit": True,
                              "collision_types": ["obj", "env"]}]
        # Add the container manager's initialization commands.
        commands.extend(self.container_manager.get_initialization_commands())
        # Mark the container manager as initialized.
        self.container_manager.initialized = True
        return commands

    def on_send(self, resp: List[bytes]) -> None:
        """
        This is called after commands are sent to the build and a response is received.

        This function is called automatically by the controller; you don't need to call it yourself.

        :param resp: The response from the build.
        """
        self.container_manager.on_send(resp=resp)
        if self.static is None:
            self._cache_static_data(resp=resp)
        self._set_dynamic_data(resp=resp)

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
        # Append the container manager's commands.
        self.commands.extend(self.container_manager.commands)
        self.container_manager.commands.clear()


    def turn_by(self, angle: float, aligned_at: float = 1) -> None:
        """
        Turn the Replicant by an angle.

        :param angle: The target angle in degrees. Positive value = clockwise turn.
        :param aligned_at: If the difference between the current angle and the target angle is less than this value, then the action is successful.
        """

        self.action = TurnBy(angle=angle, resp=self._previous_resp, aligned_at=aligned_at, collision_detection=self.collision_detection,
                             previous=self._previous_action, dynamic=self.dynamic)

    def turn_to(self, target: Union[int, Dict[str, float]], forward: bool = True) -> None:
        """
        Turn the Replicant to face a target object or position.

        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        """

        self.action = TurnTo(target=target, forward=forward, resp=self._previous_resp, collision_detection=self.collision_detection,
                             previous=self._previous_action, dynamic=self.dynamic)

    def move_by(self, distance: float, arrived_at: float = 0.1, forward: bool = True) -> None:
        """
        Move the Replicant forward by a given distance.

        :param distance: The target distance. 
        :param arrived_at: If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful.
        """

        self.action = MoveBy(distance=distance, arrived_at=arrived_at, forward=forward, collision_detection=self.collision_detection,
                              held_objects=self.held, avoid_objects = self.avoid_objects, previous=self._previous_action, dynamic=self.dynamic)

    def move_to(self, target: Union[int, Dict[str, float]], arrived_at: float = 0.1, aligned_at: float = 1,
                arrived_offset: float = 0, target_offset: str = "center", forward:bool = True) -> None:
        """
        Move to a target object or position. This combines turn_to() followed by move_by().

        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. 
        :param arrived_at: If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful.
        :param aligned_at: If the difference between the current angle and the target angle is less than this value, then the action is successful.
        :param arrived_offset: Offset the arrival position by this value. This can be useful if the Replicant needs to move to an object but shouldn't try to move to the object's centroid. This is distinct from `arrived_at` because it won't affect the Replicant's braking solution.
        """

        self.action = MoveTo(target=target, resp=self._previous_resp, dynamic=self.dynamic,
                             collision_detection=self.collision_detection, held_objects=self.held, 
                             avoid_objects=self.avoid_objects, target_offset=target_offset, forward=forward, 
                             arrived_at=arrived_at, aligned_at=aligned_at, arrived_offset=arrived_offset, 
                             previous=self._previous_action)

    def reach_for(self, target: Union[int, Dict[str,  float]], arm: Arm, use_other_arm: bool, reverse_reach: bool = False) -> None:
        """
        Reach for a target object or position.

        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. 
        :param arm: Which arm the Replicant is reaching with -- left, right or both.
        :param use_other_arm: Whether to use the other arm for reaching, if the Replicant is holding an object with the selected arm.
        :param reverse_reach: Whether the replicant is carrying one end of an object, held behind it.
        """

        self.action = ReachFor(target=target, resp=self._previous_resp, arm=arm, static=self.static, dynamic=self.dynamic,
                               collision_detection=self.collision_detection, held_objects=self.held, reverse_reach=reverse_reach,
                               previous=self._previous_action, use_other_arm=use_other_arm)

    def grasp(self, target: int, arm: Arm, use_other_arm: bool) -> None:
        """
        Grasp a target object.

        :param target: The target. 
        :param arm: Which arm the Replicant is grasping with -- left, right or both.
        :param use_other_arm: Whether to use the other arm for reaching, if the Replicant is holding an object with the selected arm.
        """

        self.action = Grasp(target=target, resp=self._previous_resp, arm=arm, static=self.static, dynamic=self.dynamic,
                               collision_detection=self.collision_detection, held_objects=self.held, previous=self._previous_action, use_other_arm=use_other_arm)

    def drop(self, target: int, arm: Arm) -> None:
        """
        Drop a held target object.

        :param target: The target object ID. 
        :param arm: Which arm the Replicant is holding the object -- left, right or both.
        """

        self.action = Drop(target=target, resp=self._previous_resp, arm=arm, static=self.static, dynamic=self.dynamic,
                               collision_detection=self.collision_detection, held_objects=self.held, previous=self._previous_action)

    def perform_action_sequence(self, animation_list: List[str]) -> None:
        """
        Perform a list of motion capture animations in sequence.

        :param animation_list: List of motion-capture animations to perform.
        """

        self.action = PerformActionSequence(animation_list=animation_list, resp=self._previous_resp, static=self.static, dynamic=self.dynamic,
                               collision_detection=self.collision_detection, previous=self._previous_action)

    def reset_arm(self, arm: Arm) -> None:
        """
        Reset arm to rest position, after performing an action.
       
        :param arm: Which arm the Replicant is reachiing with -- left, right or both.
        """

        self.action = ResetArm(resp=self._previous_resp, arm=arm, static=self.static, dynamic=self.dynamic,
                               collision_detection=self.collision_detection, previous=self._previous_action)

    def _cache_static_data(self, resp: List[bytes]) -> None:
        """
        Cache static output data.

        :param resp: The response from the build.
        """

        self.static = ReplicantStatic(replicant_id=self.replicant_id, container_manager=self.container_manager, resp=resp)
        # Set action to be an idle.
        #self.action = Wait()
        
        # Add an avatar and set up its camera.
        self.commands.extend([{"$type": "create_avatar",
                               "type": "A_Img_Caps_Kinematic",
                               "id": self.static.avatar_id},
                              {"$type": "set_pass_masks",
                               #"pass_masks": ["_img", "_id", "_depth"],
                               "pass_masks": ["_img"],
                               "avatar_id": self.static.avatar_id},
                              {"$type": "parent_avatar_to_replicant",
                               "position": {"x": -0.1, "y": -0.1, "z": 0},
                               "avatar_id": self.static.avatar_id,
                               "id": self.replicant_id},
                              {"$type": "enable_image_sensor",
                               "enable": False,
                               "avatar_id": self.static.avatar_id},
                              {"$type": "set_img_pass_encoding",
                               "value": False}])
        

    def _set_dynamic_data(self, resp: List[bytes]) -> None:
        """
        Set dynamic data.

        :param resp: The response from the build.
        """
        if self.dynamic is None:
            frame_count = 0
        else:
            self.dynamic: ReplicantDynamic
            frame_count = self.dynamic.frame_count
        dynamic = ReplicantDynamic(resp=resp, replicant_id=self.replicant_id, body_parts=[],
                                            frame_count=frame_count, previous=self._previous_action)
        self.dynamic = dynamic

