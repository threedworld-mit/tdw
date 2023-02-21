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
from tdw.replicant.actions.rotate_head import RotateHead
from tdw.replicant.actions.reset_head import ResetHead
from tdw.replicant.actions.do_nothing import DoNothing
from tdw.replicant.image_frequency import ImageFrequency
from tdw.replicant.arm import Arm
from tdw.librarian import HumanoidRecord, HumanoidLibrarian
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils


class Replicant(AddOn):
    """
    A Replicant is a human-like agent that can interact with the scene with pseudo-physics behavior.

    When a Replicant collides with objects, it initiates a physics-driven collision. The Replicant's own movements are driven by non-physics animation.

    A Replicant can walk, turn, reach for positions or objects, grasp and drop objects, and turn its head to look around.
    """

    """:class_var
    The Replicants library file. You can override this to use a custom library (e.g. a local library).
    """
    LIBRARY_NAME: str = "replicants.json"

    def __init__(self, replicant_id: int = 0, position: Union[Dict[str, float], np.ndarray] = None,
                 rotation: Union[Dict[str, float], np.ndarray] = None,
                 image_frequency: ImageFrequency = ImageFrequency.once, name: str = "replicant_0"):
        """
        :param replicant_id: The ID of the Replicant.
        :param position: The position of the Replicant as an x, y, z dictionary or numpy array. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param rotation: The rotation of the Replicant in Euler angles (degrees) as an x, y, z dictionary or numpy array. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param image_frequency: An [`ImageFrequency`](../replicant/image_frequency.md) value that sets how often images are captured.
        :param name: The name of the Replicant model.
        """

        super().__init__()
        """:field
        The initial position of the Replicant.
        """
        self.initial_position: Dict[str, float] = {"x": 0, "y": 0, "z": 0}
        """:field
        The initial rotation of the Replicant.
        """
        self.initial_rotation: Dict[str, float] = {"x": 0, "y": 0, "z": 0}
        self._set_initial_position_and_rotation(position=position, rotation=rotation)
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
        An [`ImageFrequency`](../replicant/image_frequency.md) value that sets how often images are captured.
        """
        self.image_frequency: ImageFrequency = image_frequency
        """:field
        [The collision detection rules.](../replicant/collision_detection.md) This determines whether the Replicant will immediately stop moving or turning when it collides with something.
        """
        self.collision_detection: CollisionDetection = CollisionDetection()
        # This is used for collision detection. If the previous action is the "same" as this one, this action fails.
        self._previous_action: Optional[Action] = None
        # This is used when saving images.
        self._frame_count: int = 0
        # Initialize the Replicant metdata library.
        if Replicant.LIBRARY_NAME not in Controller.HUMANOID_LIBRARIANS:
            Controller.HUMANOID_LIBRARIANS[Replicant.LIBRARY_NAME] = HumanoidLibrarian(Replicant.LIBRARY_NAME)
        # The Replicant metadata record.
        self._record: HumanoidRecord = Controller.HUMANOID_LIBRARIANS[Replicant.LIBRARY_NAME].get_record(name)

    def get_initialization_commands(self) -> List[dict]:
        """
        This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

        :return: A list of commands that will initialize this add-on.
        """

        # Add the replicant. Send output data: Replicants, Transforms, Bounds, Containment.
        commands = [{"$type": "add_replicant",
                     "name": self._record.name,
                     "position": self.initial_position,
                     "rotation": self.initial_rotation,
                     "url": self._record.get_url(),
                     "id": self.replicant_id},
                    {"$type": "add_replicant_rigidbody",
                     "id": self.replicant_id},
                    {"$type": "set_rigidbody_constraints",
                     "id": self.replicant_id,
                     "freeze_position_axes": {"x": 0, "y": 1, "z": 0}},
                    {"$type": "send_replicants",
                     "frequency": "always"},
                    {"$type": "send_transforms",
                     "frequency": "always"},
                    {"$type": "send_bounds",
                     "frequency": "always"},
                    {"$type": "send_containment",
                     "frequency": "always"},
                    {"$type": "send_framerate",
                     "frequency": "always"}]
        return commands

    def on_send(self, resp: List[bytes]) -> None:
        """
        This is called within `Controller.communicate(commands)` after commands are sent to the build and a response is received.

        Use this function to send commands to the build on the next `Controller.communicate(commands)` call, given the `resp` response.
        Any commands in the `self.commands` list will be sent on the *next* `Controller.communicate(commands)` call.

        :param resp: The response from the build.
        """

        # If there isn't cached static data, assume we have the output data we need and cache it now.
        if self.static is None:
            self._cache_static_data(resp=resp)
        # Update the dynamic data per `communicate()` call.
        self._set_dynamic_data(resp=resp)
        # Don't do anything if there isn't an action or if the action is done.
        if self.action is None or self.action.done:
            return
        # Start or continue the action.
        else:
            # Initialize the action.
            if not self.action.initialized:
                # The action's status defaults to `ongoing`, but actions sometimes fail prior to initialization.
                if self.action.status == ActionStatus.ongoing:
                    # Initialize the action and get initialization commands.
                    self.action.initialized = True
                    initialization_commands = self.action.get_initialization_commands(resp=resp,
                                                                                      static=self.static,
                                                                                      dynamic=self.dynamic,
                                                                                      image_frequency=self.image_frequency)

                    # Most actions are `ongoing` after initialization, but they might've succeeded or failed already.
                    if self.action.status == ActionStatus.ongoing:
                        self.commands.extend(initialization_commands)
                    else:
                        self.commands.extend(self.action.get_end_commands(resp=resp,
                                                                          static=self.static,
                                                                          dynamic=self.dynamic,
                                                                          image_frequency=self.image_frequency))
            # Continue an ongoing action.
            else:
                # Get the ongoing action commands.
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

        This is a non-animated action, meaning that the Replicant will immediately snap to the angle.

        :param angle: The target angle in degrees. Positive value = clockwise turn.
        """

        self.action = TurnBy(angle=angle)

    def turn_to(self, target: Union[int, Dict[str, float], np.ndarray]) -> None:
        """
        Turn the Replicant to face a target object or position.

        This is a non-animated action, meaning that the Replicant will immediately snap to the angle.

        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        """

        self.action = TurnTo(target=target)

    def move_by(self, distance: float, reset_arms: bool = True, reset_arms_duration: float = 0.25,
                scale_reset_arms_duration: bool = True, arrived_at: float = 0.1, max_walk_cycles: int = 100) -> None:
        """
        Walk a given distance.

        The Replicant will continuously play a walk cycle animation until the action ends.

        The action can end for several reasons depending on the collision detection rules (see [`self.collision_detection`](../replicant/collision_detection.md).

        - If the Replicant walks the target distance, the action succeeds.
        - If `collision_detection.previous_was_same == True`, and the previous action was `move_by()` or `move_to()`, and it was in the same direction (forwards/backwards), and the previous action ended in failure, this action ends immediately.
        - If `self.collision_detection.avoid_obstacles == True` and the Replicant encounters a wall or object in its path:
          - If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
          - Otherwise, the action ends in failure.
        - If the Replicant collides with an object or a wall and `self.collision_detection.objects == True` and/or `self.collision_detection.walls == True` respectively:
          - If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
          - Otherwise, the action ends in failure.
        - If the Replicant takes too long to reach the target distance, the action ends in failure (see `self.max_walk_cycles`).

        :param distance: The target distance. If less than 0, the Replicant will walk backwards.
        :param reset_arms: If True, reset the arms to their neutral positions while beginning the walk cycle.
        :param reset_arms_duration: The speed at which the arms are reset in seconds.
        :param scale_reset_arms_duration: If True, `reset_arms_duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        :param arrived_at: If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful.
        :param max_walk_cycles: The walk animation will loop this many times maximum. If by that point the Replicant hasn't reached its destination, the action fails.
        """

        self.action = MoveBy(distance=distance,
                             dynamic=self.dynamic,
                             collision_detection=self.collision_detection,
                             previous=self._previous_action,
                             reset_arms=reset_arms,
                             reset_arms_duration=reset_arms_duration,
                             scale_reset_arms_duration=scale_reset_arms_duration,
                             arrived_at=arrived_at,
                             max_walk_cycles=max_walk_cycles)

    def move_to(self, target: Union[int, Dict[str, float], np.ndarray], reset_arms: bool = True,
                reset_arms_duration: float = 0.25, scale_reset_arms_duration: bool = True, arrived_at: float = 0.1,
                max_walk_cycles: int = 100, bounds_position: str = "center") -> None:
        """
        Turn the Replicant to a target position or object and then walk to it.

        While walking, the Replicant will continuously play a walk cycle animation until the action ends.

        The action can end for several reasons depending on the collision detection rules (see [`self.collision_detection`](../replicant/collision_detection.md).

        - If the Replicant walks the target distance, the action succeeds.
        - If `collision_detection.previous_was_same == True`, and the previous action was `move_by()` or `move_to()`, and it was in the same direction (forwards/backwards), and the previous action ended in failure, this action ends immediately.
        - If `self.collision_detection.avoid_obstacles == True` and the Replicant encounters a wall or object in its path:
          - If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
          - Otherwise, the action ends in failure.
        - If the Replicant collides with an object or a wall and `self.collision_detection.objects == True` and/or `self.collision_detection.walls == True` respectively:
          - If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
          - Otherwise, the action ends in failure.
        - If the Replicant takes too long to reach the target distance, the action ends in failure (see `self.max_walk_cycles`).

        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        :param reset_arms: If True, reset the arms to their neutral positions while beginning the walk cycle.
        :param reset_arms_duration: The speed at which the arms are reset in seconds.
        :param scale_reset_arms_duration: If True, `reset_arms_duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        :param arrived_at: If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful.
        :param max_walk_cycles: The walk animation will loop this many times maximum. If by that point the Replicant hasn't reached its destination, the action fails.
        :param bounds_position: If `target` is an integer object ID, move towards this bounds point of the object. Options: `"center"`, `"top`", `"bottom"`, `"left"`, `"right"`, `"front"`, `"back"`.
        """

        self.action = MoveTo(target=target,
                             collision_detection=self.collision_detection,
                             previous=self._previous_action,
                             reset_arms=reset_arms,
                             reset_arms_duration=reset_arms_duration,
                             scale_reset_arms_duration=scale_reset_arms_duration,
                             arrived_at=arrived_at,
                             max_walk_cycles=max_walk_cycles,
                             bounds_position=bounds_position)

    def reach_for(self, target: Union[int, Dict[str,  float], np.ndarray], arm: Union[Arm, List[Arm]],
                  absolute: bool = True, offhand_follows: bool = False, arrived_at: float = 0.09,
                  max_distance: float = 1.5, duration: float = 0.25, scale_duration: bool = True) -> None:
        """
        Reach for a target object or position. One or both hands can reach for the target at the same time.

        If target is an object, the target position is a point on the object.
        If the object has affordance points, the target position is the affordance point closest to the hand.
        Otherwise, the target position is the bounds position closest to the hand.

        The Replicant's arm(s) will continuously over multiple `communicate()` calls move until either the motion is complete or the arm collides with something (see `self.collision_detection`).

        - If the hand is near the target at the end of the action, the action succeeds.
        - If the target is too far away at the start of the action, the action fails.
        - The collision detection will respond normally to walls, objects, obstacle avoidance, etc.
        - If `self.collision_detection.previous_was_same == True`, and if the previous action was a subclass of `ArmMotion`, and it ended in a collision, this action ends immediately.

        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        :param arm: The [`Arm`](../replicant/arm.md) value(s) that will reach for the `target` as a single value or a list. Example: `Arm.left` or `[Arm.left, Arm.right]`.
        :param absolute: If True, the target position is in world space coordinates. If False, the target position is relative to the Replicant. Ignored if `target` is an int.
        :param offhand_follows: If True, the offhand will follow the primary hand, meaning that it will maintain the same relative position. Ignored if `arm` is a list or `target` is an int.
        :param arrived_at: If at the end of the action the hand(s) is this distance or less from the target position, the action succeeds.
        :param max_distance: The maximum distance from the hand to the target position.
        :param duration: The duration of the motion in seconds.
        :param scale_duration: If True, `duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        """

        # Convert the relative position to an absolute position.
        if not isinstance(target, int) and not absolute:
            if isinstance(target, np.ndarray):
                target = self.dynamic.transform.position + target
            elif isinstance(target, dict):
                target = self.dynamic.transform.position + TDWUtils.vector3_to_array(target)
        self.action = ReachFor(target=target,
                               arms=Replicant._arms_to_list(arm),
                               dynamic=self.dynamic,
                               collision_detection=self.collision_detection,
                               offhand_follows=offhand_follows,
                               arrived_at=arrived_at,
                               previous=self._previous_action,
                               duration=duration,
                               scale_duration=scale_duration,
                               max_distance=max_distance)

    def grasp(self, target: int, arm: Arm, angle: Optional[float] = 90, axis: Optional[str] = "pitch") -> None:
        """
        Grasp a target object.

        The action fails if the hand is already holding an object. Otherwise, the action succeeds.

        When an object is grasped, it is made kinematic. Any objects contained by the object are parented to it and also made kinematic. For more information regarding containment in TDW, [read this](../../lessons/semantic_states/containment.md).

        :param target: The target object ID.
        :param arm: The [`Arm`](../replicant/arm.md) value for the hand that will grasp the target object.
        :param angle: Continuously (per `communicate()` call, including after this action ends), rotate the the grasped object by this many degrees relative to the hand. If None, the grasped object will maintain its initial rotation.
        :param axis: Continuously (per `communicate()` call, including after this action ends) rotate the grasped object around this axis relative to the hand. Options: `"pitch"`, `"yaw"`, `"roll"`. If None, the grasped object will maintain its initial rotation.
        """

        self.action = Grasp(target=target,
                            arm=arm,
                            dynamic=self.dynamic,
                            angle=angle,
                            axis=axis)

    def drop(self, arm: Arm, max_num_frames: int = 100) -> None:
        """
        Drop a held target object.

        The action ends when the object stops moving or the number of consecutive `communicate()` calls since dropping the object exceeds `self.max_num_frames`.

        When an object is dropped, it is made non-kinematic. Any objects contained by the object are parented to it and also made non-kinematic. For more information regarding containment in TDW, [read this](../../lessons/semantic_states/containment.md).

        :param arm: The [`Arm`](../replicant/arm.md) holding the object.
        :param max_num_frames: Wait this number of `communicate()` calls maximum for the object to stop moving before ending the action.
        """

        self.action = Drop(arm=arm, dynamic=self.dynamic, max_num_frames=max_num_frames)

    def animate(self, animation: str, library: str = "humanoid_animations.json") -> None:
        """
        Play an animation.

        The animation will end either when the animation clip is finished or if the Replicant collides with something (see [`self.collision_detection`](../replicant/collision_detection.md)).

        - The collision detection will respond normally to walls, objects, obstacle avoidance, etc.
        - If `self.collision_detection.previous_was_same == True`, and it was the same animation, and it ended in a collision, this action ends immediately.

        :param animation: The name of the animation.
        :param library: The animation library.
        """

        self.action = Animate(animation=animation,
                              collision_detection=self.collision_detection,
                              forward=True,
                              library=library,
                              previous=self._previous_action,
                              ik_body_parts=[])

    def reset_arm(self, arm: Union[Arm, List[Arm]], duration: float = 0.25, scale_duration: bool = True) -> None:
        """
        Move arm(s) back to rest position(s). One or both arms can be reset at the same time.

        The Replicant's arm(s) will continuously over multiple `communicate()` calls move until either the motion is complete or the arm collides with something (see `self.collision_detection`).

        - The collision detection will respond normally to walls, objects, obstacle avoidance, etc.
        - If `self.collision_detection.previous_was_same == True`, and if the previous action was an arm motion, and it ended in a collision, this action ends immediately.
       
        :param arm: The [`Arm`](../replicant/arm.md) value(s) that will reach for the `target` as a single value or a list. Example: `Arm.left` or `[Arm.left, Arm.right]`.
        :param duration: The duration of the motion in seconds.
        :param scale_duration: If True, `duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        """

        self.action = ResetArm(arms=Replicant._arms_to_list(arm),
                               dynamic=self.dynamic,
                               collision_detection=self.collision_detection,
                               previous=self._previous_action,
                               duration=duration,
                               scale_duration=scale_duration)

    def look_at(self, target: Union[int, np.ndarray, Dict[str,  float]], duration: float = 0.1,
                scale_duration: bool = True):
        """
        Look at a target object or position.

        The head will continuously move over multiple `communicate()` calls until it is looking at the target.

        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        :param duration: The duration of the motion in seconds.
        :param scale_duration: If True, `duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        """

        self.action = LookAt(target=target, duration=duration, scale_duration=scale_duration)

    def rotate_head(self, axis: str, angle: float, duration: float = 0.1, scale_duration: bool = True):
        """
        Rotate the head by an angle around an axis.

        The head will continuously move over multiple `communicate()` calls until it is looking at the target.

        :param axis: The axis of rotation. Options: `"pitch"`, `"yaw"`, `"roll"`.
        :param angle: The target angle in degrees.
        :param duration: The duration of the motion in seconds.
        :param scale_duration: If True, `duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        """

        self.action = RotateHead(axis=axis, angle=angle, duration=duration, scale_duration=scale_duration)

    def reset_head(self, duration: float = 0.1, scale_duration: bool = True):
        """
        Reset the head to its neutral rotation.

        The head will continuously move over multiple `communicate()` calls until it is at its neutral rotation.

        :param duration: The duration of the motion in seconds.
        :param scale_duration: If True, `duration` will be multiplied by `framerate / 60)`, ensuring smoother motions at faster-than-life simulation speeds.
        """

        self.action = ResetHead(duration=duration, scale_duration=scale_duration)

    def reset(self, position: Union[Dict[str, float], np.ndarray] = None,
              rotation: Union[Dict[str, float], np.ndarray] = None) -> None:
        """
        Reset the Replicant. Call this when you reset the scene.

        :param position: The position of the Replicant as an x, y, z dictionary or numpy array. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param rotation: The rotation of the Replicant in Euler angles (degrees) as an x, y, z dictionary or numpy array. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        """

        self.initialized = False
        self.dynamic = None
        self.static = None
        self.action = None
        self._previous_action = None
        self._frame_count: int = 0
        self.collision_detection = CollisionDetection()
        self._set_initial_position_and_rotation(position=position, rotation=rotation)
        self.commands.clear()

    def _set_initial_position_and_rotation(self, position: Union[Dict[str, float], np.ndarray] = None,
                                           rotation: Union[Dict[str, float], np.ndarray] = None) -> None:
        """
        Set the intial position and rotation.

        :param position: The position of the Replicant as an x, y, z dictionary or numpy array. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param rotation: The rotation of the Replicant in Euler angles (degrees) as an x, y, z dictionary or numpy array. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        """

        if position is None:
            self.initial_position = {"x": 0, "y": 0, "z": 0}
        elif isinstance(position, dict):
            self.initial_position = position
        elif isinstance(position, np.ndarray):
            self.initial_position = TDWUtils.array_to_vector3(position)
        else:
            raise Exception(position)
        if rotation is None:
            self.initial_rotation = {"x": 0, "y": 0, "z": 0}
        elif isinstance(rotation, dict):
            self.initial_rotation = rotation
        elif isinstance(rotation, np.ndarray):
            self.initial_rotation = TDWUtils.array_to_vector3(rotation)

    def _cache_static_data(self, resp: List[bytes]) -> None:
        """
        Cache static output data.

        :param resp: The response from the build.
        """

        self.static = ReplicantStatic(replicant_id=self.replicant_id, resp=resp)
        # Set an initial action.
        self.action = DoNothing()
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

    @staticmethod
    def _arms_to_list(arm: Union[Arm, List[Arm]]) -> List[Arm]:
        """
        Converts a single `Arm` value to a list if needed.

        :param arm: Either a single `Arm` value or a list of `Arm` values.

        :return: A list of `Arm` values.
        """

        if isinstance(arm, Arm):
            return [arm]
        elif isinstance(arm, list):
            return arm
        else:
            raise Exception(f"Invalid arms: {arm}")
