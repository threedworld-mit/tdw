from typing import List, Optional, Dict, Union
from copy import deepcopy
import numpy as np
from tdw.add_ons.add_on import AddOn
from tdw.drone.actions.action import Action
from tdw.drone.action_status import ActionStatus
from tdw.drone.actions.turn_by import TurnBy
from tdw.drone.actions.turn_to import TurnTo
from tdw.drone.actions.move_by import MoveBy
from tdw.drone.actions.move_to import MoveTo
from tdw.drone.image_frequency import ImageFrequency
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils


class Drone(AddOn):
    """

    """

    """:class_var
    The drone's library file. You can override this to use a custom library (e.g. a local library).
    """
    LIBRARY_NAME: str = "drone.json"

    def __init__(self, drone_id: int = 0, position: Union[Dict[str, float], np.ndarray] = None,
                 rotation: Union[Dict[str, float], np.ndarray] = None,
                 image_frequency: ImageFrequency = ImageFrequency.once, name: str = "drone",
                 forward_speed: float = 3, backward_speed: float = 3, rise_speed: float = 3, drop_speed: float = 3,
                 acceleration: float = 0.3, deceleration: float = 0.2, stability: float = 0.1, turn_sensitivity: float = 2,   
                 enable_lights: bool = False, target_framerate: int = 100):
        """
        :param replicant_id: The ID of the Replicant.
        :param position: The position of the Replicant as an x, y, z dictionary or numpy array. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param rotation: The rotation of the Replicant in Euler angles (degrees) as an x, y, z dictionary or numpy array. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param image_frequency: An [`ImageFrequency`](../replicant/image_frequency.md) value that sets how often images are captured.
        :param name: The name of the Replicant model.
        :param target_framerate: The target framerate. It's possible to set a higher target framerate, but doing so can lead to a loss of precision in agent movement.
        """

        super().__init__()
        """:field
        The initial position of the drone.
        """
        self.initial_position: Dict[str, float] = {"x": 0, "y": 0, "z": 0}
        """:field
        The initial rotation of the drone.
        """
        self.initial_rotation: Dict[str, float] = {"x": 0, "y": 0, "z": 0}
        self._set_initial_position_and_rotation(position=position, rotation=rotation)
        """:field
        The [`DroneDynamic`](../drone/drone_dynamic.md) data.
        """
        self.dynamic: Optional[DroneDynamic] = None
        """:field
        The ID of this drone.
        """
        self.drone_id: int = drone_id
        """:field
        The drone's current [action](../drone/actions/action.md). Can be None (no ongoing action).
        """
        self.action: Optional[Action] = None
        """:field
        An [`ImageFrequency`](../drone/image_frequency.md) value that sets how often images are captured.
        """
        self.image_frequency: ImageFrequency = image_frequency
        """:field
        The max forward speed of this drone.
        """
        self.forward_speed = forward_speed
        """:field
        The max backwards speed of this drone.
        """
        self.backward_speed = backward_speed
        """:field
        The max vertical rise speed of this drone.
        """
        self.rise_speed = rise_speed
        """:field
        The max vertical drop speed of this drone.
        """
        self.drop_speed = drop_speed
        """:field
        How fast the drone speeds up.
        """
        self.acceleration = acceleration
        """:field
        How fast the drone slows down.
        """
        self.deceleration = deceleration
        """:field
        How easily the drone is affected by outside forces.
        """
        self.stability = stability
        """:field
        How fast the drone rotates.
        """
        self.turn_sensitivity = turn_sensitivity
        """:field
        Whether the drone's lights are on and blinking.
        """
        self.enable_lights = enable_lights
        # This is used for collision detection. If the previous action is the "same" as this one, this action fails.
        self._previous_action: Optional[Action] = None
        # This is used when saving images.
        self._frame_count: int = 0
        """
        # Initialize the Replicant metadata library.
        if Replicant.LIBRARY_NAME not in Controller.HUMANOID_LIBRARIANS:
            Controller.HUMANOID_LIBRARIANS[Replicant.LIBRARY_NAME] = HumanoidLibrarian(Replicant.LIBRARY_NAME)
        # The Replicant metadata record.
        self._record: HumanoidRecord = Controller.HUMANOID_LIBRARIANS[Replicant.LIBRARY_NAME].get_record(name)
        """
        # The target framerate.
        self._target_framerate: int = target_framerate

    def get_initialization_commands(self) -> List[dict]:
        """
        This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

        :return: A list of commands that will initialize this add-on.
        """

        # Add the replicant. Send output data: Replicants, Transforms, Bounds, Containment.
        commands = [{"$type": "add_drone", 
                     "id": self.drone_id,
                     "name":"drone", 
                     "url": "https://tdw-public.s3.amazonaws.com/flying_objects/windows/2020.3/drone", 
                     "position": self.initial_position,
                     "rotation": self.initial_rotation,
                     "rise_speed": self.rise_speed,
                     "drop_speed": self.drop_speed,
                     "forward_speed": self.forward_speed,
                     "backward_speed": self.backward_speed,
                     "acceleration": self.acceleration,
                     "deceleration": self.deceleration,
                     "stability": self.stability,
                     "turn_sensitivity": self.turn_sensitivity,
                     "enable_lights": False},
                    {"$type": "set_target_framerate",
                     "framerate": self._target_framerate},
                    {"$type": "send_transforms",
                     "frequency": "always"},
                    {"$type": "send_bounds",
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
                                                                                      dynamic=self.dynamic,
                                                                                      image_frequency=self.image_frequency)

                    # Most actions are `ongoing` after initialization, but they might've succeeded or failed already.
                    if self.action.status == ActionStatus.ongoing:
                        self.commands.extend(initialization_commands)
                    else:
                        self.commands.extend(self.action.get_end_commands(resp=resp,
                                                                          dynamic=self.dynamic,
                                                                          image_frequency=self.image_frequency))
            # Continue an ongoing action.
            else:
                # Get the ongoing action commands.
                action_commands = self.action.get_ongoing_commands(resp=resp, dynamic=self.dynamic)
                # This is an ongoing action. Append ongoing commands.
                if self.action.status == ActionStatus.ongoing:
                    self.commands.extend(action_commands)
                # This action is done. Append end commands.
                else:
                    self.commands.extend(self.action.get_end_commands(resp=resp,
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
        Turn the drone by an angle.

        This is a non-animated action, meaning that the drone will immediately snap to the angle.

        :param angle: The target angle in degrees. Positive value = clockwise turn.
        """

        self.action = TurnBy(angle=angle)

    def turn_to(self, target: Union[int, Dict[str, float], np.ndarray]) -> None:
        """
        Turn the drone to face a target object or position.

        This is a non-animated action, meaning that the drone will immediately snap to the angle.

        :param target: The target. If int: An object ID. If dict: A position as an x, y, z dictionary. If numpy array: A position as an [x, y, z] numpy array.
        """

        self.action = TurnTo(target=target)

    def move_by(self, distance: float, arrived_at: float = 0.1) -> None:
        """
        Fly a given distance.

        The action can end for several reasons depending on the collision detection rules (see [`self.collision_detection`](../replicant/collision_detection.md).

        - If the drone flys the target distance, the action succeeds.
        - If `collision_detection.previous_was_same == True`, and the previous action was `move_by()` or `move_to()`, and it was in the same direction (forwards/backwards), and the previous action ended in failure, this action ends immediately.
        - If `self.collision_detection.avoid_obstacles == True` and the Replicant encounters a wall or object in its path:
          - If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
          - Otherwise, the action ends in failure.
        - If the Replicant collides with an object or a wall and `self.collision_detection.objects == True` and/or `self.collision_detection.walls == True` respectively:
          - If the object is in `self.collision_detection.exclude_objects`, the Replicant ignores it.
          - Otherwise, the action ends in failure.

        :param distance: The target distance. If less than 0, the Replicant will walk backwards.
        :param arrived_at: If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful.
        """

        self.action = MoveBy(distance=distance,
                             dynamic=self.dynamic,
                             collision_detection=self.collision_detection,
                             previous=self._previous_action,
                             arrived_at=arrived_at)

    def move_to(self, target: Union[int, Dict[str, float], np.ndarray], reset_arms: bool = True, arrived_at: float = 0.1, bounds_position: str = "center") -> None:
        """
        Turn the drone to a target position or object and then fly to it.

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
        :param arrived_at: If at any point during the action the difference between the target distance and distance traversed is less than this, then the action is successful.
        :param bounds_position: If `target` is an integer object ID, move towards this bounds point of the object. Options: `"center"`, `"top`", `"bottom"`, `"left"`, `"right"`, `"front"`, `"back"`.
        """

        self.action = MoveTo(target=target,
                             collision_detection=self.collision_detection,
                             previous=self._previous_action,
                             arrived_at=arrived_at,
                             bounds_position=bounds_position)
   

    def _set_initial_position_and_rotation(self, position: Union[Dict[str, float], np.ndarray] = None,
                                           rotation: Union[Dict[str, float], np.ndarray] = None) -> None:
        """
        Set the intial position and rotation.

        :param position: The position of the drone as an x, y, z dictionary or numpy array. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param rotation: The rotation of the drone in Euler angles (degrees) as an x, y, z dictionary or numpy array. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
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

    
    def _set_dynamic_data(self, resp: List[bytes]) -> None:
        """
        Set dynamic data.

        :param resp: The response from the build.
        """

        self.dynamic = DroneDynamic(resp=resp, drone_id=self.drone_id, frame_count=self._frame_count)
        if self.dynamic.got_images:
            self._frame_count += 1

   