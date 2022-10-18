from __future__ import annotations
from typing import List, Optional, Dict, Union
from copy import deepcopy
import numpy as np
from tdw.add_ons.add_on import AddOn
from tdw.replicant.replicant_static import ReplicantStatic
from tdw.replicant.replicant_dynamic import ReplicantDynamic
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
from tdw.replicant.actions.animate import Animate
from tdw.replicant.actions.look_at import LookAt
from tdw.replicant.actions.reset_head import ResetHead
from tdw.replicant.image_frequency import ImageFrequency
from tdw.replicant.arm import Arm
from tdw.librarian import HumanoidRecord, HumanoidLibrarian
from tdw.controller import Controller


class Replicant(AddOn):
    _LIBRARY_NAME: str = "replicants.json"

    def __init__(self, replicant_id: int = 0, position: Dict[str, float] = None, rotation: Dict[str, float] = None,
                 image_frequency: ImageFrequency = ImageFrequency.once, name: str = "replicant_0"):
        """
        :param replicant_id: The ID of the Replicant.
        :param position: The position of the Replicant. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param rotation: The rotation of the Replicant in Euler angles (degrees). If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param image_frequency: An [`ImageFrequency`](../agents/image_frequency.md) value that sets how often images are captured.
        :param name: The name of the Replicant model.
        """

        super().__init__()
        if position is None:
            """:field
            The initial position of the Replicant.
            """
            self.initial_position: Dict[str, float] = {"x": 0, "y": 0, "z": 0}
        else:
            self.initial_position: Dict[str, float] = position
        if rotation is None:
            """:field
            The initial rotation of the Replicant.
            """
            self.initial_rotation: Dict[str, float] = {"x": 0, "y": 0, "z": 0}
        else:
            self.initial_rotation: Dict[str, float] = rotation
        """:field
        The [`ReplicantStatic`](../replicant/replicant_static.md) data.
        """
        self.static: Optional[ReplicantStatic] = None
        """:field
        The [`ReplicantDynamic`](../replicant/replicant_dynamic.md) data.
        """
        self.dynamic: Optional[ReplicantDynamic] = None
        """:field
        The ID of this replicant.
        """
        self.replicant_id: int = replicant_id
        """:field
        The Replicant's current [action](../replicant/actions/action.md). Can be None (no ongoing action).
        """
        self.action: Optional[Action] = None
        """:field
        An [`ImageFrequency`](../agents/image_frequency.md) value that sets how often images are captured.
        """
        self.image_frequency: ImageFrequency = image_frequency
        """:field
        [The collision detection rules.](../replicant/collision_detection.md) This determines whether the Replicant will immediately stop moving or turning when it collides with something.
        """
        self.collision_detection: CollisionDetection = CollisionDetection()
        self._previous_action: Optional[Action] = None
        self._previous_resp: List[bytes] = list()
        self._frame_count: int = 0
        # Initialize the Replicant metdata library.
        if Replicant._LIBRARY_NAME not in Controller.HUMANOID_LIBRARIANS:
            Controller.HUMANOID_LIBRARIANS[Replicant._LIBRARY_NAME] = HumanoidLibrarian(Replicant._LIBRARY_NAME)
        # Get the metdata record.
        self._record: HumanoidRecord = Controller.HUMANOID_LIBRARIANS[Replicant._LIBRARY_NAME].get_record(name)

    def get_initialization_commands(self) -> List[dict]:
        commands = [{"$type": "add_replicant",
                     "name": self._record.name,
                     "position": self.initial_position,
                     "rotation": self.initial_rotation,
                     "url": self._record.get_url(),
                     "id": self.replicant_id},
                    {"$type": "add_replicant_rigidbody",
                     "id": self.replicant_id},
                    {"$type": "send_replicants",
                     "frequency": "always"},
                    {"$type": "send_transforms",
                     "frequency": "always"},
                    {"$type": "send_bounds",
                     "frequency": "always"},
                    {"$type": "send_containment",
                     "frequency": "always"},
                    {"$type": "send_collisions",
                     "enter": True,
                     "stay": False,
                     "exit": True,
                     "collision_types": ["obj", "env"]}]
        return commands

    def on_send(self, resp: List[bytes]) -> None:
        """
        This is called after commands are sent to the build and a response is received.

        This function is called automatically by the controller; you don't need to call it yourself.

        :param resp: The response from the build.
        """

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
                    initialization_commands = self.action.get_initialization_commands(resp=resp,
                                                                                      static=self.static,
                                                                                      dynamic=self.dynamic,
                                                                                      image_frequency=self.image_frequency)
                    # This is an ongoing action.
                    if self.action.status == ActionStatus.ongoing:
                        self.commands.extend(initialization_commands)
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

    def turn_by(self, angle: float) -> None:
        """
        Turn the Replicant by an angle.

        :param angle: The target angle in degrees. Positive value = clockwise turn.
        """

        self.action = TurnBy(angle=angle)

    def turn_to(self, target: Union[int, Dict[str, float], np.ndarray]) -> None:
        """
        Turn the Replicant to face a target object or position.

        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        """

        self.action = TurnTo(target=target)

    def move_by(self, distance: float, reset_arms_num_frames: int = 15, arrived_at: float = 0.1,
                max_walk_cycles: int = 100) -> None:
        """
        Move the Replicant forward by a given distance.

        :param distance: The target distance. If less than 0, the Replicant will walk backwards.
        :param reset_arms_num_frames: The number of frames for resetting the arms while walking. This controls the speed of the arm motion.
        :param arrived_at: If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful.
        :param max_walk_cycles: The walk animation will loop this many times maximum. If by that point the Replicant hasn't reached its destination, the action fails.
        """

        self.action = MoveBy(distance=distance, dynamic=self.dynamic, collision_detection=self.collision_detection,
                             previous=self._previous_action, reset_arms_num_frames=reset_arms_num_frames,
                             arrived_at=arrived_at, max_walk_cycles=max_walk_cycles)

    def move_to(self, target: Union[int, Dict[str, float], np.ndarray], reset_arms_num_frames: int = 15,
                arrived_at: float = 0.1, max_walk_cycles: int = 100, bounds_position: str = "center") -> None:
        """
        Move to a target object or position.

        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        :param reset_arms_num_frames: The number of frames for resetting the arms while walking. This controls the speed of the arm motion.
        :param arrived_at: If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful.
        :param max_walk_cycles: The walk animation will loop this many times maximum. If by that point the Replicant hasn't reached its destination, the action fails.
        :param bounds_position: If `target` is an integer object ID, move towards this bounds point of the object. Options: `"center"`, `"top`", `"bottom"`, `"left"`, `"right"`, `"front"`, `"back"`.
        """

        self.action = MoveTo(target=target,
                             resp=self._previous_resp,
                             collision_detection=self.collision_detection,
                             previous=self._previous_action,
                             reset_arms_num_frames=reset_arms_num_frames,
                             arrived_at=arrived_at,
                             max_walk_cycles=max_walk_cycles,
                             bounds_position=bounds_position)

    def reach_for(self, target: Union[int, Dict[str,  float], np.ndarray], arms: Union[Arm, List[Arm]],
                  arrived_at: float = 0.01, max_distance: float = 1.5, duration: float = 0.25) -> None:
        """
        Reach for a target object or position.

        If target is an object, the target position is a point on the object.
        If the object has affordance points, the target position is the affordance point closest to the hand.
        Otherwise, the target position is the bounds position closest to the hand.

        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        :param arms: The [`Arm`](../agents/arm.md) value(s) that will reach for the `target` as a single value or a list. Example: `Arm.left` or `[Arm.left, Arm.right]`.
        :param arrived_at: If at the end of the action the hand(s) is this distance or less from the target position, the action succeeds.
        :param max_distance: The maximum distance from the hand to the target position.
        :param duration: The duration of the motion in seconds.
        """

        if isinstance(arms, Arm):
            a = [arms]
        elif isinstance(arms, list):
            a = arms
        else:
            raise Exception(f"Invalid arms: {arms}")
        self.action = ReachFor(target=target,
                               arms=a,
                               dynamic=self.dynamic,
                               collision_detection=self.collision_detection,
                               arrived_at=arrived_at,
                               previous=self._previous_action,
                               duration=duration,
                               max_distance=max_distance)

    def grasp(self, target: int, arm: Arm, orient_to_floor: bool = True) -> None:
        """
        Grasp a target object.

        :param target: The target object ID.
        :param arm: The [`Arm`](../agents/arm.md) value for the hand that will grasp the target object.
        :param orient_to_floor: If True, rotate the grasped object to be level with the floor.
        """

        self.action = Grasp(target=target,
                            arm=arm,
                            dynamic=self.dynamic,
                            orient_to_floor=orient_to_floor)

    def drop(self, arm: Arm, max_num_frames: int = 100) -> None:
        """
        Drop a held target object.

        :param arm: The [`Arm`](../agents/arm.md) holding the object.
        :param max_num_frames: Wait this number of `communicate()` calls maximum for the object to stop moving before ending the action.
        """

        self.action = Drop(arm=arm, dynamic=self.dynamic, max_num_frames=max_num_frames)

    def animate(self, animation: str, forward: bool = True, library: str = "humanoid_animations.json") -> None:
        """
        Play an animation.

        :param animation: The name of the animation.
        :param forward: If True, play the animation forwards. If False, play the animation backwards.
        :param library: The animation library.
        """

        self.action = Animate(animation=animation,
                              collision_detection=self.collision_detection,
                              forward=forward,
                              library=library,
                              previous=self._previous_action)

    def reset_arm(self, arms: Union[Arm, List[Arm]], duration: float = 0.25) -> None:
        """
        Reset arm to rest position, after performing an action.
       
        :param arms: The [`Arm`](../agents/arm.md) value(s) that will reach for the `target` as a single value or a list. Example: `Arm.left` or `[Arm.left, Arm.right]`.
        :param duration: The duration of the motion in seconds.
        """

        if isinstance(arms, Arm):
            a = [arms]
        elif isinstance(arms, list):
            a = arms
        else:
            raise Exception(f"Invalid arms: {arms}")
        self.action = ResetArm(arms=a,
                               dynamic=self.dynamic,
                               collision_detection=self.collision_detection,
                               previous=self._previous_action,
                               duration=duration)

    def look_at(self, target: Union[int, np.ndarray, Dict[str,  float]], duration: float = 0.1):
        """
        Look at a target object or position.

        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        :param duration: The duration of the motion in seconds.
        """

        self.action = LookAt(target=target, duration=duration)

    def reset_head(self, duration: float = 0.1):
        """
        Look at a target object or position.

        :param duration: The duration of the motion in seconds.
        """

        self.action = ResetHead(duration=duration)

    def reset(self, position: Dict[str, float] = None, rotation: Dict[str, float] = None,) -> None:
        """
        Reset the Replicant. Call this when you reset the scene.

        :param position: The position of the replicant. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param rotation: The rotation of the replicant in Euler angles (degrees). If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        """

        self.initialized = False
        self.dynamic = None
        self.static = None
        self.action = None
        self._previous_action = None
        self._previous_resp.clear()
        self._frame_count: int = 0
        self.collision_detection = CollisionDetection()
        if position is None:
            self.initial_position = {"x": 0, "y": 0, "z": 0}
        else:
            self.initial_position = position
        if rotation is None:
            self.initial_rotation = {"x": 0, "y": 0, "z": 0}
        else:
            self.initial_rotation = rotation

    def _cache_static_data(self, resp: List[bytes]) -> None:
        """
        Cache static output data.

        :param resp: The response from the build.
        """

        self.static = ReplicantStatic(replicant_id=self.replicant_id, resp=resp)
        # Add an avatar and set up its camera.
        self.commands.extend([{"$type": "create_avatar",
                               "type": "A_Img_Caps_Kinematic",
                               "id": self.static.avatar_id},
                              {"$type": "set_pass_masks",
                               "pass_masks": ["_img", "_id", "_depth"],
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

        self.dynamic = ReplicantDynamic(resp=resp, replicant_id=self.replicant_id, frame_count=self._frame_count)
        if self.dynamic.got_images:
            self._frame_count += 1
