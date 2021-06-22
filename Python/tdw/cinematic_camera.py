from enum import Enum
from typing import List, Dict, Optional, Union, Tuple
import numpy as np
from tdw.tdw_utils import TDWUtils, QuaternionUtils
from tdw.output_data import OutputData, Transforms, Bounds, AvatarKinematic, ImageSensors, CameraMotionComplete, Images


class _MoveTarget(Enum):
    """
    A type of target that the camera can move towards.
    """

    position = 1
    object_position = 2
    object_centroid = 4


class _RotateTarget(Enum):
    """
    A type of target that the camera can rotate towards.
    """

    position = 1
    object_position = 2
    object_centroid = 4
    rotation = 8


class _FocusTarget(Enum):
    """
    A type of target for the camera focus.
    """

    distance = 1
    object_position = 2
    object_centroid = 4


class CinematicCamera:
    """
    Wrapper class for third-person camera controls in TDW. These controls are "cinematic" in the sense that the camera will move, rotate, etc. *towards* a target at a set speed per frame. The `CinematicCamera` class is suitable for demo videos of TDW, but *not* for most actual experiments. The actual camera object at runtime is an `"A_Img_Caps_Kinematic"` avatar.

    This is not a controller. Per-frame, this object can read the latest response from the build and output commands. To add a camera to the scene you must first create a `Camera` object and then send its `init_commands`:

    ```python
    from tdw.controller import Controller
    from tdw.tdw_utils import TDWUtils
    from tdw.cinematic_camera import CinematicCamera

    c = Controller(launch_build=False)
    c.start()
    cam = CinematicCamera(position={"x": 0, "y": 1.5, "z": 0},
                          rotation={"x": 2, "y": 45, "z": 0},
                          move_speed=0.1,
                          rotate_speed=3,
                          focus_speed=0.3)
    commands = [TDWUtils.create_empty_room(12, 12)]

    # Initialize the camera.
    commands.extend(cam.init_commands)

    # Send the commands.
    resp = c.communicate(cam.init_commands)
    ```

    Most of the constructor parameters have defaults values. Below is a more succinct example:

    ```python
    from tdw.controller import Controller
    from tdw.tdw_utils import TDWUtils
    from tdw.cinematic_camera import CinematicCamera

    c = Controller(launch_build=False)
    c.start()
    cam = CinematicCamera(position={"x": 0, "y": 1.5, "z": 0})
    commands = [TDWUtils.create_empty_room(12, 12)]
    # Initialize the camera.
    commands.extend(cam.init_commands)
    # Send the commands.
    resp = c.communicate(cam.init_commands)
    ```

    Each function in this class will *start* to move the camera but won't actually send commands (because this is not a controller):

    ```python
    from tdw.controller import Controller
    from tdw.tdw_utils import TDWUtils
    from tdw.cinematic_camera import CinematicCamera

    c = Controller(launch_build=False)
    c.start()
    cam = CinematicCamera(position={"x": 0, "y": 1.5, "z": 0})
    commands = [TDWUtils.create_empty_room(12, 12)]
    # Initialize the camera.
    commands.extend(cam.init_commands)
    # Send the commands.
    resp = c.communicate(cam.init_commands)

    # Set a movement target for the camera.
    cam.move_to_position(target={"x": 1, "y": 2, "z": -0.5})
    ```

    To actually apply changes to the camera, you will need to append the commands returned by `cam.get_commands(resp)`:

    ```python
    from tdw.controller import Controller
    from tdw.tdw_utils import TDWUtils
    from tdw.cinematic_camera import CinematicCamera

    c = Controller(launch_build=False)
    c.start()
    cam = CinematicCamera(position={"x": 0, "y": 1.5, "z": 0})
    commands = [TDWUtils.create_empty_room(12, 12)]
    # Initialize the camera.
    commands.extend(cam.init_commands)
    # Send the commands.
    resp = c.communicate(cam.init_commands)

    # Set a movement target for the camera.
    cam.move_to_position(target={"x": 1, "y": 2, "z": -0.5})

    for i in range(100):
        commands = cam.get_commands(resp=resp)
        resp = c.communicate(commands)
    ```

    Note that all objects that you want the camera to move to must be in the scene *before* adding the camera:

    ```python
    from tdw.controller import Controller
    from tdw.tdw_utils import TDWUtils
    from tdw.cinematic_camera import CinematicCamera

    object_id = 0
    c = Controller(launch_build=False)
    c.start()
    cam = CinematicCamera(position={"x": 0, "y": 1.5, "z": 0})
    # Add an object before adding the camera.
    commands = [TDWUtils.create_empty_room(12, 12),
                c.get_add_object(model_name="iron_box", object_id=object_id)]
    # Initialize the camera.
    commands.extend(cam.init_commands)
    # Send the commands.
    resp = c.communicate(cam.init_commands)

    # Set a movement target for the camera.
    cam.move_to_position(target={"x": 1, "y": 2, "z": -0.5})

    for i in range(100):
        commands = cam.get_commands(resp=resp)
        resp = c.communicate(commands)
    ```

    ## Possible motions

    - **Move** towards a target object or position
    - **Rotate** towards a target quaternion, Euler angles; or rotate to look at a target position or object
    - **Focus** towards a target distance or object

    ## Stopping motions

    There are many ways to stop a camera motion:

    - Stop sending `cam.get_commands(resp)` to the build
    - Call `cam.stop_moving()`, `cam.stop_rotating()`, or `cam.stop_focusing()`
    - Call `cam.motions_are_done(resp)`, which will return a dictionary indicating whether the each type of motion is done:

    ```python
    from tdw.controller import Controller
    from tdw.tdw_utils import TDWUtils
    from tdw.cinematic_camera import CinematicCamera

    c = Controller(launch_build=False)

    # Create an empty room and a camera.
    c.start()
    cam = CinematicCamera(position={"x": 0.1, "y": 1.6, "z": -4.2})
    commands = [TDWUtils.create_empty_room(12, 12)]
    commands.extend(cam.init_commands)
    resp = c.communicate(commands)

    # Rotate and move the camera.
    cam.move_to_position(target={"x": 2, "y": 4, "z": 0})
    cam.rotate_by_rpy(target={"x": 0, "y": -45, "z": 0})

    # Loop until both motions are done.
    move = False
    rotate = False
    while not move or not rotate:
        motions = cam.motions_are_done(resp=resp)
        if motions["move"]:
            move = True
        if motions["rotate"]:
            rotate = True
        resp = c.communicate(cam.get_commands(resp=resp))
    print("DONE!")
    ```

    ## Output Data

    This object requires certain output data, which it will automatically request via `cam.init_commands`. If you're not already requesting this data per frame, you might notice that the simulation runs slightly slower.

    The output data will be:

    - `Transforms` (for all objects in the scene)
    - `Bounds` (for all objects in the scene)
    - Avatar data (for all avatars in the scene; for this avatar, it's `AvatarKinematic`)
    - `ImageSensors` (for all avatars in the scene)
    - `Images` (for all avatars in the scene, but only if `images=True` in the constructor of this object)
    - `CameraMotionComplete` (for all avatars in the scene)

    ## Saving Images

    To save images, set `images=True` in the constructor and then call `cam.save_images()`:

    ```python
    from tdw.controller import Controller
    from tdw.tdw_utils import TDWUtils
    from tdw.cinematic_camera import CinematicCamera

    output_directory = "images"

    c = Controller(launch_build=False)
    c.start()
    cam = CinematicCamera(position={"x": 0, "y": 1.5, "z": 0}, images=True)
    # Add an object before adding the camera.
    commands = [TDWUtils.create_empty_room(12, 12)]
    # Initialize the camera.
    commands.extend(cam.init_commands)
    # Send the commands.
    resp = c.communicate(cam.init_commands)

    # Set a movement target for the camera.
    cam.move_to_position(target={"x": 1, "y": 2, "z": -0.5})

    for i in range(100):
        commands = cam.get_commands(resp=resp)
        resp = c.communicate(commands)
        cam.save_images(resp=resp)
    ```

    """

    """:class_var
    The next third-person camera's rendering order.
    """
    RENDER_ORDER: int = 100

    def __init__(self, position: Dict[str, float], avatar_id: str = "c", rotation: Union[int, Dict[str, float]] = None,
                 move_speed: float = 0.1, rotate_speed: float = 3, focus_speed: float = 0.3,
                 images: bool = False, pass_masks: List[str] = None):
        """
        :param position: The initial position of the camera.
        :param avatar_id: The ID of the avatar (camera).
        :param rotation: The initial rotation of the camera. If an `int`, the camera will look at the object with the matching ID. If a dict: The camera will rotate to the quaternion if the keys are `[x, y, z, w]` or to the Euler angles if the keys are `[x, y, z]`.
        :param move_speed: The directional speed of the camera. This can later be adjusted by setting `self.move_speed`.
        :param rotate_speed: The angular speed of the camera. This can later be adjusted by setting `self.rotate_speed`.
        :param focus_speed: The speed of the focus of the camera. This can later be adjusted by setting `self.focus_speed`.
        :param images: If True, all cameras (not just this one!) will return images per frame.
        :param pass_masks: The pass masks for this camera. If None, defaults to `["_img"]`.
        """

        self.avatar_id: str = avatar_id
        self.move_speed: float = move_speed
        self.rotate_speed: float = rotate_speed
        self.focus_speed: float = focus_speed
        # Send these commands to initialize the camera.
        self.init_commands: List[dict] = [{"$type": "create_avatar",
                                           "type": "A_Img_Caps_Kinematic",
                                           "id": self.avatar_id},
                                          {"$type": "teleport_avatar_to",
                                           "position": position,
                                           "avatar_id": self.avatar_id},
                                          {"$type": "set_anti_aliasing",
                                           "mode": "subpixel",
                                           "avatar_id": self.avatar_id},
                                          {"$type": "set_render_order",
                                           "render_order": CinematicCamera.RENDER_ORDER,
                                           "avatar_id": self.avatar_id},
                                          {"$type": "send_transforms",
                                           "frequency": "always"},
                                          {"$type": "send_avatars",
                                           "frequency": "always"},
                                          {"$type": "send_bounds",
                                           "frequency": "always"},
                                          {"$type": "send_image_sensors",
                                           "frequency": "always"}]
        if rotation is not None:
            if isinstance(rotation, int):
                self.init_commands.append({"$type": "look_at",
                                           "object_id": rotation,
                                           "use_centroid": True,
                                           "avatar_id": self.avatar_id})
            elif isinstance(rotation, dict):
                # Rotate to a quaternion.
                if "w" in rotation:
                    self.init_commands.append({"$type": "rotate_sensor_container_to",
                                               "rotation": rotation,
                                               "avatar_id": self.avatar_id})
                # Rotate to Euler angles.
                else:
                    for a, axis in zip(["x", "y", "z"], ["roll", "pitch", "yaw"]):
                        self.init_commands.append({"$type": "rotate_sensor_container_by",
                                                   "axis": axis,
                                                   "angle": rotation[a],
                                                   "avatar_id": self.avatar_id})
        self.images: bool = images
        if images:
            self.init_commands.append({"$type": "send_images",
                                       "frequency": "always"})
        if pass_masks is None:
            pass_masks = ["_img"]
        self.init_commands.append({"$type": "set_pass_masks",
                                   "pass_masks": pass_masks,
                                   "avatar_id": self.avatar_id})
        CinematicCamera.RENDER_ORDER += 1

        self._move_target: Optional[Union[int, Dict[str, float]]] = None
        self._move_distance_offset: float = 0
        self._move_min_y: float = 0.25
        self._move_target_type: _MoveTarget = _MoveTarget.position
        # Update these fields to apply them to the current position.
        self._relative_translation: Dict[str, float] = {"x": 0, "y": 0, "z": 0}
        self._has_relative_translation: bool = False

        self._rotate_target: Optional[Union[int, Dict[str, float]]] = None
        self._rotate_target_type: _RotateTarget = _RotateTarget.position
        # Use these fields to remember the Euler angles and
        # apply them later to self._rotate_target once we have the current camera rotation.
        self._eulers: Dict[str, float] = {"x": 0, "y": 0, "z": 0}
        self._has_eulers: bool = False

        self._focus_target: Optional[Union[float, int]] = None
        self._focus_target_type: _FocusTarget = _FocusTarget.distance

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
        self._move_target_type = _MoveTarget.position

    def move_to_object(self, target: int, offset_distance: float = 1, min_y: float = 0.25,
                       centroid: bool = True) -> None:
        """
        Start moving towards a target object.

        :param target: The ID of the target object.
        :param offset_distance: Stop moving when the camera is this far away from the object.
        :param min_y: Clamp the y positional coordinate of the camera to this minimum value.
        :param centroid: If True, move towards the centroid of the object (the object's center in `Bounds` output data). If False, move towards the bottom-center of the object (the object's position in `Transforms` output data).
        """

        self._move_target = target
        self._move_distance_offset = offset_distance
        self._move_min_y = min_y
        self._move_target_type = _MoveTarget.object_centroid if centroid else _MoveTarget.object_position

    def stop_moving(self) -> None:
        self._move_target = None

    def rotate_to_object(self, target: int, centroid: bool = True) -> None:
        self._rotate_target = target
        self._rotate_target_type = _RotateTarget.object_centroid if centroid else _RotateTarget.object_position

    def rotate_by_rpy(self, target: Dict[str, float]) -> None:
        """
        Start rotating the camera by the `[roll, pitch, yaw]` angles expressed as an `[x, y, z]` dictionary.

        :param target: The target `[roll, pitch, yaw]` angles from when this function was first called, in degrees.
        """

        # Remember the Eulers. They will be applied to the rotation later.
        self._eulers = target
        self._has_eulers = True
        self._rotate_target_type = _RotateTarget.rotation
        self._rotate_target = None

    def rotate_to_rotation(self, target: Dict[str, float]) -> None:
        """
        Start rotating to a rotation, expressed as a quaternion dictionary.

        :param target: The target rotation.
        """

        self._rotate_target = target
        self._rotate_target_type = _RotateTarget.rotation

    def stop_rotating(self) -> None:
        """
        Stop rotating to a target.
        """

        self._rotate_target = None

    def focus_on_distance(self, target: float) -> None:
        """
        Start focusing towards a target distance.

        :param target: The target distance.
        """

        self._focus_target = target
        self._focus_target_type = _FocusTarget.distance

    def focus_on_object(self, target: int, centroid: bool) -> None:
        """
        Start focusing on a target object.

        :param target: The ID of the target object.
        :param centroid: If True, focus towards the centroid of the object (the object's center in `Bounds` output data). If False, focus towards the bottom-center of the object (the object's position in `Transforms` output data).
        """

        self._focus_target = target
        self._focus_target_type = _FocusTarget.object_centroid if centroid else _FocusTarget.object_position

    def stop_focusing(self) -> None:
        """
        Stop focusing on a target.
        """

        self._focus_target = None

    def get_commands(self, resp: List[bytes]) -> List[dict]:
        """
        :param resp: The most recent response from the build.

        :return: A list of commands to send to the build.
        """

        commands: List[dict] = list()

        # Set a relative target.
        if self._has_relative_translation:
            origin = self._get_avatar_position(resp=resp)
            self._move_target = origin + TDWUtils.vector3_to_array(self._relative_translation)
            self._has_relative_translation = False
        if self._move_target is not None:
            if self._move_target_type == _MoveTarget.position:
                commands.append({"$type": "move_avatar_towards_position",
                                 "position": self._move_target,
                                 "avatar_id": self.avatar_id})
            elif self._move_target_type == _MoveTarget.object_position:
                commands.append({"$type": "move_avatar_towards_object",
                                 "object_id": self._move_target,
                                 "offset_distance": self._move_distance_offset,
                                 "min_y": self._move_min_y,
                                 "use_centroid": False,
                                 "avatar_id": self.avatar_id})
            elif self._move_target_type == _MoveTarget.object_centroid:
                commands.append({"$type": "move_avatar_towards_object",
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
            if self._rotate_target_type == _RotateTarget.rotation:
                commands.append({"$type": "rotate_sensor_container_towards_rotation",
                                 "avatar_id": self.avatar_id,
                                 "rotation": self._rotate_target,
                                 "speed": self.rotate_speed})
            elif self._rotate_target_type == _RotateTarget.object_position:
                commands.append({"$type": "rotate_sensor_container_towards_object",
                                 "avatar_id": self.avatar_id,
                                 "speed": self.rotate_speed,
                                 "object_id": self._rotate_target,
                                 "use_centroid": False})
            elif self._rotate_target_type == _RotateTarget.object_centroid:
                commands.append({"$type": "rotate_sensor_container_towards_object",
                                 "avatar_id": self.avatar_id,
                                 "speed": self.rotate_speed,
                                 "object_id": self._rotate_target,
                                 "use_centroid": True})
            else:
                raise Exception(f"Invalid rotate target type: {self._move_target_type}")
        # Focus towards a target distance.
        if self._focus_target is not None:
            if self._focus_target_type == _FocusTarget.distance:
                d = self._focus_target
            elif self._focus_target_type == _FocusTarget.object_position:
                d = np.linalg.norm(self._get_avatar_position(resp=resp) -
                                   self._get_object_position(resp=resp, target=self._focus_target))
            elif self._focus_target_type == _FocusTarget.object_centroid:
                d = np.linalg.norm(self._get_avatar_position(resp=resp) -
                                   self._get_object_center(resp=resp, target=self._focus_target))
            else:
                raise Exception(f"Invalid focus target type: {self._move_target_type}")
            commands.append({"$type": "focus_towards",
                             "avatar_id": self.avatar_id,
                             "distance": float(d),
                             "speed": self.focus_speed})
        return commands

    def motions_are_done(self, resp: List[bytes]) -> Dict[str, bool]:
        """
        :param resp: The most recent response from the build.

        :return: A dictionary of which motions, if any, are complete. For example: `{"move": True, "rotate": False, "focus": False}`
        """

        move: bool = False
        rotate: bool = False
        focus: bool = False
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "camm":
                cam = CameraMotionComplete(resp[i])
                if cam.get_avatar_id() == self.avatar_id:
                    m = cam.get_motion()
                    if m == "move":
                        move = True
                    elif m == "rotate":
                        rotate = True
                    elif m == "focus":
                        focus = True
                    else:
                        raise Exception(f"Motion state not defined: {m}")
        return {"move": move, "rotate": rotate, "focus": focus}

    def save_images(self, resp: List[bytes], output_directory: str) -> None:
        """
        Save images that were generated by this camera.

        :param resp: The most recent response from the build.
        :param output_directory: The output directory for the image files.
        """
        
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "imag":
                images = Images(resp[i])
                TDWUtils.save_images(images=images,
                                     filename=f"{self.avatar_id}_{int.from_bytes(resp[-1], byteorder='big')}",
                                     output_directory=output_directory)

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

    @staticmethod
    def _get_object_position(resp: List[bytes], target: int) -> np.array:
        """
        :param resp: The most recent response from the build.
        :param target: The ID of the target object.

        :return: The position of the target object.
        """

        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "tran":
                tr = Transforms(resp[i])
                for j in range(tr.get_num()):
                    if tr.get_id(j) == target:
                        return np.array(tr.get_position(j))

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
