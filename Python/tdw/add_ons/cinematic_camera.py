from enum import Enum
from typing import List, Dict, Optional, Union, Tuple
import numpy as np
from tdw.tdw_utils import TDWUtils, QuaternionUtils
from tdw.output_data import OutputData, Bounds, AvatarKinematic, ImageSensors, CameraMotionComplete
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


class CinematicCamera(ThirdPersonCameraBase):
    """
    Wrapper class for third-person camera controls in TDW. These controls are "cinematic" in the sense that the camera will move, rotate, etc. *towards* a target at a set speed per frame. The `CinematicCamera` class is suitable for demo videos of TDW, but *not* for most actual experiments.

    ```python
    from tdw.controller import Controller
    from tdw.tdw_utils import TDWUtils
    from tdw.add_ons.cinematic_camera import CinematicCamera

    c = Controller(launch_build=False)
    c.start()
    cam = CinematicCamera(position={"x": 0, "y": 1.5, "z": 0},
                          rotation={"x": 2, "y": 45, "z": 0},
                          move_speed=0.1,
                          rotate_speed=3,
                          focus_speed=0.3)
    c.add_ons.append(cam)
    c.communicate(TDWUtils.create_empty_room(12, 12))
    ```

    Each function in this class will *start* to move the camera but won't actually send commands (because this is not an `AddOn`, not a `Controller`).

    To actually apply changes to the camera and the scene, you need to send commands to the build like you normally would. In this example, the list of commands is empty, but it doesn't have to be:

    ```python
    from tdw.controller import Controller
    from tdw.tdw_utils import TDWUtils
    from tdw.add_ons.cinematic_camera import CinematicCamera

    c = Controller(launch_build=False)
    c.start()
    cam = CinematicCamera(position={"x": 0, "y": 1.5, "z": 0},
                          rotation={"x": 2, "y": 45, "z": 0},
                          move_speed=0.1,
                          rotate_speed=3,
                          focus_speed=0.3)
    c.add_ons.append(cam)

    # Set a movement target for the camera. This won't actually send any commands!
    cam.move_to_position(target={"x": 1, "y": 2, "z": -0.5})

    c.communicate(TDWUtils.create_empty_room(12, 12))
    for i in range(100):
        c.communicate([])
    ```

    Note that all objects that you want the camera to move to must be in the scene *before* adding the camera:

    ```python
    from tdw.controller import Controller
    from tdw.tdw_utils import TDWUtils
    from tdw.add_ons.cinematic_camera import CinematicCamera

    object_id = 0
    c = Controller(launch_build=False)
    c.start()
    c.communicate([TDWUtils.create_empty_room(12, 12),
                   c.get_add_object(model_name="iron_box", object_id=object_id)])
    cam = CinematicCamera(position={"x": 4, "y": 1.5, "z": 0},
                          rotation={"x": 2, "y": 45, "z": 0})
    c.add_ons.append(cam)

    # Look at the target object.
    cam.move_to_object(target=object_id, offset_distance=1)
    cam.rotate_to_object(target=object_id)

    for i in range(500):
        c.communicate([])
    ```

    ## Possible motions

    - **Move** towards a target object or position
    - **Rotate** towards a target quaternion, Euler angles; or rotate to look at a target position or object
    - **Focus** towards a target distance or object. Focusing is handled implicitly whenever the camera is rotating towards a target object.

    ## Stopping motions

    There are two ways to stop a camera motion:

    1. Call `cam.stop_moving()` or `cam.stop_rotating()`:

    ```python
    from tdw.controller import Controller
    from tdw.tdw_utils import TDWUtils
    from tdw.add_ons.cinematic_camera import CinematicCamera

    object_id = 0
    c = Controller(launch_build=False)
    c.start()
    c.communicate([TDWUtils.create_empty_room(12, 12),
                   c.get_add_object(model_name="iron_box", object_id=object_id)])
    cam = CinematicCamera(position={"x": 4, "y": 1.5, "z": 0},
                          rotation={"x": 2, "y": 45, "z": 0})
    c.add_ons.append(cam)

    # Look at the target object.
    cam.move_to_object(target=object_id, offset_distance=1)
    cam.rotate_to_object(target=object_id)

    for i in range(20):
        c.communicate([])

    # Stop moving and rotating the camera.
    cam.stop_rotating()
    cam.stop_moving()

    for i in range(500):
        c.communicate([])
    ```

    2. Call `cam.motions_are_done(resp)`, which will return a dictionary indicating whether the each type of motion is done:

    ```python
    from tdw.controller import Controller
    from tdw.tdw_utils import TDWUtils
    from tdw.add_ons.cinematic_camera import CinematicCamera

    object_id = 0
    c = Controller(launch_build=False)
    c.start()
    c.communicate([TDWUtils.create_empty_room(12, 12),
                   c.get_add_object(model_name="iron_box", object_id=object_id)])
    cam = CinematicCamera(position={"x": 4, "y": 1.5, "z": 0},
                          rotation={"x": 2, "y": 45, "z": 0})
    c.add_ons.append(cam)

    # Look at the target object.
    cam.move_to_object(target=object_id, offset_distance=1)
    cam.rotate_to_object(target=object_id)

    done = False
    while not done:
        resp = c.communicate([])
        motions = cam.motions_are_done(resp=resp)
        done = motions["move"] and motions["rotate"]
    print("Done!")
    c.communicate({"$type": "terminate"})
    ```

    ## Output Data

    This object requires certain output data, which it will automatically request via `cam.init_commands`. If you're not already requesting this data per frame, you might notice that the simulation runs slightly slower.

    The output data will include:

    - `Bounds` (for all objects in the scene)
    - Avatar data (for all avatars in the scene; for this avatar, it's `AvatarKinematic`)
    - `ImageSensors` (for all avatars in the scene)
    - `CameraMotionComplete` (for this avatar and any other cinematic cameras, whenever the avatar finishes a motion)

    ## Saving Images

    To save images per frame, include an `ImageCapture` add-on to the Controller:

    ```python
    from tdw.controller import Controller
    from tdw.tdw_utils import TDWUtils
    from tdw.add_ons.cinematic_camera import CinematicCamera
    from tdw.add_ons.image_capture import ImageCapture

    object_id = 0
    c = Controller(launch_build=False)
    c.start()
    c.communicate([TDWUtils.create_empty_room(12, 12),
                   c.get_add_object(model_name="iron_box", object_id=object_id)])
    cam = CinematicCamera(position={"x": 4, "y": 1.5, "z": 0},
                          rotation={"x": 2, "y": 45, "z": 0})
    cap = ImageCapture(path="D:/cinematic_camera_demo", avatar_ids=[cam.avatar_id])
    c.add_ons.extend([cam, cap])

    # Look at the target object.
    cam.move_to_object(target=object_id, offset_distance=1)
    cam.rotate_to_object(target=object_id)

    done = False
    while not done:
        resp = c.communicate([])
        motions = cam.motions_are_done(resp=resp)
        done = motions["move"] and motions["rotate"]
    print("Done!")
    c.communicate({"$type": "terminate"})
    ```
    """

    def __init__(self, avatar_id: str = None, position: Dict[str, float] = None, rotation: Dict[str, float] = None,
                 fov: int = None, pass_masks: List[str] = None, framerate: int = None,
                 move_speed: float = 0.1, rotate_speed: float = 3, focus_speed: float = 0.3):
        """
        :param avatar_id: The ID of the avatar (camera). If None, a random ID is generated.
        :param position: The initial position of the object.If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param rotation: The initial rotation of the camera. Can be Euler angles (keys are `(x, y, z)`) or a quaternion (keys are `(x, y, z, w)`). If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param fov: If not None, this is the initial field of view. Otherwise, defaults to 35.
        :param pass_masks: The pass masks. If None, defaults to `["_img"]`.
        :param framerate: If not None, sets the target framerate.
        :param move_speed: The directional speed of the camera. This can later be adjusted by setting `self.move_speed`.
        :param rotate_speed: The angular speed of the camera. This can later be adjusted by setting `self.rotate_speed`.
        :param focus_speed: The speed of the focus of the camera. This can later be adjusted by setting `self.focus_speed`.
        """

        super().__init__(avatar_id=avatar_id, position=position, rotation=rotation, fov=fov, pass_masks=pass_masks,
                         framerate=framerate)
        """:field
        The directional speed of the camera. This can later be adjusted by setting `self.move_speed`.
        """
        self.move_speed: float = move_speed
        """:field
        The angular speed of the camera. This can later be adjusted by setting `self.rotate_speed`.
        """
        self.rotate_speed: float = rotate_speed
        """:field
        The speed of the focus of the camera. This can later be adjusted by setting `self.focus_speed`.
        """
        self.focus_speed: float = focus_speed

        self._init_commands.extend([{"$type": "send_avatars",
                                     "frequency": "always"},
                                    {"$type": "send_bounds",
                                     "frequency": "always"},
                                    {"$type": "send_image_sensors",
                                     "frequency": "always"}])

        # A target object ID or position to move towards. Can be None (no target).
        self._move_target: Optional[Union[int, Dict[str, float]]] = None
        # If `self._move_target` is an int, try to stay this far away from the target object.
        self._move_distance_offset: float = 0
        # If `self._move_target` is not None, clamp the height of the camera to this minimal value.
        self._move_min_y: float = 0.25
        # The type of move target.
        self._move_target_type: _MoveTargetType = _MoveTargetType.position
        # If `self.move_target` is relative to the current position, temporarily store the relative target here.
        self._relative_translation: Dict[str, float] = {"x": 0, "y": 0, "z": 0}
        # This boolean is used as a state machine to let the camera know that it needs to apply `self._relative_translation` to its current position.
        self._has_relative_translation: bool = False

        # A target object ID, position, quaternion, or Euler angles to rotate to. Can be None (no target).
        self._rotate_target: Optional[Union[int, Dict[str, float]]] = None
        # The type of rotate target.
        self._rotate_target_type: _RotateTargetType = _RotateTargetType.position
        # If `self._rotate_target` is Euler angles, temporarily store them here.
        self._eulers: Dict[str, float] = {"x": 0, "y": 0, "z": 0}
        # This boolean is used as a state machine to let the camera know that it needs to apply `self._eulers` to its current rotation.
        self._has_eulers: bool = False

    def on_communicate(self, resp: List[bytes], commands: List[dict]) -> None:
        # Set a relative target.
        if self._has_relative_translation:
            origin = self._get_avatar_position(resp=resp)
            self._move_target = origin + TDWUtils.vector3_to_array(self._relative_translation)
            self._has_relative_translation = False
        if self._move_target is not None:
            if self._move_target_type == _MoveTargetType.position:
                self.commands.append({"$type": "move_avatar_towards_position",
                                      "position": self._move_target,
                                      "avatar_id": self.avatar_id})
            elif self._move_target_type == _MoveTargetType.object:
                self.commands.append({"$type": "move_avatar_towards_object",
                                      "object_id": self._move_target,
                                      "offset_distance": self._move_distance_offset,
                                      "min_y": self._move_min_y,
                                      "use_centroid": True,
                                      "avatar_id": self.avatar_id})
            else:
                raise Exception(f"Invalid move target type: {self._move_target_type}")
        # Apply Euler angles to the current rotation.
        if self._has_eulers:
            self._has_eulers = False
            image_sensors, rotation, forward = self._get_image_sensor(resp=resp)
            if image_sensors:
                eulers = QuaternionUtils.quaternion_to_euler_angles(rotation)
                eulers[0] += self._eulers["x"]
                eulers[1] += self._eulers["y"]
                eulers[2] += self._eulers["z"]
            else:
                eulers = np.array([self._eulers["x"], self._eulers["y"], self._eulers["z"]])
            self._rotate_target = TDWUtils.array_to_vector4(
                QuaternionUtils.euler_angles_to_quaternion(np.deg2rad(eulers)))
        # Rotate towards a target.
        if self._rotate_target is not None:
            if self._rotate_target_type == _RotateTargetType.rotation:
                self.commands.append({"$type": "rotate_sensor_container_towards_rotation",
                                      "avatar_id": self.avatar_id,
                                      "rotation": self._rotate_target,
                                      "speed": self.rotate_speed})
            elif self._rotate_target_type == _RotateTargetType.object:
                self.commands.extend([{"$type": "rotate_sensor_container_towards_object",
                                       "avatar_id": self.avatar_id,
                                       "speed": self.rotate_speed,
                                       "object_id": self._rotate_target,
                                       "use_centroid": True},
                                      {"$type": "focus_towards_object",
                                       "avatar_id": self.avatar_id,
                                       "speed": self.focus_speed,
                                       "object_id": self._rotate_target,
                                       "use_centroid": True}])
            else:
                raise Exception(f"Invalid rotate target type: {self._move_target_type}")

    def move_to_position(self, target: Dict[str, float], relative: bool = False) -> None:
        """
        Start moving towards a target position.

        :param relative: If True, the target is relative to the current position of the avatar. If False, the target is in absolute worldspace coordinates.
        :param target: The target position.
        """

        if relative:
            self._has_relative_translation = True
            self._relative_translation = target
        else:
            self._move_target = target
        self._move_target_type = _MoveTargetType.position

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

    def stop_moving(self) -> None:
        """
        Stop moving towards the current target.
        """

        self._move_target = None

    def rotate_to_object(self, target: int) -> None:
        """
        Start to rotate towards an object (to look at the object).

        :param target: The ID of the target object.
        """

        self._rotate_target = target
        self._rotate_target_type = _RotateTargetType.object

    def rotate_by_rpy(self, target: Dict[str, float]) -> None:
        """
        Start rotating the camera by the `[roll, pitch, yaw]` angles expressed as an `[x, y, z]` dictionary.

        :param target: The target `[roll, pitch, yaw]` angles from when this function was first called, in degrees.
        """

        # Remember the Eulers. They will be applied to the rotation later.
        self._eulers = target
        self._has_eulers = True
        self._rotate_target_type = _RotateTargetType.rotation
        self._rotate_target = None

    def rotate_to_rotation(self, target: Dict[str, float]) -> None:
        """
        Start rotating to a rotation, expressed as a quaternion dictionary.

        :param target: The target rotation.
        """

        self._rotate_target = target
        self._rotate_target_type = _RotateTargetType.rotation

    def stop_rotating(self) -> None:
        """
        Stop rotating towards the current target.
        """

        self._rotate_target = None

    def motions_are_done(self, resp: List[bytes]) -> Dict[str, bool]:
        """
        :param resp: The most recent response from the build.

        :return: A dictionary of which motions are complete. For example: `{"move": True, "rotate": False, "focus": False}`
        """

        move: bool = self._move_target is None
        rotate: bool = self._rotate_target is None
        focus: bool = self._rotate_target is None or self._rotate_target_type is not _RotateTargetType.object
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "camm":
                cam = CameraMotionComplete(resp[i])
                if cam.get_avatar_id() == self.avatar_id:
                    m = cam.get_motion()
                    if m == "move":
                        move = True
                        self._move_target = None
                    elif m == "rotate":
                        rotate = True
                        self._rotate_target = None
                    elif m == "focus":
                        focus = True
                    else:
                        raise Exception(f"Motion state not defined: {m}")
        return {"move": move, "rotate": rotate, "focus": focus}

    @staticmethod
    def _get_object_center(resp: List[bytes], target: int) -> np.array:
        """
        :param resp: The most recent response from the build.
        :param target: The ID of the target object.

        :return: The centroid of the target object.
        """

        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "boun":
                b = Bounds(resp[i])
                for j in range(b.get_num()):
                    if b.get_id(j) == target:
                        return TDWUtils.get_bounds_dict(b, j)["center"]
        raise Exception("Bounds output data for target object not found in the response from the build.")

    def _get_avatar_position(self, resp: List[bytes]) -> np.array:
        """
        :param resp: The most recent response from the build.

        :return: Output data for this avatar.
        """

        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "avki":
                a = AvatarKinematic(resp[i])
                # Make sure this is the correct avatar.
                if a.get_avatar_id() == self.avatar_id:
                    return np.array(a.get_position())
        raise Exception("Avatar output data not found in the response from the build.")

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
