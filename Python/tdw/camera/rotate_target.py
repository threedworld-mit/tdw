from enum import Enum
from typing import List, Union, Dict, Tuple, Optional
import numpy as np
from tdw.tdw_utils import TDWUtils, QuaternionUtils
from tdw.camera.camera_target import CameraTarget
from tdw.output_data import OutputData, ImageSensors


class _TargetType(Enum):
    """
    The type of rotation target, given the `target` parameter in the constructor.
    """

    none = 1
    obj = 2
    pos = 4
    rpy = 8
    rot = 16


class RotateTarget(CameraTarget):
    """
    Rotate to or towards a target object, position, or rotation.
    """

    def __init__(self, resp: List[bytes], avatar_id: str, target: Union[int, Dict[str, float]] = None, speed: float = None,
                 centroid: bool = True):
        """
        :param resp: The most recent response from the build.
        :param avatar_id: The ID of the avatar (the camera).
        :param target: If an `int`, rotate to look at an object with a matching ID. If `Dict[str, float]`: If the keys are `[x, y, z, w]`, rotate to or towards the quaternion. If the keys are `[x, y, z]`, rotate to or towards a position. If the keys are `[r, p, y]`, rotate to or towards RPY angles in degrees.
        :param speed: If None, the camera will instantly rotate to the target. Otherwise, the camera will rotate the target this many degrees per frame.
        :param centroid: If True and `target` is an `int`, use the centroid of the target object as the target. If False and `target` is an `int`, use the bottom-center of the object as the target.
        """

        super().__init__(avatar_id=avatar_id, target=target, speed=speed, centroid=centroid)

        if resp is None:
            resp = list()

        # The target rotation, assuming that the target isn't moving (i.e. isn't an object).
        self._target_rotation: Optional[Dict[str, float]] = None

        # Set the target type.
        self._target_type: _TargetType
        if self.target is None:
            self._target_type = _TargetType.none
        elif isinstance(self.target, int):
            self._target_type = _TargetType.obj
        elif isinstance(self.target, dict):
            if "r" in self.target and "p" in self.target and "y" in self.target:
                self._target_type = _TargetType.rpy
                image_sensors, rotation, forward = self._get_image_sensor(resp=resp)
                if image_sensors:
                    eulers = QuaternionUtils.quaternion_to_euler_angles(rotation)
                    eulers[0] += self.target["r"]
                    eulers[1] += self.target["p"]
                    eulers[2] += self.target["y"]
                else:
                    eulers = np.array([self.target["r"], self.target["p"], self.target["y"]])
                self._target_rotation = TDWUtils.array_to_vector4(
                    QuaternionUtils.euler_angles_to_quaternion(np.deg2rad(eulers)))
            elif "x" in self.target and "y" in self.target and "z" in self.target:
                if "w" in self.target:
                    self._target_type = _TargetType.rot
                    self._target_rotation = self.target
                else:
                    self._target_type = _TargetType.pos
            else:
                raise Exception(f"Bad target dictionary: {self.target}")
        else:
            raise TypeError(f"Bad target: {self.target}")

    def _get_instant_commands(self, resp: List[bytes]) -> List[dict]:
        # If there's no target, reset the rotation.
        if self._target_type == _TargetType.none:
            return [{"$type": "reset_sensor_container_rotation",
                     "avatar_id": self.avatar_id}]
        # Rotate to look at a target.
        elif self._target_type == _TargetType.pos:
            return [{"$type": "look_at",
                     "object_id": self.target,
                     "use_centroid": self.centroid,
                     "avatar_id": self.avatar_id}]
        elif self._target_type == _TargetType.rpy:
            for a, axis in zip(["r", "p", "y"], ["roll", "pitch", "yaw"]):
                return [{"$type": "rotate_sensor_container_by",
                         "axis": "pitch",
                         "angle": self.target[a],
                         "avatar_id": self.avatar_id}]
        elif self._target_type == _TargetType.pos:
            return [{"$type": "look_at_position",
                     "position": self.target,
                     "avatar_id": self.avatar_id}]
        elif self._target_type == _TargetType.rot:
            return [{"$type": "rotate_sensor_container_to",
                     "rotation": self.target,
                     "avatar_id": self.avatar_id}]
        else:
            raise Exception(f"Not defined: {self._target_type}")

    def _get_lerp_commands(self, resp: List[bytes]) -> List[dict]:
        # Rotate towards the default rotation.
        if self._target_type == _TargetType.none:
            return [{"$type": "rotate_sensor_container_towards_rotation",
                     "avatar_id": self.avatar_id,
                     "speed": self.speed}]
        else:
            # Rotate towards the current position of the target.
            if self._target_type == _TargetType.obj:
                return [{"$type": "rotate_sensor_container_towards_object",
                         "avatar_id": self.avatar_id,
                         "speed": self.speed,
                         "object_id": self.target,
                         "use_centroid": self.centroid}]
            # Rotate towards a set rotation.
            elif self._target_type == _TargetType.rot or self._target_type == _TargetType.rpy:
                return [{"$type": "rotate_sensor_container_towards_rotation",
                         "avatar_id": self.avatar_id,
                         "speed": self.speed,
                         "rotation": self._target_rotation}]
            elif self._target_type == _TargetType.pos:
                return [{"$type": "rotate_sensor_container_towards_position",
                         "avatar_id": self.avatar_id,
                         "speed": self.speed,
                         "target": self.target}]
            else:
                raise Exception(f"Not defined: {self._target_type}")

    def _get_image_sensor(self, resp: List[bytes]) -> Tuple[bool, np.array, np.array]:
        """
        :param resp: The most recent response from the build.

        :return: True if we got image sensor data, the current rotation and forward of the image sensor.
        """

        # Get the current rotation of the sensor container.
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "imse":
                imse = ImageSensors(resp[i])
                if imse.get_avatar_id() == self.avatar_id:
                    return True, np.array(imse.get_sensor_rotation(0)), np.array(imse.get_sensor_forward(0))
        return False, np.array([0, 0, 0, 0]), np.array([0, 0, 0])
