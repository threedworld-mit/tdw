from typing import List, Optional, Dict
import numpy as np
from tdw.type_aliases import POSITION, ROTATION
from tdw.add_ons.add_on import AddOn
from tdw.drone.drone_dynamic import DroneDynamic
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.librarian import DroneRecord, DroneLibrarian


class Drone(AddOn):
    """
    A drone is a flying agent. From this API, you can set the drone's speed (lift, drive, turn) and turn its motor on and off.

    The drone's output data, including images, is stored in [`drone.dynamic`](../drone/drone_dynamic.md).
    """

    """:class_var
    The drone's library file. You can override this to use a custom library (e.g. a local library).
    """
    LIBRARY_NAME: str = "drones.json"

    def __init__(self, drone_id: int = 0, position: POSITION = None, rotation: ROTATION = None, name: str = "drone",
                 forward_speed: float = 3, backward_speed: float = 3, rise_speed: float = 3, drop_speed: float = 3,
                 acceleration: float = 0.3, deceleration: float = 0.2, stability: float = 0.1,
                 turn_sensitivity: float = 2, enable_lights: bool = False, motor_on: bool = True,
                 image_capture: bool = True, image_passes: List[str] = None):
        """
        :param drone_id: The ID of the drone.
        :param position: The position of the drone as an x, y, z dictionary or numpy array. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param rotation: The rotation of the drone in Euler angles (degrees) as an x, y, z dictionary or numpy array. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
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
        :param image_capture: If True, the drone will receive image and camera matrix data per `communicate()` call. Whether or not this is True, the drone will always render images in the simulation window.
        :param image_passes: A list of image passes that will be captured. Ignored if `image_capture == False`. If None, defaults to `["_img", "_id"]`.
        """

        super().__init__()

        if position is None:
            """:field
            The initial position of the drone.
            """
            self.initial_position: Dict[str, float] = {"x": 0, "y": 0, "z": 0}
        elif isinstance(position, dict):
            self.initial_position = position
        elif isinstance(position, np.ndarray):
            self.initial_position = TDWUtils.array_to_vector3(position)
        else:
            raise Exception(position)
        if rotation is None:
            """:field
            The initial rotation of the drone in Euler angles.
            """
            self.initial_rotation: Dict[str, float] = {"x": 0, "y": 0, "z": 0}
        elif isinstance(rotation, dict):
            self.initial_rotation = rotation
        elif isinstance(rotation, np.ndarray):
            self.initial_rotation = TDWUtils.array_to_vector3(rotation)
        """:field
        The [`DroneDynamic`](../drone/drone_dynamic.md) data.
        """
        self.dynamic: Optional[DroneDynamic] = None
        """:field
        The ID of this drone.
        """
        self.drone_id: int = drone_id
        self._name: str = name
        """:field
        The ID of the drone's avatar (camera). This is used internally for API calls.
        """
        self.avatar_id: str = str(drone_id)
        self._forward_speed: float = forward_speed
        self._backward_speed: float = backward_speed
        self._rise_speed: float = rise_speed
        self._drop_speed: float = drop_speed
        self._acceleration: float = acceleration
        self._deceleration: float = deceleration
        self._stability: float = stability
        self._turn_sensitivity: float = turn_sensitivity
        self._enable_lights: bool = enable_lights
        self._lift: int = 0
        self._drive: int = 0
        self._turn: int = 0
        self._initial_motor_on = motor_on
        # This is used when saving images.
        self._frame_count: int = 0
        # Initialize the Replicant metadata library.
        if Drone.LIBRARY_NAME not in Controller.DRONE_LIBRARIANS:
            Controller.DRONE_LIBRARIANS[Drone.LIBRARY_NAME] = DroneLibrarian(Drone.LIBRARY_NAME)
        # The Replicant metadata record.
        self._record: DroneRecord = Controller.DRONE_LIBRARIANS[Drone.LIBRARY_NAME].get_record(name)
        self._image_capture: bool = image_capture
        if image_passes is None:
            self._image_passes: List[str] = ["_img", "_depth"]
        else:
            self._image_passes = image_passes

    def get_initialization_commands(self) -> List[dict]:
        """
        This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

        :return: A list of commands that will initialize this add-on.
        """

        commands = [{"$type": "add_drone", 
                     "id": self.drone_id,
                     "name": self._name,
                     "url": self._record.get_url(), 
                     "position": self.initial_position,
                     "rotation": self.initial_rotation,
                     "rise_speed": self._rise_speed,
                     "drop_speed": self._drop_speed,
                     "forward_speed": self._forward_speed,
                     "backward_speed": self._backward_speed,
                     "acceleration": self._acceleration,
                     "deceleration": self._deceleration,
                     "stability": self._stability,
                     "turn_sensitivity": self._turn_sensitivity,
                     "enable_lights": self._enable_lights,
                     "motor_on": self._initial_motor_on},
                    {"$type": "create_avatar",
                     "type": "A_Img_Caps_Kinematic",
                     "id": self.avatar_id},
                    {"$type": "parent_avatar_to_drone",
                     "position": {"x": 0, "y": -0.1, "z": 0},
                     "avatar_id": self.avatar_id,
                     "id": self.drone_id},
                    {"$type": "rotate_sensor_container_by", 
                     "axis": "pitch", 
                     "angle": 45.0,
                     "avatar_id": self.avatar_id},
                    {"$type": "send_transforms",
                     "frequency": "always"},
                    {"$type": "send_drones",
                     "frequency": "always"}]
        if self._image_capture:
            commands.extend([{"$type": "set_pass_masks",
                              "pass_masks": self._image_passes,
                              "avatar_id": self.avatar_id},
                             {"$type": "set_img_pass_encoding",
                              "value": False},
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
        self.dynamic = DroneDynamic(resp=resp, drone_id=self.drone_id, frame_count=self._frame_count)
        if self.dynamic.got_images:
            self._frame_count += 1

        # Add commands for elevation and forward motion.
        self.commands.extend([{"$type": "apply_drone_drive",
                               "id": self.drone_id,
                               "force": self._drive},
                              {"$type": "apply_drone_lift",
                               "id": self.drone_id,
                               "force": self._lift},
                              {"$type": "apply_drone_turn",
                               "id": self.drone_id,
                               "force": self._turn}])
      
    def set_lift(self, lift: int) -> None:
        """
        Set the drone's lift force.

        :param lift: The lift force. Must be -1, 0, or 1.
        """

        self._lift = Drone._get_clamped_force(lift)

    def set_drive(self, drive: int) -> None:
        """
        Set the drone's drive force.

        :param drive: The drive force. Must be -1, 0, or 1.
        """

        self._drive = Drone._get_clamped_force(drive)

    def set_turn(self, turn: int) -> None:
        """
        Set the drone's turn force.

        :param turn: The turn force. Must be -1, 0, or 1.
        """

        self._turn = Drone._get_clamped_force(turn)

    def set_motor(self, motor_on: bool) -> None:
        """
        Turn the drone's motor on or off.

        :param motor_on: If True, turn the motor on. If False, turn the motor off.
        """

        self._lift = 0
        self._turn = 0
        self._drive = 0
        self.commands.append({"$type": "set_drone_motor",
                              "motor_on": motor_on})

    def set_speed(self, forward_speed: float = 3, backward_speed: float = 3) -> None:
        """
        Set the drone's forward and/or backward speeds.

        :param forward_speed: The forward speed. Must be between 0 and 20.0.
        :param forward_speed: The forward speed. Must be between 0 and 20.0.
        """

        self.commands.append({"$type": "set_drone_speed",
                              "id": self.drone_id,
                              "forward_speed": Drone._get_clamped_speed(forward_speed),
                              "backward_speed": Drone._get_clamped_speed(backward_speed)})

    @staticmethod
    def _get_clamped_force(force: int) -> float:
        """
        :param force: The force input value.

        :return: The force clamped between -1 and 1.
        """

        return int(max(min(force, 1), -1))

    @staticmethod
    def _get_clamped_speed(speed: float) -> float:
        """
        :param speed: The speed input value.

        :return: The speed clamped between 0 and 20.
        """

        return float(max(min(speed, 20.0), 0))
