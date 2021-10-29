from enum import Enum
from typing import List, Dict, Optional, Union
import numpy as np
from tdw.tdw_utils import TDWUtils, QuaternionUtils
from tdw.output_data import OutputData, AvatarKinematic, ImageSensors, CameraMotionComplete
from tdw.add_ons.third_person_camera_base import ThirdPersonCameraBase


class _MoveTargetType(Enum):
    """
    A type of target that the camera can move towards.
    """

    position = 1
    object = 2


class _RotateTargetType(Enum):
    """
    A type of target that the camera can rotate towards.
    """

    position = 1
    object = 2
    rotation = 4


class _FocusTargetType(Enum):
    """
    A type of target that the camera can focus towards.
    """

    position = 1
    object = 2
    distance = 4


class CinematicCamera(ThirdPersonCameraBase):
    """
    Wrapper class for third-person camera controls in TDW. These controls are "cinematic" in the sense that the camera will move, rotate, etc. *towards* a target at a set speed per frame. The `CinematicCamera` class is suitable for demo videos of TDW, but *not* for most actual experiments.
    """

    def __init__(self, avatar_id: str = None, position: Dict[str, float] = None, rotation: Dict[str, float] = None,
                 field_of_view: int = None, move_speed: float = 0.1, rotate_speed: float = 1,
                 look_at: Union[int, Dict[str, float]] = None, focus_distance: float = 6):
        """
        :param avatar_id: The ID of the avatar (camera). If None, a random ID is generated.
        :param position: The initial position of the object.If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param rotation: The initial rotation of the camera. Can be Euler angles (keys are `(x, y, z)`) or a quaternion (keys are `(x, y, z, w)`). If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param field_of_view: If not None, set the field of view.
        :param move_speed: The directional speed of the camera. This can later be adjusted by setting `self.move_speed`.
        :param rotate_speed: The angular speed of the camera. This can later be adjusted by setting `self.rotate_speed`.
        :param look_at: If not None, the cinematic camera will look at this object (if int) or position (if dictionary).
        :param focus_distance: The initial focus distance. Ignore if `look_at` is an object ID (in which case the camera will focus on the target object).
        """

        super().__init__(avatar_id=avatar_id, position=position, rotation=rotation, field_of_view=field_of_view)
        """:field
        The directional speed of the camera.
        """
        self.move_speed: float = move_speed
        """:field
        The angular speed of the camera.
        """
        self.rotate_speed: float = rotate_speed

        # A target object ID or position to move towards. Can be None (no target).
        self._move_target: Optional[Union[int, Dict[str, float]]] = None
        # If `self._move_target` is an int, try to stay this far away from the target object.
        self._move_distance_offset: float = 0
        # If `self._move_target` is not None, clamp the height of the camera to this minimal value.
        self._move_min_y: float = 0.25
        # The type of move target.
        self._move_target_type: _MoveTargetType = _MoveTargetType.position
        """:field
        If True, the camera is moving.
        """
        self.moving: bool = False

        # A target object ID, position, quaternion, or Euler angles to rotate to. Can be None (no target).
        self._rotate_target: Optional[Union[int, Dict[str, float]]] = None
        # The type of rotate target.
        self._rotate_target_type: _RotateTargetType = _RotateTargetType.position
        """:field
        If True, the camera is rotating.
        """
        self.rotating: bool = False
        self._look_at: Optional[Union[int, Dict[str, float]]] = look_at
        # The current forward directional vector of the image sensor.
        self._sensor_forward: np.array = np.array([0, 0, 0])
        # The current rotation of the image sensor.
        self._sensor_rotation: np.array = np.array([0, 0, 0, 0])
        # The object ID of the focus target.
        self._focus_target: Union[int, float, Dict[str, float]] = focus_distance
        # The type of focus target.
        self._focus_target_type: _FocusTargetType = _FocusTargetType.distance

    def get_initialization_commands(self) -> List[dict]:
        commands = super().get_initialization_commands()
        commands.extend([{"$type": "send_avatars",
                          "frequency": "always"},
                         {"$type": "send_image_sensors",
                          "frequency": "always"}])
        if self._look_at is not None:
            # Look at and focus on the object.
            if isinstance(self._look_at, int):
                commands.extend([{"$type": "look_at",
                                  "object_id": self._look_at,
                                  "use_centroid": True,
                                  "avatar_id": self.avatar_id},
                                 {"$type": "focus_on_object",
                                  "object_id": self._look_at,
                                  "use_centroid": True,
                                  "avatar_id": self.avatar_id}])
                # Continue to look at the object.
                self.rotate_to_object(target=self._look_at)
            # Look at and focus on the position.
            elif isinstance(self._look_at, dict):
                distance = np.linalg.norm(TDWUtils.vector3_to_array(self.position) - TDWUtils.vector3_to_array(self._look_at))
                commands.extend([{"$type": "look_at_position",
                                  "position": self._look_at,
                                  "avatar_id": self.avatar_id},
                                 {"$type": "set_focus_distance",
                                  "focus_distance": distance}])
                # Continue to look at the position.
                self.rotate_to_position(target=self._look_at)
            else:
                raise TypeError(f"Invalid look-at target: {self._look_at}")
        # Focus on the target distance.
        else:
            commands.append({"$type": "set_focus_distance",
                             "focus_distance": self._focus_target})
        return commands

    def on_send(self, resp: List[bytes]) -> None:
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "camm":
                cam = CameraMotionComplete(resp[i])
                if cam.get_avatar_id() == self.avatar_id:
                    m = cam.get_motion()
                    if m == "move":
                        self.stop_moving()
                    elif m == "rotate":
                        self.stop_rotating()
                    elif m == "focus":
                        pass
                    else:
                        raise Exception(f"Motion state not defined: {m}")
            elif r_id == "imse":
                imse = ImageSensors(resp[i])
                if imse.get_avatar_id() == self.avatar_id:
                    self._sensor_forward = np.array(imse.get_sensor_forward(0))
                    self._sensor_rotation = np.array(imse.get_sensor_rotation(0))
            elif r_id == "avki":
                a = AvatarKinematic(resp[i])
                if a.get_avatar_id() == self.avatar_id:
                    self.position = TDWUtils.array_to_vector3(a.get_position())
        if self._move_target is not None:
            if self._move_target_type == _MoveTargetType.position:
                self.commands.append({"$type": "move_avatar_towards_position",
                                      "position": self._move_target,
                                      "speed": self.move_speed,
                                      "avatar_id": self.avatar_id})
            elif self._move_target_type == _MoveTargetType.object:
                self.commands.append({"$type": "move_avatar_towards_object",
                                      "object_id": self._move_target,
                                      "offset_distance": self._move_distance_offset,
                                      "min_y": self._move_min_y,
                                      "use_centroid": True,
                                      "speed": self.move_speed,
                                      "avatar_id": self.avatar_id})
            else:
                raise Exception(f"Invalid move target type: {self._move_target_type}")
        # Rotate towards a target.
        if self._rotate_target is not None:
            if self._rotate_target_type == _RotateTargetType.rotation:
                self.commands.append({"$type": "rotate_sensor_container_towards_rotation",
                                      "avatar_id": self.avatar_id,
                                      "rotation": self._rotate_target,
                                      "speed": self.rotate_speed})
            elif self._rotate_target_type == _RotateTargetType.object:
                self.commands.append({"$type": "rotate_sensor_container_towards_object",
                                      "avatar_id": self.avatar_id,
                                      "speed": self.rotate_speed,
                                      "object_id": self._rotate_target,
                                      "use_centroid": True})
            elif self._rotate_target_type == _RotateTargetType.position:
                self.commands.append({"$type": "rotate_sensor_container_towards_position",
                                      "avatar_id": self.avatar_id,
                                      "position": self._rotate_target,
                                      "speed": self.rotate_speed})
            else:
                raise Exception(f"Invalid rotate target type: {self._move_target_type}")
        # Set the focus.
        if self._focus_target_type == _FocusTargetType.distance:
            self.commands.append({"$type": "set_focus_distance",
                                  "focus_distance": self._focus_target})
        elif self._focus_target_type == _FocusTargetType.position:
            self.commands.append({"$type": "set_focus_distance",
                                  "focus_distance": np.linalg.norm(TDWUtils.vector3_to_array(self.position) -
                                                                   TDWUtils.vector3_to_array(self._focus_target))})
        elif self._focus_target_type == _FocusTargetType.object:
            self.commands.append({"$type": "focus_on_object",
                                  "avatar_id": self.avatar_id,
                                  "object_id": self._focus_target,
                                  "use_centroid": True})
        else:
            raise Exception(f"Invalid focus target type: {self._focus_target_type}")

    def move_to_position(self, target: Dict[str, float], relative: bool = False) -> None:
        """
        Start moving towards a target position.

        :param relative: If True, the target is relative to the current position of the avatar. If False, the target is in absolute worldspace coordinates.
        :param target: The target position.
        """

        if relative:
            self._move_target = TDWUtils.array_to_vector3(TDWUtils.vector3_to_array(target) +
                                                          TDWUtils.vector3_to_array(self.position))
        else:
            self._move_target = target
        self._move_target_type = _MoveTargetType.position
        self.moving = True

    def move_to_object(self, target: int, offset_distance: float = 1, min_y: float = 0.25) -> None:
        """
        Start moving towards a target object.

        :param target: The ID of the target object.
        :param offset_distance: Stop moving when the camera is this far away from the object.
        :param min_y: Clamp the y positional coordinate of the camera to this minimum value.
        """

        self._move_target = target
        self._move_distance_offset = offset_distance
        self._move_min_y = min_y
        self._move_target_type = _MoveTargetType.object
        self.moving = True

    def stop_moving(self) -> None:
        """
        Stop moving towards the current target.
        """

        self._move_target = None
        self.moving = False

    def rotate_to_object(self, target: int) -> None:
        """
        Rotate towards an object. This will update if

        :param target: The ID of the target object.
        """

        self._rotate_target = target
        self._rotate_target_type = _RotateTargetType.object
        self.rotating = True
        self._focus_target = target
        self._focus_target_type = _FocusTargetType.object

    def rotate_to_position(self, target: Dict[str, float]) -> None:
        """
        Start to rotate towards a position.

        :param target: The target position.
        """

        self._rotate_target = target
        self._rotate_target_type = _RotateTargetType.position
        self.rotating = True
        self._focus_target = target
        self._focus_target_type = _FocusTargetType.position

    def rotate_by_rpy(self, target: Dict[str, float]) -> None:
        """
        Rotate the camera by the `[pitch, yaw, roll]` angles expressed as an `[x, y, z]` dictionary.

        :param target: The target `[pitch, yaw, roll]` angles from when this function was first called, in degrees.
        """

        eulers = QuaternionUtils.quaternion_to_euler_angles(self._sensor_rotation)
        eulers[0] += target["x"]
        eulers[1] += target["y"]
        eulers[2] += target["z"]
        self._rotate_target = TDWUtils.array_to_vector4(
            QuaternionUtils.euler_angles_to_quaternion(np.deg2rad(eulers)))
        self._rotate_target_type = _RotateTargetType.rotation
        self.rotating = True

    def rotate_to_rotation(self, target: Dict[str, float]) -> None:
        """
        Rotate towards a rotation quaternion.

        :param target: The target rotation.
        """

        self._rotate_target = target
        self._rotate_target_type = _RotateTargetType.rotation
        self.rotating = True

    def stop_rotating(self) -> None:
        """
        Stop rotating towards the current target.
        """

        self._rotate_target = None
        self.rotating = False

    def set_focus_distance(self, target: float) -> None:
        """
        Set the focus distance.

        :param target: The focus distance.
        """

        self._focus_target = target
        self._focus_target_type = _FocusTargetType.distance

    def focus_on_object(self, target: int) -> None:
        """
        Set the focus distance to the distance from the camera to an object. This will update every frame as the camera or object moves.

        :param target: The object ID.
        """

        self._focus_target = target
        self._focus_target_type = _FocusTargetType.object
