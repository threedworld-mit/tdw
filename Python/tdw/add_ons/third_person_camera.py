from secrets import token_urlsafe
from typing import List, Dict, Union, Optional
from tdw.add_ons.add_on import AddOn


class ThirdPersonCamera(AddOn):
    """
    Add a third-person camera to the scene. This includes initialization parameters (position, rotation, etc.) and some basic movement parameters (whether to follow or look at a target),.

    ```python
    from tdw.controller import Controller
    from tdw.tdw_utils import TDWUtils
    from tdw.add_ons.third_person_camera import ThirdPersonCamera

    c = Controller(launch_build=False)
    c.start()
    cam = ThirdPersonCamera(avatar_id="c",
                            position={"x": 1, "y": 2.2, "z": -0.5},
                            rotation={"x": 0, "y": -45, "z": 0})
    c.add_ons.append(cam)
    c.communicate(TDWUtils.create_empty_room(12, 12))
    ```

    By itself, a `ThirdPersonCamera` won't capture images (though it will render them on the screen). For image capture, include an `ImageCapture` add-on:

    ```python
    from tdw.controller import Controller
    from tdw.tdw_utils import TDWUtils
    from tdw.add_ons.third_person_camera import ThirdPersonCamera
    from tdw.add_ons.image_capture import ImageCapture

    c = Controller(launch_build=False)
    c.start()
    cam = ThirdPersonCamera(avatar_id="c",
                            position={"x": 1, "y": 2.2, "z": -0.5},
                            rotation={"x": 0, "y": -45, "z": 0})
    cap = ImageCapture(path="images", avatar_ids=["c"])
    c.add_ons.append(cam)
    c.add_ons.append(cap)
    c.communicate(TDWUtils.create_empty_room(12, 12))
    ```

    ## Third-person cameras and avatars

    The `ThirdPersonCamera` is a wrapper class for a standard `A_Img_Caps_Kinematic` TDW avatar. All non-physics avatar commands may be sent for this camera.

    In this document, the words "camera" and "avatar" may be used interchangeably.
    """

    # The render order. Third person cameras will always render "on top" of any other cameras.
    _RENDER_ORDER: int = 100

    def __init__(self, avatar_id: str = None, position: Dict[str, float] = None,
                 rotation: Dict[str, float] = None, look_at: Union[int, Dict[str, float]] = None,
                 fov: int = None, follow_object: int = None, follow_rotate: bool = False, pass_masks: List[str] = None,
                 framerate: int = None):
        """
        :param avatar_id: The ID of the avatar (camera). If None, a random ID is generated.
        :param position: The initial position of the camera. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param rotation: The initial rotation of the camera. Can be Euler angles (keys are `(x, y, z)`) or a quaternion (keys are `(x, y, z, w)`). If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param look_at: If not None, rotate look at this target every frame. Overrides `rotation`. Can be an int (an object ID) or an `(x, y, z)` dictionary (a position).
        :param fov: If not None, this is the initial field of view. Otherwise, defaults to 35.
        :param follow_object: If not None, follow an object per frame. Use `position` as a relative value from the target object rather than worldspace coordinates.
        :param follow_rotate: If True, match the rotation of the object. Ignored if `follow_object` is None.
        :param pass_masks: The pass masks. If None, defaults to `["_img"]`.
        :param framerate: If not None, sets the target framerate.
        """

        super().__init__()
        # Set a random avatar ID.
        if avatar_id is None:
            """:field
            The ID of the avatar that (this camera).
            """
            self.avatar_id: str = token_urlsafe(4)
        else:
            self.avatar_id: str = avatar_id
        if pass_masks is None:
            pass_masks = ["_img"]
        self._init_commands: List[dict] = [{"$type": "create_avatar",
                                            "type": "A_Img_Caps_Kinematic",
                                            "id": self.avatar_id},
                                           {"$type": "set_pass_masks",
                                            "pass_masks": pass_masks,
                                            "avatar_id": self.avatar_id}]
        self.position: Optional[Dict[str, float]] = position
        if self.position is not None and follow_object is None:
            self._init_commands.append({"$type": "teleport_avatar_to",
                                        "position": self.position,
                                        "avatar_id": self.avatar_id})
        if rotation is not None:
            if isinstance(rotation, dict):
                if "w" in rotation:
                    self._init_commands.append({"$type": "rotate_sensor_container_to",
                                                "rotation": rotation,
                                                "avatar_id": self.avatar_id})
                else:
                    for q, axis in zip(["x", "y", "z"], ["pitch", "yaw", "roll"]):
                        self._init_commands.append({"$type": "rotate_sensor_container_by",
                                                    "axis": axis,
                                                    "angle": rotation[q],
                                                    "avatar_id": self.avatar_id})
        # Maybe look at a target (overrides rotation).
        self.look_at_target: Optional[Union[int, Dict[str, float]]] = look_at
        self._init_commands.extend(self._get_look_at_commands())
        if fov is not None:
            self._init_commands.append({"$type": "set_field_of_view",
                                        "field_of_view": fov,
                                        "avatar_id": self.avatar_id})
        """:field
        The ID of the follow target, if any.
        """
        self.follow_object: Optional[int] = follow_object
        """:field
        If `self.follow is not None`, this determines whether the camera will follow the object's rotation.
        """
        self.follow_rotate: bool = follow_rotate

        if framerate is not None:
            self._init_commands.append({"$type": "set_target_framerate",
                                        "framerate": framerate})

        self._init_commands.append({"$type": "set_render_order",
                                    "render_order": ThirdPersonCamera._RENDER_ORDER,
                                    "avatar_id": self.avatar_id})
        ThirdPersonCamera._RENDER_ORDER += 1

    def get_initialization_commands(self) -> List[dict]:
        return self._init_commands

    def on_communicate(self, resp: List[bytes], commands: List[dict]) -> None:
        if self.look_at_target is not None:
            self.commands.extend(self._get_look_at_commands())
        if self.follow_object is not None and self.position is not None:
            self.commands.append({"$type": "follow_object",
                                  "object_id": self.follow_object,
                                  "position": self.position,
                                  "rotation": self.follow_rotate,
                                  "avatar_id": self.avatar_id})

    def _get_look_at_commands(self) -> List[dict]:
        """
        :return: A command for looking at a target.
        """

        commands = []
        if self.look_at_target is None:
            return commands
        # Look at and focus on the object.
        elif isinstance(self.look_at_target, int):
            commands.extend([{"$type": "look_at",
                              "object_id": self.look_at_target,
                              "use_centroid": True,
                              "avatar_id": self.avatar_id},
                             {"$type": "focus_on_object",
                              "object_id": self.look_at_target,
                              "use_centroid": True,
                              "avatar_id": self.avatar_id}])
        elif isinstance(self.look_at_target, dict):
            commands.append({"$type": "look_at_position",
                             "position": self.look_at_target,
                             "avatar_id": self.avatar_id})
        else:
            raise TypeError(f"Invalid look-at target: {self.look_at_target}")
