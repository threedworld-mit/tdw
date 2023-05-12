from typing import List, Optional, Dict, Union
from copy import deepcopy
import numpy as np
from tdw.add_ons.add_on import AddOn
from tdw.drone.drone_dynamic import DroneDynamic
from tdw.drone.image_frequency import ImageFrequency
from tdw.drone.collision_detection import CollisionDetection
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.librarian import DroneRecord, DroneLibrarian


class Drone(AddOn):
    """

    """

    """:class_var
    The drone's library file. You can override this to use a custom library (e.g. a local library).
    """
    LIBRARY_NAME: str = "drones.json"

    def __init__(self, drone_id: int = 0, position: Union[Dict[str, float], np.ndarray] = None,
                 rotation: Union[Dict[str, float], np.ndarray] = None,
                 image_frequency: ImageFrequency = ImageFrequency.once, name: str = "drone",
                 forward_speed: float = 3, backward_speed: float = 3, rise_speed: float = 3, drop_speed: float = 3,
                 acceleration: float = 0.3, deceleration: float = 0.2, stability: float = 0.1, turn_sensitivity: float = 2,   
                 enable_lights: bool = False, motor_on: bool = True, target_framerate: int = 100):
        """
        :param drone_id: The ID of the drone.
        :param position: The position of the drone as an x, y, z dictionary or numpy array. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param rotation: The rotation of the drone in Euler angles (degrees) as an x, y, z dictionary or numpy array. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param image_frequency: An [`ImageFrequency`](../replicant/image_frequency.md) value that sets how often images are captured.
        :param name: The name of the drone model.
        :param forward_speed: Sets the drone's max forward speed.
        :param backward_speed: Sets the drone's max backward speed.
        :param rise_speed: Sets the drone's max vertical rise speed.
        :param drop_speed: Sets the drone's max vertical drop speed.
        :param acceleration: How fast the drone speeds up.
        :param deceleration: How fast the drone slows down.
        :param stability: How easily the drone is affected by outside forces.
        :param turn_sensitivity: The name of the drone model.
        :param enable_lights: Sets whether or not the drone's lights are on. 
        :param motor_on: Sets whether or not the drone is active on start.    
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
        The name this drone.
        """
        self.name: int = name
        """:field
        The ID of the drone's avatar (camera). This is used internally for API calls.
        """
        self.avatar_id: str = str(drone_id)
        """:field
        An [`ImageFrequency`](../drone/image_frequency.md) value that sets how often images are captured.
        """
        self.image_frequency: ImageFrequency = image_frequency
        """:field
        [The collision detection rules.](../replicant/collision_detection.md) This determines whether the drone will immediately stop moving or turning when it collides with something.
        """
        self.collision_detection: CollisionDetection = CollisionDetection()
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
        """:field
        The current drone lift value.
        """
        self.lift = 0
        """:field
        The current drone drive value.
        """
        self.drive = 0
        """:field
        The current drone turn value.
        """
        self.turn = 0
        """:field
        Whether the drone's motor is on or off.
        """
        self.motor_on = motor_on
        # This is used for collision detection. If the previous action is the "same" as this one, this action fails.
        self._previous_action: Optional[Action] = None
        # This is used when saving images.
        self._frame_count: int = 0
        # Initialize the Replicant metadata library.
        if Drone.LIBRARY_NAME not in Controller.DRONE_LIBRARIANS:
            Controller.DRONE_LIBRARIANS[Drone.LIBRARY_NAME] = DroneLibrarian(Drone.LIBRARY_NAME)
        # The Replicant metadata record.
        self._record: DroneRecord = Controller.DRONE_LIBRARIANS[Drone.LIBRARY_NAME].get_record(name)
        # The target framerate.
        self._target_framerate: int = target_framerate

    def get_initialization_commands(self) -> List[dict]:
        """
        This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

        :return: A list of commands that will initialize this add-on.
        """

        # Add the replicant. Send output data: Transforms, Bounds.
        commands = [{"$type": "add_drone", 
                     "id": self.drone_id,
                     "name":self.name, 
                     "url": self._record.get_url(), 
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
                     "enable_lights": self.enable_lights,
                     "motor_on": self.motor_on},
                    {"$type": "create_avatar",
                     "type": "A_Img_Caps_Kinematic",
                     "id": self.avatar_id},
                    {"$type": "set_pass_masks",
                    "pass_masks": ["_img", "_depth"],
                    "avatar_id": self.avatar_id},
                    {"$type": "parent_avatar_to_drone",
                     "position": {"x": 0, "y": -0.1, "z": 0},
                     "avatar_id": self.avatar_id,
                     "id": self.drone_id},
                    {"$type": "set_img_pass_encoding",
                     "value": True},
                    {"$type": "rotate_sensor_container_by", 
                     "axis": "pitch", 
                     "angle": 45.0,
                     "avatar_id": self.avatar_id},
                    {"$type": "set_target_framerate",
                     "framerate": self._target_framerate},
                    {"$type": "send_transforms",
                     "frequency": "always"},
                    {"$type": "send_bounds",
                     "frequency": "always"},
                    {"$type": "send_framerate",
                     "frequency": "always"}]
        if self.image_frequency == ImageFrequency.once or self.image_frequency == ImageFrequency.never:
            commands.extend([{"$type": "enable_image_sensor",
                              "enable": False,
                              "avatar_id": self.avatar_id}])
        # If we want images per frame, enable image capture now.
        elif self.image_frequency == ImageFrequency.always:
            commands.extend([{"$type": "enable_image_sensor",
                              "enable": True,
                              "avatar_id": self.avatar_id},
                             {"$type": "send_images",
                              "frequency": "always"},
                             {"$type": "send_camera_matrices",
                              "frequency": "always"}])
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

        # Add commands for elevation and forward motion.
        self.commands.extend([{"$type": "apply_drive_force_to_drone", "id": self.drone_id, "force": self.drive},
                              {"$type": "apply_lift_force_to_drone", "id": self.drone_id, "force": self.lift},
                              {"$type": "apply_turn_force_to_drone", "id": self.drone_id, "force": self.turn},
                              {"$type": "set_drone_motor", "motor_on": self.motor_on}])
      
    def set_lift(self, lift: float) -> None:
        self.lift = lift

    def set_drive(self, drive: float) -> None:
        self.drive = drive

    def set_turn(self, turn: float) -> None:
        self.turn = turn

    def set_motor(self, motor_on: bool):
        self.motor_on = motor_on
   
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

   