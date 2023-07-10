from typing import List, Optional, Dict
import numpy as np
from tdw.type_aliases import POSITION, ROTATION
from tdw.add_ons.add_on import AddOn
from tdw.vehicle.vehicle_dynamic import VehicleDynamic
from tdw.controller import Controller
from tdw.tdw_utils import TDWUtils
from tdw.librarian import VehicleRecord, VehicleLibrarian


class Vehicle(AddOn):
    """
    A vehicle is a driving agent such as a car, bus or truck. From this API, you can set the vehicles's speed (drive, turn, brake) and turn its motor on and off.

    The vehicle's output data, including images, is stored in [`vehicle.dynamic`](../vehicle/vehicle_dynamic.md).
    """

    """:class_var
    The vehicle's library file. You can override this to use a custom library (e.g. a local library).
    """
    LIBRARY_NAME: str = "vehicles.json"

    def __init__(self, vehicle_id: int = 0, position: POSITION = None, rotation: ROTATION = None,
                 name: str = "all_terrain_vehicle", forward_speed: float = 30, reverse_speed: float = 12,
                 image_capture: bool = True, image_passes: List[str] = None):
        """
        :param vehicle_id: The ID of the vehicle.
        :param position: The position of the vehicle as an x, y, z dictionary or numpy array. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param rotation: The rotation of the vehicle in Euler angles (degrees) as an x, y, z dictionary or numpy array. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param name: The name of the vehicle model.
        :param forward_speed: Sets the vehicle's max forward speed.
        :param reverse_speed: Sets the vehicle's max reverse speed.
        :param image_capture: If True, the vehicle will receive image and camera matrix data per `communicate()` call. Whether or not this is True, the vehicle will always render images in the simulation window.
        :param image_passes: A list of image passes that will be captured. Ignored if `image_capture == False`. If None, defaults to `["_img", "_id"]`.
        """

        super().__init__()

        if position is None:
            """:field
            The initial position of the vehicle.
            """
            self.initial_position: Dict[str, float] = {"x": 0, "y": 0, "z": 0}
        elif isinstance(position, dict):
            self.initial_position = position
        elif isinstance(position, np.ndarray):
            self.initial_position = TDWUtils.array_to_vector3(position)
        else:
            raise Exception(position)
        """:field
        The initial rotation of the vehicle in Euler angles.
        """
        if rotation is None:
            self.initial_rotation: Dict[str, float] = {"x": 0, "y": 0, "z": 0}
        elif isinstance(rotation, dict):
            self.initial_rotation = rotation
        elif isinstance(rotation, np.ndarray):
            self.initial_rotation = TDWUtils.array_to_vector3(rotation)
        """:field
        The [`VehicleDynamic`](../vehicle/vehicle_dynamic.md) data.
        """
        self.dynamic: Optional[VehicleDynamic] = None
        """:field
        The ID of this vehicle.
        """
        self.vehicle_id: int = vehicle_id
        self._name: str = name
        """:field
        The ID of the vehicle's avatar (camera). This is used internally for API calls.
        """
        self.avatar_id: str = str(vehicle_id)
        self._forward_speed: float = forward_speed
        self._reverse_speed: float = reverse_speed
        self._drive: float = 0
        self._turn: float = 0
        self._brake: float = 0
        # This is used when saving images.
        self._frame_count: int = 0
        # Initialize the vehicle metadata library.
        if Vehicle.LIBRARY_NAME not in Controller.VEHICLE_LIBRARIANS:
            Controller.VEHICLE_LIBRARIANS[Vehicle.LIBRARY_NAME] = VehicleLibrarian(Vehicle.LIBRARY_NAME)
        # The vehicle metadata record.
        self._record: VehicleRecord = Controller.VEHICLE_LIBRARIANS[Vehicle.LIBRARY_NAME].get_record(name)
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

        commands = [{"$type": "add_vehicle", 
                     "id": self.vehicle_id,
                     "name": self._name,
                     "url": self._record.get_url(), 
                     "position": self.initial_position,
                     "rotation": self.initial_rotation,
                     "forward_speed": self._forward_speed,
                     "reverse_speed": self._reverse_speed},
                    {"$type": "create_avatar",
                     "type": "A_Img_Caps_Kinematic",
                     "id": self.avatar_id},
                    # Add camera and position to approximately driver head height, just in front of windshield.
                    # Other vehicle assets will likely require adjusting these values.
                    {"$type": "parent_avatar_to_vehicle",
                     "position": {"x": 0, "y": 1.75, "z": 1.0},
                     "avatar_id": self.avatar_id,
                     "id": self.vehicle_id},
                    {"$type": "rotate_sensor_container_by", 
                     "axis": "pitch", 
                     "angle": 0,
                     "avatar_id": self.avatar_id},
                    {"$type": "send_transforms",
                     "frequency": "always"},
                    {"$type": "send_rigidbodies",
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
        self.dynamic = VehicleDynamic(resp=resp, agent_id=self.vehicle_id, frame_count=self._frame_count)
        if self.dynamic.got_images:
            self._frame_count += 1

        # Add commands for elevation and forward motion.
        self.commands.extend([{"$type": "apply_vehicle_drive",
                               "id": self.vehicle_id,
                               "force": self._drive},
                              {"$type": "apply_vehicle_turn",
                               "id": self.vehicle_id,
                               "force": self._turn},
                              {"$type": "apply_vehicle_brake",
                               "id": self.vehicle_id,
                               "force": self._brake}])

    def set_drive(self, drive: float) -> None:
        """
        Set the vehicle's drive force.

        :param drive: The drive force as a float. Must be between -1.0 and 1.0.
        """

        self._drive = Vehicle._get_clamped_force(drive)

    def set_turn(self, turn: float) -> None:
        """
        Set the vehicle's turn force.

        :param turn: The turn force as a float. Must be between -1.0 and 1.0.
        """

        self._turn = Vehicle._get_clamped_force(turn)

    def set_brake(self, brake: float) -> None:
        """
        Set the vehicle's brake force.

        :param brake: The brake force as a float. Must be between -1.0 and 1.0.
        """

        self._brake = Vehicle._get_clamped_force(brake)

    @staticmethod
    def _get_clamped_force(force: float) -> float:
        """
        :param force: The force input value.

        :return: The force clamped between -1 and 1.
        """

        return max(min(force, 1), -1)
