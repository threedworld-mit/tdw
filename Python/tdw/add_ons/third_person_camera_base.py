from secrets import token_urlsafe
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from overrides import final
from tdw.add_ons.add_on import AddOn


class ThirdPersonCameraBase(AddOn, ABC):
    """
    An abstract base class for third-person camera controller add-ons.
    """

    """:class_var
    The render order. Third person cameras will always render "on top" of any other cameras.
    """
    RENDER_ORDER: int = 100

    def __init__(self, avatar_id: str = None, position: Dict[str, float] = None, rotation: Dict[str, float] = None,
                 field_of_view: int = None):
        """
        :param avatar_id: The ID of the avatar (camera). If None, a random ID is generated.
        :param position: The initial position of the camera. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param rotation: The initial rotation of the camera. Can be Euler angles (keys are `(x, y, z)`) or a quaternion (keys are `(x, y, z, w)`). If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        :param field_of_view: If not None, set the field of view.
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
        self._render_order = ThirdPersonCameraBase.RENDER_ORDER
        ThirdPersonCameraBase.RENDER_ORDER += 1
        """:field
        The position of the camera. If None, defaults to `{"x": 0, "y": 0, "z": 0}`.
        """
        self.position: Optional[Dict[str, float]] = position
        # The initial rotation.
        self._rotation: Optional[Dict[str, float]] = rotation
        # The field of view.
        self._field_of_view: float = field_of_view

    @abstractmethod
    def on_send(self, resp: List[bytes]) -> None:
        """
        This is called after commands are sent to the build and a response is received.

        Use this function to send commands to the build on the next frame, given the `resp` response.
        Any commands in the `self.commands` list will be sent on the next frame.

        :param resp: The response from the build.
        """

        raise Exception()

    def get_initialization_commands(self) -> List[dict]:
        """
        This function gets called exactly once per add-on. To re-initialize, set `self.initialized = False`.

        :return: A list of commands that will initialize this add-on.
        """

        commands = [{"$type": "create_avatar",
                     "type": self._get_avatar_type(),
                     "id": self.avatar_id},
                    {"$type": "set_pass_masks",
                     "pass_masks": ["_img"],
                     "avatar_id": self.avatar_id},
                    {"$type": "set_render_order",
                     "render_order": self._render_order,
                     "avatar_id": self.avatar_id}]
        # Set the initial position.
        if self.position is not None:
            commands.append({"$type": "teleport_avatar_to",
                             "position": self.position,
                             "avatar_id": self.avatar_id})
        # Set the initial rotation.
        if self._rotation is not None:
            if isinstance(self._rotation, dict):
                if "w" in self._rotation:
                    commands.append({"$type": "rotate_sensor_container_to",
                                     "rotation": self._rotation,
                                     "avatar_id": self.avatar_id})
                else:
                    for q, axis in zip(["x", "y", "z"], ["pitch", "yaw", "roll"]):
                        commands.append({"$type": "rotate_sensor_container_by",
                                         "axis": axis,
                                         "angle": self._rotation[q],
                                         "avatar_id": self.avatar_id})
        # Set the field of view.
        if self._field_of_view is not None:
            commands.append({"$type": "set_field_of_view",
                             "field_of_view": self._field_of_view,
                             "avatar_id": self.avatar_id})
        return commands

    @final
    def before_send(self, commands: List[dict]) -> None:
        """
        This is called before sending commands to the build. By default, this function doesn't do anything.

        :param commands: The commands that are about to be sent to the build.
        """

        pass

    def _get_avatar_type(self) -> str:
        """
        :return: The type of avatar.
        """

        return "A_Img_Caps_Kinematic"
