from secrets import token_urlsafe
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from overrides import final
from tdw.add_ons.add_on import AddOn


class ThirdPersonCameraBase(AddOn, ABC):
    """
    An abstract base class for third-person camera controller add-ons.
    """

    # The render order. Third person cameras will always render "on top" of any other cameras.
    __RENDER_ORDER: int = 100

    def __init__(self, avatar_id: str = None, position: Dict[str, float] = None, rotation: Dict[str, float] = None,
                 fov: int = None, pass_masks: List[str] = None, framerate: int = None):
        """
        :param avatar_id: The ID of the avatar (camera). If None, a random ID is generated.
        :param position: The initial position of the object.If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param rotation: The initial rotation of the camera. Can be Euler angles (keys are `(x, y, z)`) or a quaternion (keys are `(x, y, z, w)`). If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param fov: If not None, this is the initial field of view. Otherwise, defaults to 35.
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
                                            "avatar_id": self.avatar_id},
                                           {"$type": "set_render_order",
                                            "render_order": ThirdPersonCameraBase.__RENDER_ORDER,
                                            "avatar_id": self.avatar_id},
                                           {"$type": "set_anti_aliasing",
                                            "mode": "subpixel",
                                            "avatar_id": self.avatar_id}]
        ThirdPersonCameraBase.__RENDER_ORDER += 1
        """:field
        The initial position of the object. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        """
        self.position: Optional[Dict[str, float]] = position
        # Set the initial position.
        if self.position is not None:
            self._init_commands.append({"$type": "teleport_avatar_to",
                                        "position": self.position,
                                        "avatar_id": self.avatar_id})
        # Set the initial rotation.
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
        # Set the field of view.
        if fov is not None:
            self._init_commands.append({"$type": "set_field_of_view",
                                        "field_of_view": fov,
                                        "avatar_id": self.avatar_id})
        # Set the simulation framerate.
        if framerate is not None:
            self._init_commands.append({"$type": "set_target_framerate",
                                        "framerate": framerate})

    @abstractmethod
    def on_send(self, resp: List[bytes]) -> None:
        """
        This is called after commands are sent to the build and a response is received.

        :param resp: The response from the build.
        """

        raise Exception()

    @final
    def get_initialization_commands(self) -> List[dict]:
        """
        :return: A list of commands that will initialize this module.
        """

        return self._init_commands

    @final
    def previous_commands(self, commands: List[dict]) -> None:
        """
        Do something with the commands that were just sent to the build. By default, this function doesn't do anything.

        :param commands: The commands that were just sent to the build.
        """

        pass
